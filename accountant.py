import os
import json
from datetime import datetime
import utils

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

INCOME_FILE = os.path.join(DATA_DIR, "income.txt")
APPOINTMENT_FILE = os.path.join(DATA_DIR, "appointment.txt")
MEDICINE_FILE = os.path.join(DATA_DIR, "medicine.txt")
BILL_RECEIPT_FILE = os.path.join(DATA_DIR, "bill_receipt.txt")

os.makedirs(DATA_DIR, exist_ok=True)


def write_bill_receipt(bill, appointment):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bill_status = bill.get("status", "unpaid").capitalize()
    medicine_ids = appointment.get("medicine", "")

    medicine_details = "\n--- Prescribed Medicines ---\n"

    if medicine_ids:
        try:
            with open(MEDICINE_FILE, "r") as f:
                medicines = json.load(f)

            for med_id in [m.strip() for m in medicine_ids.split(",")]:
                med = next((m for m in medicines if m.get("medID") == med_id), None)
                if med:
                    medicine_details += (
                        f"  {med.get('name', 'Unknown')} "
                        f"(ID: {med_id}) : RM {float(med.get('price', 0)):.2f}\n"
                    )
        except Exception:
            medicine_details += "  (Error loading medicine details)\n"
    else:
        medicine_details += "  No medicines prescribed\n"

    receipt = (
        "\n" + "=" * 60 + "\n"
        "=== BILL RECEIPT ===\n"
        f"Bill ID        : {bill.get('billID')}\n"
        f"Patient ID     : {bill.get('patient')}\n"
        f"Appointment ID : {bill.get('appointmentID')}\n"
        f"Doctor ID      : {appointment.get('doctorID')}\n"
        f"Date           : {appointment.get('date')}\n"
        "\n--- Bill Breakdown ---\n"
        f"Consultation Fee : RM {bill.get('consultationFee', 0):.2f}\n"
        + medicine_details +
        f"\nMedicine Fee (Total) : RM {bill.get('medicineFee', 0):.2f}\n"
        f"Total Amount         : RM {bill.get('amount', 0):.2f}\n"
        f"\nStatus : {bill_status}\n"
        f"Recorded On : {timestamp}\n"
        + "=" * 60 + "\n"
    )

    with open(BILL_RECEIPT_FILE, "a", encoding="utf-8") as f:
        f.write(receipt)


def calculate_patient_bill():
    print("\n=== Calculate Patient Bill ===")

    apt_id = input("Enter Appointment ID (e.g., A1): ").strip()
    if not apt_id:
        print("Appointment ID cannot be empty.")
        return

    appointments = utils.read_records(APPOINTMENT_FILE)
    appointment = next((a for a in appointments if a.get("aptID") == apt_id), None)

    if not appointment:
        print("Appointment not found.")
        return

    appointment_status = appointment.get("status", "").lower()
    if appointment_status not in ["consulted", "booked"]:
        print("Invalid appointment status.")
        return

    patient_id = appointment.get("patientID")

    try:
        consult_price = float(input("Enter Consultation Price (RM): "))
        if consult_price < 0:
            raise ValueError
    except ValueError:
        print("Invalid consultation price.")
        return

    medicine_total = 0.0
    medicine_ids = appointment.get("medicine", "")

    if medicine_ids:
        medicines = utils.read_records(MEDICINE_FILE)
        for med_id in [m.strip() for m in medicine_ids.split(",")]:
            med = next((m for m in medicines if m.get("medID") == med_id), None)
            if med:
                medicine_total += float(med.get("price", 0))

    total_amount = consult_price + medicine_total

    print("\n=== Bill Summary ===")
    print(f"Consultation Fee : RM {consult_price:.2f}")
    print(f"Medicine Fee     : RM {medicine_total:.2f}")
    print(f"Total Amount     : RM {total_amount:.2f}")

    if input("\nRecord this bill? (yes/no): ").lower() != "yes":
        return

    bill_status = "paid" if appointment_status == "consulted" else "unpaid"

    # 🔑 Generate Bill ID (BEST PRACTICE)
    records = utils.read_records(INCOME_FILE)
    bill_id = f"B{len(records) + 1}"

    bill = {
        "billID": bill_id,
        "patient": patient_id,
        "appointmentID": apt_id,
        "consultationFee": consult_price,
        "medicineFee": medicine_total,
        "amount": total_amount,
        "status": bill_status
    }

    utils.add_record(INCOME_FILE, bill)
    write_bill_receipt(bill, appointment)

    if appointment_status == "consulted":
        utils.update_record(APPOINTMENT_FILE, apt_id, {"status": "paid"})
        print("\nBill recorded and appointment marked as paid.")
    else:
        print("\nBill recorded as unpaid.")


def view_unpaid_bills():
    records = utils.read_records(INCOME_FILE)
    unpaid = [r for r in records if r.get("status") == "unpaid"]

    print("\n=== Unpaid Bills ===")
    if not unpaid:
        print("No unpaid bills.")
    else:
        for bill in unpaid:
            print(
                f"{bill.get('billID', 'N/A')} | "
                f"{bill.get('patient', 'Unknown')} | "
                f"RM {bill.get('amount', 0):.2f}"
            )

    input("\nPress Enter to continue...")


def income_summary():
    records = utils.read_records(INCOME_FILE)

    paid = [r for r in records if r.get("status") == "paid"]
    unpaid = [r for r in records if r.get("status") == "unpaid"]

    print("\n=== INCOME SUMMARY ===")
    print(f"Paid Total     : RM {sum(float(r.get('amount', 0)) for r in paid):.2f}")
    print(f"Outstanding    : RM {sum(float(r.get('amount', 0)) for r in unpaid):.2f}")
    print(f"Total Revenue  : RM {sum(float(r.get('amount', 0)) for r in records):.2f}")

    input("\nPress Enter to continue...")


def accountant_menu():
    while True:
        os.system("cls" if os.name == "nt" else "clear")
        print("\n=== Accounts Personnel Menu ===")
        print("1. Calculate and Record Patient Bill")
        print("2. View Unpaid Bills")
        print("3. View Income Summary")
        print("4. Back to Main Menu")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            calculate_patient_bill()
        elif choice == "2":
            view_unpaid_bills()
        elif choice == "3":
            income_summary()
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
            input("Press Enter to continue...")
