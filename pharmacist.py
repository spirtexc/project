import os
import utils




current_path = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(current_path, "data")
os.makedirs(data_dir, exist_ok=True)

med_source = os.path.join(data_dir, "medicine.txt")
consultation_source = os.path.join(data_dir, "appointment.txt")

LOW_STOCK_LIMIT = 5



def generate_med_id():
    medicines = utils.read_records(med_source)

    max_num = 0
    for med in medicines:
        med_id = med.get("medID", "")
        if med_id.startswith("M") and med_id[1:].isdigit():
            max_num = max(max_num, int(med_id[1:]))

    return f"M{max_num + 1}"



def add_medicine():
    print("\n--- Add Medicine ---")

    name = input("Enter medicine name (or type 'exit'): ").strip()
    if name.lower() == "exit":
        return

    try:
        stock = int(input("Enter stock quantity: "))
        price = float(input("Enter price (RM): "))
    except ValueError:
        print("Invalid stock or price input.")
        return

    med_id = generate_med_id()

    record = {
        "medID": med_id,
        "name": name,
        "stock": stock,
        "price": round(price, 2)
    }

    utils.add_record(med_source, record)



def update_medicine():
    print("\n--- Update Medicine ---")
    med_id = input("Enter Medicine ID (e.g., M1): ").strip()

    medicine = utils.find_record(med_source, "and", {"medID": med_id})
    if not medicine:
        print("Medicine not found.")
        return

    print("\n1. Update Stock")
    print("2. Update Price")
    choice = input("Enter choice: ").strip()

    updates = {}

    try:
        if choice == "1":
            updates["stock"] = int(input("Enter new stock: "))
        elif choice == "2":
            updates["price"] = round(float(input("Enter new price (RM): ")), 2)
        else:
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return

    utils.update_record(med_source, med_id, updates)




def mark_appointment_completed(apt_id):
    appointment = utils.find_record(
        consultation_source,
        "and",
        {"aptID": apt_id}
    )

    if not appointment:
        print("Appointment not found.")
        return

    appointment = appointment[0]

    if appointment.get("status") != "paid":
        print("Status not updated (appointment not paid or already completed).")
        return

    utils.update_record(
        consultation_source,
        apt_id,
        {"status": "completed"}
    )

    print("Appointment status updated to COMPLETED.")



def remove_medicine():
    print("\n--- Remove Medicine ---")
    med_id = input("Enter Medicine ID: ").strip()


    medicine = utils.find_record(med_source, "and", {"medID": med_id})

    if not medicine:
        print("Medicine not found.")
        return
    print("\nMedicine to be deleted:")
    utils.pretty_print_box(medicine[0])
    confirm = input("Are you sure you want to delete this medicine? (y/n): ").strip().lower()
    if confirm == "y":
        utils.delete_record(med_source, med_id)
    else:
        print("Deletion cancelled.")


def manage_medicine_menu():
    while True:
        print("\n===== Manage Medicine Records =====")
        print("1. Add Medicine")
        print("2. Update Medicine")
        print("3. Remove Medicine")
        print("4. Back")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            add_medicine()
        elif choice == "2":
            update_medicine()
        elif choice == "3":
            remove_medicine()
        elif choice == "4":
            break
        else:
            print("Invalid option.")





def get_medicine_ids_by_consultation_by_id(consult_id):
    consultations = utils.read_records(consultation_source)

    for consult in consultations:
        cid = str(consult.get("aptID", "")).strip().upper()

        if cid == consult_id:
            medicine = consult.get("medicine")

            if not medicine:
                print("This appointment has no prescription.")
                return []

            if isinstance(medicine, list):
                meds = medicine
            elif isinstance(medicine, str):
                meds = medicine.split(",")
            else:
                meds = []

            return [m.strip().upper() for m in meds if m.strip()]

    print("Appointment not found.")
    return []




def print_medication_list():
    print("\n===== Medication List (By Consultation) =====")

    consult_id = input("Enter Appointment ID (e.g. A1): ").strip().upper()
    prescribed_ids = get_medicine_ids_by_consultation_by_id(consult_id)

    if not prescribed_ids:
        return

    medicines = utils.read_records(med_source)

    needed_medicines = [
        med for med in medicines
        if str(med.get("medID", "")).strip().upper() in prescribed_ids
    ]

    if not needed_medicines:
        print("Prescribed medicines not found in inventory.")
        return


    utils.pretty_print_records(
        needed_medicines,
        headers=["medID", "name", "stock", "price"]
    )


    confirm = input("\nConfirm dispense and complete appointment? (y/n): ").strip().lower()
    if confirm != "y":
        print("Dispense cancelled. Appointment status unchanged.")
        return


    
    # DEDUCT STOCK
    for med in needed_medicines:
        new_stock = int(med.get("stock", 0)) - 1
        if new_stock < 0:
            print(f"Warning: Stock for {med.get('name')} is insufficient!")
            # In a real app we might stop here, but let's proceed with warning or just set to 0
            new_stock = 0
            
        utils.update_record(med_source, med.get("medID"), {"stock": new_stock})
        print(f"Updates: {med.get('name')} stock -> {new_stock}")

    mark_appointment_completed(consult_id)



def view_low_stock():
    print("\n===== Low Stock Alert =====")
    medicines = utils.read_records(med_source)

    found = False
    for med in medicines:
        if int(med.get("stock", 0)) <= LOW_STOCK_LIMIT:
            print(
                f"{med['medID']} | {med['name']} "
                f"→ ONLY {med['stock']} LEFT"
            )
            found = True

    if not found:
        print("All medicines have sufficient stock.")



def pharmacist_menu():
    while True:
        print("\n===================================")
        print(" Pharmacist Management System")
        print("===================================")
        print("1. Manage Medicine Records")
        print("2. View Medication List")
        print("3. View Low Stock Alert")
        print("4. Logout")
        print("===================================")

        choice = input("Enter your choice: ").strip()

        if choice == "1":
            manage_medicine_menu()
        elif choice == "2":
            print_medication_list()
        elif choice == "3":
            view_low_stock()
        elif choice == "4":
            print("Logging out...")
            break
        else:
            print("Invalid choice. Please try again.")