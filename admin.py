'''
Administrator Functions
- Manage clinic users and doctor records (add, update, delete)
- View reports (total patients, appointments, income)
- Generate clinic summary report (staff, medicine)
'''

import os
import difflib
from datetime import date, timedelta

import utils

# ------------------------------
# File paths
# ------------------------------
current_path = os.path.dirname(os.path.abspath(__file__))
user_source = os.path.join(current_path, "data/user.txt")
appointment_source = os.path.join(current_path, "data/appointment.txt")
medicine_source = os.path.join(current_path, "data/medicine.txt")
income_source = os.path.join(current_path, "data/income.txt")

# ---------------------------------------------------
# SHARED ROLE MAP (shortcut -> lowercase stored role)
# ---------------------------------------------------
role_map = {
    "d": "doctor",
    "doctor": "doctor",

    "r": "receptionist",
    "receptionist": "receptionist",

    "p": "pharmacist",
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
def attach_user_names(records, user_map, fields):
    """Return new list with selected fields converted from 'Uid' to 'Uid - name'."""
    result = []
    for r in records:
        new_r = r.copy()
        for field in fields:
            user_id = new_r.get(field)
            if user_id:
                new_r[field] = format_user_id_with_name(user_id, user_map)
        result.append(new_r)
    return result


# ---------------------------------------------------
# ADD USER
# ---------------------------------------------------
def add_user():
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
        added_user = records[-1]
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

    input("\nPress Enter to continue...")


# ---------------------------------------------------
# UPDATE USER
# ---------------------------------------------------
def update_user():
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
    input("\nPress Enter to continue...")


# ---------------------------------------------------
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

    input("\nPress Enter to continue...")


# ---------------------------------------------------
# VIEW INCOME REPORT
# ---------------------------------------------------
def view_income():
    records = utils.read_records(income_source)
    appointments = utils.read_records(appointment_source)
    user_map = load_user_map()

    if not records:
        print("No income records found.")
        input("\nPress Enter to continue...")
        return

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
            "accountant",           # old data compatibility
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

    low_stock = [m for m in records if m.get("stock", 0) < 20]

    print("\n--- Low Stock Medicines (stock < 20) ---")
    if low_stock:
        utils.pretty_print_records(low_stock, ["userID", "name", "stock"])
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
        print("2. Appointments")
        print("3. Income")
        print("4. Back")
        choice = input("Choose: ")

        match choice:
            case "1":
                view_patients()
            case "2":
                view_appointments()
            case "3":
                view_income()
            case "4":
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
