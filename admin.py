<<<<<<< HEAD
"""
=======
'''
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
Administrator Functions
- Manage clinic users and doctor records (add, update, delete)
- View reports (total patients, appointments, income)
- Generate clinic summary report (staff, medicine)
<<<<<<< HEAD
"""
=======
'''
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069

import os
import difflib
from datetime import date, timedelta
<<<<<<< HEAD
=======

>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
import utils

# ------------------------------
# File paths
# ------------------------------
current_path = os.path.dirname(os.path.abspath(__file__))
user_source = os.path.join(current_path, "data/user.txt")
appointment_source = os.path.join(current_path, "data/appointment.txt")
medicine_source = os.path.join(current_path, "data/medicine.txt")
income_source = os.path.join(current_path, "data/income.txt")
<<<<<<< HEAD
patient_source = os.path.join(current_path, "data/patient.txt")
bill_source = os.path.join(current_path, "data/bill.txt")
=======
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069

# ---------------------------------------------------
# SHARED ROLE MAP (shortcut -> lowercase stored role)
# ---------------------------------------------------
role_map = {
    "d": "doctor",
    "doctor": "doctor",

    "r": "receptionist",
    "receptionist": "receptionist",

<<<<<<< HEAD
    "ph": "pharmacist",
=======
    "p": "pharmacist",
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    "pharmacist": "pharmacist",

    "a": "accounts personnel",
    "acc": "accounts personnel",
    "accounts": "accounts personnel",
    "accountant": "accounts personnel",
    "account": "accounts personnel",

    "ad": "administrator",
    "admin": "administrator",
    "administrator": "administrator",

    "p": "patient",
    "patient": "patient"
}


# ---------------------------------------------------
<<<<<<< HEAD
=======
# Helper: load users as dict {id: user_record}
# ---------------------------------------------------
def load_user_map():
    users = utils.read_records(user_source)
    return {u.get("userID"): u for u in users if "userID" in u}


def format_user_id_with_name(user_id, user_map):
    """Return 'U1 - username' if possible, else just id."""
    user = user_map.get(user_id)
    if user:
        return f"{user_id} - {user.get('username', '')}"
    return user_id or ""


# ---------------------------------------------------
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
# Helper: suggest usernames when not found
# ---------------------------------------------------
def suggest_nearest_users(input_name):
    """Print nearest matching usernames and return list of user records."""
    records = utils.read_records(user_source)
    usernames = [r["username"] for r in records if "username" in r]

    close = difflib.get_close_matches(input_name, usernames, n=3, cutoff=0.4)

    if not close:
        print("\nNo similar usernames found.")
        return []

    print("\nDid you mean:")
    suggestions = []
    for name in close:
        user = next(r for r in records if r["username"] == name)
        phone = user.get("phone", "No phone")
        print(f" - {name}  (Phone: {phone})")
        suggestions.append(user)

    return suggestions


# ---------------------------------------------------
# Helper: attach user names to id fields on copies
# ---------------------------------------------------
<<<<<<< HEAD
def attach_user_names(records, user_records, patient_records, fields):
    #Return new list with selected fields converted from 'Uid' to 'Uid - name'
=======
def attach_user_names(records, user_map, fields):
    """Return new list with selected fields converted from 'Uid' to 'Uid - name'."""
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    result = []
    for r in records:
        new_r = r.copy()
        for field in fields:
<<<<<<< HEAD
            id_val = new_r.get(field)
            if not id_val:
                continue
            name = ""
            if field in ["patientID", "userID"]:
                patient = next((p for p in patient_records if p.get("patientID") == id_val), None)
                if patient:
                    name = patient.get("name", "")
            if not name:
                user = next((u for u in user_records if u.get("userID") == id_val), None)
                if user:
                    name = user.get("username", "")
            if name:
                new_r[field] = f"{id_val} - {name}"
            else:
                new_r[field] = id_val
=======
            user_id = new_r.get(field)
            if user_id:
                new_r[field] = format_user_id_with_name(user_id, user_map)
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
        result.append(new_r)
    return result


# ---------------------------------------------------
# ADD USER
# ---------------------------------------------------
def add_user():
<<<<<<< HEAD
    _, userID = utils.next_id(user_source)
    # Validate username
    while True:
        username = input("Enter username (3-20 chars, no spaces): ").strip()
        if not username:
            print("Username cannot be empty.")
            continue
        if len(username) < 3 or len(username) > 20:
            print("Username must be between 3 and 20 characters.")
            continue
        if " " in username:
            print("Username cannot contain spaces.")
            continue
        # Check for duplicate username
        existing = utils.find_record(user_source, "and", {"username": username})
        if existing:
            print("Username already exists. Please choose another.")
            continue
        break
    # Validate password
    while True:
        password = input("Enter password (minimum 3 characters): ").strip()
        if len(password) < 3:
            print("Password must be at least 3 characters long.")
            continue
        break
    # Validate age
    while True:
        age = input("Enter age (1-120): ").strip()
        if not age.isdigit():
            print("Age must be a number.")
            continue
        age_int = int(age)
        if age_int < 1 or age_int > 120:
            print("Age must be between 1 and 120.")
            continue
        break
    # Validate phone number
    while True:
        phone = input("Enter phone number (e.g., 012-3456789): ").strip()
        # Remove hyphens for validation
        phone_digits = phone.replace("-", "")
        if not phone_digits.isdigit():
            print("Phone number must contain only digits and hyphens.")
            continue
        if len(phone_digits) < 10 or len(phone_digits) > 11:
            print("Phone number must be 10-11 digits.")
            continue
        break

    print("\nEnter role ([D]octor / [R]eceptionist / [PH]armacist / "
          "[A]ccounts Personnel / [AD]ministrator / [P]atients:")
    

    while True:
        role_input = input("Role: ").strip().lower()
        if role_input not in role_map:
            print("Invalid role. Please enter one of: D, R, PH, A, AD, P")
            continue
        break

    role = role_map[role_input]
=======
    userID = utils.read_records(user_source, "userID")
    if not userID:
        userID = "U1"
    else:
        userID = f"U{len(userID) + 1}"
    username = input("Enter username: ")
    password = input("Enter password: ")
    age = input("Enter age: ")
    phone = input("Enter phone number: ")

    print("\nEnter role ([D]octor / [R]eceptionist / [P]harmacist / "
          "[A]ccounts Personnel / [AD]ministrator / [U]ser(patients)):")
    role_input = input("Role: ").strip().lower()

    if role_input not in role_map:
        print("Invalid role. User not added.")
        input("Press Enter to continue...")
        return

    role = role_map[role_input]  # lowercase stored role
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069

    new_user = {
        "userID": userID,
        "username": username,
        "password": password,
        "age": age,
        "role": role,
        "status": "active",
        "phone": phone
    }

    utils.add_record(user_source, new_user)

    # Show confirmation and the created record
    os.system('cls||clear')
    print("User added successfully!\n")

    records = utils.read_records(user_source)
    if records:
<<<<<<< HEAD
        added_user = records[-1]                                            
=======
        added_user = records[-1]
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
        utils.pretty_print_box(added_user)

    input("\nPress Enter to continue...")


# ---------------------------------------------------
# REMOVE USER
# ---------------------------------------------------
def remove_user():
    keyword = input("Enter username or user ID to remove: ")

    found = utils.find_record(user_source, "or", {
        "username": keyword,
        "userID": keyword
    })

    if not found:
        print("User not found.")
        suggest_nearest_users(keyword)
        input("\nPress Enter to continue...")
        return

<<<<<<< HEAD
    # Assume only one match for simplicity
    user = found[0]
    user_id = user.get("userID")

    print("\nUser found:")
    utils.pretty_print_box(user)

    confirm = input("Confirm delete? (y/n): ").strip().lower()
    if confirm != "y":
        print("Delete cancelled.")
        input("\nPress Enter to continue...")
        return

    utils.delete_record(user_source, user_id)
    print("User removed successfully.")
=======
    print("\nMatching User(s):")
    utils.pretty_print_records(found)

    confirm = input("Enter EXACT userID to confirm deletion: ")
    deleted_user = next((u for u in found if u.get("userID") == confirm), None)

    if deleted_user is None:
        print("Invalid userID. Deletion cancelled.")    
        input("Press Enter to continue...")
        return

    utils.delete_record(user_source, confirm)

    os.system('cls||clear')
    print("User deleted successfully!\n")
    print("Deleted User Record:")
    utils.pretty_print_box(deleted_user)

>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    input("\nPress Enter to continue...")


# ---------------------------------------------------
# UPDATE USER
# ---------------------------------------------------
def update_user():
<<<<<<< HEAD
    keyword = input("Enter username or user ID to update: ")

    found = utils.find_record(user_source, "or", {
        "username": keyword,
        "userID": keyword
    })

    if not found:
        print("User not found.")
        suggest_nearest_users(keyword)
        input("\nPress Enter to continue...")
        return

    # Assume one match
    user = found[0]
    user_id = user.get("userID")

    print("\nUser found:")
    utils.pretty_print_box(user)

    print("\nEnter new values (leave blank to keep current):")

    new_username = input("New username: ").strip()
    new_password = input("New password: ").strip()
    new_age = input("New age: ").strip()
    new_phone = input("New phone: ").strip()
    new_role = input("New role: ").strip().lower()

    updates = {}
    if new_username:
        updates["username"] = new_username
    if new_password:
        updates["password"] = new_password
    if new_age:
        updates["age"] = new_age
    if new_phone:
        updates["phone"] = new_phone
    if new_role in role_map:
        updates["role"] = role_map[new_role]

    if not updates:
        print("No changes made.")
        input("\nPress Enter to continue...")
        return

    utils.update_record(user_source, user_id, updates)
    input("\nPress Enter to continue...")


# ---------------------------------------------------
# VIEW PATIENTS
# ---------------------------------------------------
def view_patients():
    records = utils.read_records(patient_source)

    if not records:
        print("No patients found.")
        input("\nPress Enter to continue...")
        return

    print("\nTotal Patients:", len(records))
    utils.pretty_print_records(records, ["patientID", "name", "dob", "age", "phone", "status"])
=======
    username = input("Enter username to update: ")

    records = utils.read_records(user_source)
    user = next((r for r in records if r.get("username") == username), None)

    if not user:
        print("User not found.")
        suggest_nearest_users(username)
        input("\nPress Enter to continue...")
        return

    print("\nCurrent User Data:")
    utils.pretty_print_box(user)

    new_pass = input("New password (leave blank to keep): ")

    print("\nEnter new role ([D]octor / [R]eceptionist / [P]harmacist / "
          "[A]ccounts Personnel / [AD]ministrator / [U]ser(patients))\n"
          "(leave blank to keep):")
    role_input = input("Role: ").strip().lower()

    new_age = input("New age (leave blank to keep): ")

    updates = {}

    if new_pass:
        updates["password"] = new_pass

    if role_input:
        if role_input not in role_map:
            print("Invalid role entered. Role not updated.")
        else:
            updates["role"] = role_map[role_input] 
    if new_age:
        updates["age"] = new_age

    if updates:
        utils.update_record(user_source, user["userID"], updates)

        os.system('cls||clear')
        print("User updated successfully!\n")

        # Reload updated record
        new_records = utils.read_records(user_source)
        updated = next((r for r in new_records if r.get("userID") == user["userID"]), user)

        print("Updated Record:")
        utils.pretty_print_box(updated)
        input("\nPress Enter to continue...")
    else:
        print("No changes applied.")
        input("Press Enter to continue...")


# ---------------------------------------------------
# VIEW PATIENTS REPORT  (role = 'patient')
# ---------------------------------------------------
def view_patients():
    records = utils.read_records(user_source)
    patients = [r for r in records if r.get("role") == "patient"]

    print("\nTotal Patients:", len(patients))

    show = input("Show details? (yes/no): ").lower()
    if show == "yes":
        utils.pretty_print_records(patients)
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    input("\nPress Enter to continue...")


# ---------------------------------------------------
<<<<<<< HEAD
# VIEW UPCOMING APPOINTMENTS
# ---------------------------------------------------
def view_upcoming_appointments():
    today = date.today()
    days = [today + timedelta(days=i) for i in range(1, 8)]
    records = utils.read_records(appointment_source)
    user_records = utils.read_records(user_source)
    patient_records = utils.read_records(patient_source)
    overview = []
    for day in days:
        booked = sum(1 for r in records if r.get("date") == day.isoformat() and r.get("status") == "Booked")
        cancelled = sum(1 for r in records if r.get("date") == day.isoformat() and r.get("status") == "Cancelled")
        total = booked + cancelled
        overview.append({
            "Date": day.isoformat(),
            "Booked": booked,
            "Cancelled": cancelled,
            "Total": total
        })
    print("\n--- Next 7 Days Overview ---")
    utils.pretty_print_records(overview, ["Date", "Booked", "Cancelled", "Total"])
    
    try:
        day_num = int(input("\nSelect day (1-7): "))
        if 1 <= day_num <= 7:
            selected_day = days[day_num - 1]
            status_input = input("Show [B]ooked, [C]ancelled, or [A]ll: ").strip().lower()
            if status_input == 'b':
                status_filter = ["Booked"]
            elif status_input == 'c':
                status_filter = ["Cancelled"]
            else:
                status_filter = ["Booked", "Cancelled"]
            appts = [r for r in records if r.get("date") == selected_day.isoformat() and r.get("status") in status_filter]
            if appts:
                display = attach_user_names(appts, user_records, patient_records, ["patientID", "doctorID"])
                print(f"\n--- Appointments for {selected_day} ---")
                utils.pretty_print_records(display, ["aptID", "patientID", "doctorID", "date", "time", "status"])
            else:
                print("No appointments for selected criteria.")
        else:
            print("Invalid day number.")
    except ValueError:
        print("Please enter a number.")
    
    input("\nPress Enter to continue...")


# ---------------------------------------------------
# VIEW APPOINTMENTS HISTORY
# ---------------------------------------------------
def view_appointments_history():
    os.system('cls||clear')
    print("\n--- Appointments History ---")
    appointments = utils.read_records(appointment_source)
    user_records = utils.read_records(user_source)
    patient_records = utils.read_records(patient_source)
    if appointments:
        display = attach_user_names(appointments, user_records, patient_records, ["patientID", "doctorID"])
        utils.pretty_print_records(display, ["aptID", "patientID", "doctorID", "date", "time", "status"])
    else:
        print("No appointments found.")
=======
# VIEW APPOINTMENTS REPORT
# ---------------------------------------------------
def view_appointments():
    today = date.today()
    records = utils.read_records(appointment_source)
    user_map = load_user_map()

    confirmed = [r for r in records if r.get("status") == "confirmed"]
    print("\nTotal Confirmed Appointments:", len(confirmed))

    print("\nPending & Cancelled (next 7 days):\n")

    for i in range(1, 8):
        check_date = (today + timedelta(days=i)).strftime("%Y-%m-%d")

        pending = [r for r in records
                   if r.get("status") == "pending" and r.get("date") == check_date]

        cancelled = [r for r in records
                     if r.get("status") == "cancelled" and r.get("date") == check_date]

        print(f"{check_date}: Pending={len(pending)}, Cancelled={len(cancelled)}")

    show = input("\nShow filtered appointment details? (yes/no): ").lower()
    if show != "yes":
        return

    status = input("Status (pending/cancelled/confirmed): ").lower()
    date_range = input("Date range (YYYY-MM-DD to YYYY-MM-DD): ")
    time_range = input("Time range (HH:MM to HH:MM): ")

    try:
        date_from, date_to = [d.strip() for d in date_range.split("to")]
        time_from, time_to = [t.strip() for t in time_range.split("to")]
    except Exception:
        print("Invalid range format.")
        input("\nPress Enter to continue...")
        return

    filtered = [
        r for r in records
        if r.get("status") == status
        and date_from <= r.get("date", "") <= date_to
        and time_from <= r.get("time", "") <= time_to
    ]

    print("\nFiltered Results:")
    if filtered:
        # Convert patient & doctor id → "Uid - name"
        display = attach_user_names(filtered, user_map, ["patient", "doctor"])
        utils.pretty_print_records(display, ["aptID", "patient", "date", "time", "doctor", "status"])
    else:
        print("No matching appointments found.")

>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    input("\nPress Enter to continue...")


# ---------------------------------------------------
# VIEW INCOME REPORT
# ---------------------------------------------------
def view_income():
    records = utils.read_records(income_source)
<<<<<<< HEAD
    user_records = utils.read_records(user_source)
    patient_records = utils.read_records(patient_source)
    apt_records = utils.read_records(appointment_source)
=======
    appointments = utils.read_records(appointment_source)
    user_map = load_user_map()

>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    if not records:
        print("No income records found.")
        input("\nPress Enter to continue...")
        return
<<<<<<< HEAD
    paid = [r for r in records if r.get("status") == "paid"]
    total_income = sum(float(r.get("amount", 0)) for r in paid)
    print("\n--- Income Summary ---")
    print("Total Income Collected: RM", total_income)
    print("Paid Bills:", len(paid))
    detail = input("\nShow detailed records? (yes/no): ").strip().lower()
    if detail != "yes":
        input("\nPress Enter to continue...")
        return
    print("\n--- Paid Bills ---")
    display_paid = []
    for r in paid:
        patient_id = r.get("userID") or r.get("patient", "")
        name = ""
        patient = next((p for p in patient_records if p.get("patientID") == patient_id), None)
        if patient:
            name = patient.get("name", "")
        if not name:
            user = next((u for u in user_records if u.get("userID") == patient_id), None)
            if user:
                name = user.get("username", "")
        display_id = f"{patient_id} - {name}" if name else patient_id
        apt_id = r.get("appointmentID", "") or r.get("aptID", "")
        date = ""
        if apt_id:
            apt = next((a for a in apt_records if a.get("aptID") == apt_id), None)
            if apt:
                date = apt.get("date", "")
        new_r = {
            "inID": r.get("inID", ""),
            "userID": display_id,
            "amount": r.get("amount", ""),
            "date": date
        }
        display_paid.append(new_r)
    utils.pretty_print_records(display_paid, ["inID", "userID", "amount", "date"])
=======

    paid = [r for r in records if r.get("status") == "paid"]
    unpaid = [r for r in records if r.get("status") == "unpaid"]

    total_income = sum(float(r.get("amount", 0)) for r in paid)

    print("\n--- Income Summary ---")
    print("Total Income Collected: RM", total_income)
    print("Paid Bills:", len(paid))
    print("Unpaid Bills:", len(unpaid))

    detail = input("\nShow detailed records? (paid/unpaid): ").strip().lower()

    # ---- PAID ----
    if detail == "paid":
        print("\n--- Paid Bills ---")
        display_paid = attach_user_names(paid, user_map, ["patient"])
        utils.pretty_print_records(display_paid, ["inID", "patient", "amount", "status"])
        input("\nPress Enter to continue...")
        return

    # ---- UNPAID + RELATED APPOINTMENTS ----
    if detail == "unpaid":
        print("\n--- Unpaid Bills ---")
        display_unpaid = attach_user_names(unpaid, user_map, ["patient"])
        utils.pretty_print_records(display_unpaid, ["inID", "patient", "amount", "status"])

        print("\n--- Related Appointments for Unpaid Bills ---")
        unpaid_patient_ids = [b.get("patient") for b in unpaid if b.get("patient")]

        related_appointments = [
            a for a in appointments
            if a.get("patient") in unpaid_patient_ids
        ]

        if related_appointments:
            display_app = attach_user_names(related_appointments, user_map, ["patient", "doctor"])
            utils.pretty_print_records(
                display_app,
                ["aptID", "patient", "date", "time", "doctor", "status"]
            )
        else:
            print("No appointments found for unpaid bills.")

        input("\nPress Enter to continue...")
        return

    print("Invalid option.")
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    input("\nPress Enter to continue...")


# ---------------------------------------------------
# STAFF SUMMARY (non-patients)
# ---------------------------------------------------
def staff_summary():
    records = utils.read_records(user_source)
    staff = [
        r for r in records
        if r.get("role") in [
            "administrator",
            "doctor",
            "pharmacist",
            "accounts personnel",
<<<<<<< HEAD
            "accountant",           
=======
            "accountant",           # old data compatibility
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
            "receptionist"
        ]
    ]

    print("\nTotal Staff:", len(staff))
    utils.pretty_print_records(staff, ["userID", "username", "role"])
    input("Press Enter to continue...")


# ---------------------------------------------------
# MEDICINE SUMMARY
# ---------------------------------------------------
def medicine_summary():
    records = utils.read_records(medicine_source)

    if not records:
        print("No medicine records found.")
        input("\nPress Enter to continue...")
        return

    print("\n--- Medicine Summary ---")
    print("Total Medicine Items:", len(records))
    utils.pretty_print_records(records, ["medID", "name", "stock", "price"])
    # Convert stock to int for comparison
    records = [{**m, "stock": int(m.get("stock", 0))} for m in records]
<<<<<<< HEAD
    low_stock_value = 20
    low_stock = [m for m in records if m.get("stock", 0) < low_stock_value]

    print(f"\n--- Low Stock Medicines (stock < {low_stock_value}) ---")
    if low_stock:
        utils.pretty_print_records(low_stock, ["medID", "name", "stock"])
=======

    low_stock = [m for m in records if m.get("stock", 0) < 20]

    print("\n--- Low Stock Medicines (stock < 20) ---")
    if low_stock:
        utils.pretty_print_records(low_stock, ["userID", "name", "stock"])
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
    else:
        print("No low-stock medicines.\n")

    input("\nPress Enter to continue...")


# ---------------------------------------------------
# SUB-MENUS
# ---------------------------------------------------
def manage_users_menu():
    while True:
        os.system('cls||clear')
        print("\n--- Manage Clinic Users ---")
        print("1. Add User")
        print("2. Remove User")
        print("3. Update User")
        print("4. Back")
        choice = input("Choose: ")

        match choice:
            case "1":
                add_user()
            case "2":
                remove_user()
            case "3":
                update_user()
            case "4":
                return
            case _:
                print("Invalid choice.")
                input("Press Enter to continue...")


def view_reports_menu():
    while True:
        os.system('cls||clear')
        print("\n--- Reports ---")
        print("1. Total Patients")
<<<<<<< HEAD
        print("2. Upcoming Appointments")
        print("3. Appointments History")
        print("4. Income")
        print("5. Back")
=======
        print("2. Appointments")
        print("3. Income")
        print("4. Back")
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
        choice = input("Choose: ")

        match choice:
            case "1":
                view_patients()
            case "2":
<<<<<<< HEAD
                view_upcoming_appointments()
            case "3":
                view_appointments_history()
            case "4":
                view_income()
            case "5":
=======
                view_appointments()
            case "3":
                view_income()
            case "4":
>>>>>>> f3a60dd9ce629b5da2f106cdfcb3dc01ec8bd069
                return
            case _:
                print("Invalid choice.")
                input("Press Enter to continue...")


def generate_summary_menu():
    while True:
        os.system('cls||clear')
        print("\n--- Clinic Summary ---")
        print("1. Staff Summary")
        print("2. Medicine Summary")
        print("3. Back")
        choice = input("Choose: ")

        match choice:
            case "1":
                staff_summary()
            case "2":
                medicine_summary()
            case "3":
                return
            case _:
                print("Invalid choice.")
                input("Press Enter to continue...")


# ---------------------------------------------------
# MAIN ADMIN MENU
# ---------------------------------------------------
def admin_menu():
    while True:
        os.system('cls||clear')
        print("\n--- Administrator Menu ---")
        print("1. Manage Users")
        print("2. View Reports")
        print("3. Generate Summary Report")
        print("4. Back to Main Menu")
        choice = input("Choose: ")

        match choice:
            case "1":
                manage_users_menu()
            case "2":
                view_reports_menu()
            case "3":
                generate_summary_menu()
            case "4":
                return
            case _:
                print("Invalid choice.")
                input("Press Enter to continue...")
