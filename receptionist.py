import os
import re
import json
import difflib
from datetime import datetime, date, timedelta

# Okay, let's set up the base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# File paths for our data storage
PATIENT_FILE = os.path.join(DATA_DIR, "patient.txt")
USER_FILE = os.path.join(DATA_DIR, "user.txt")  # doctors stored here with role=doctor
APPT_FILE = os.path.join(DATA_DIR, "appointment.txt")

# Simple regex for validating names
NAME_RE = re.compile(r"^[A-Za-z .'-]+$")


# ==============================
# BASIC UTILITY FUNCTIONS
# ==============================
def clear_screen():
    """Clear the terminal screen"""
    os.system("cls" if os.name == "nt" else "clear")


def ensure_data_file_exists(file_path):
    """Make sure the data file exists, create it if not"""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if not os.path.exists(file_path):
        # Just initialize with empty array
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("[]")


def load_json_data(file_path):
    """Load JSON data from file, return empty list if problems"""
    ensure_data_file_exists(file_path)
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Sometimes data might not be a list for some reason
            if isinstance(data, list):
                return data
            else:
                return []
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or missing, just return empty
        return []


def save_json_data(file_path, data_rows):
    """Save data back to JSON file"""
    ensure_data_file_exists(file_path)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data_rows, f, indent=4)


def display_single_record(record):
    """Display a single record in key: value format"""
    if not record:
        print("(no data to show)")
        return

    # Calculate max width for alignment
    max_width = 0
    for k in record.keys():
        if len(k) > max_width:
            max_width = len(k)

    for key in record:
        value = record.get(key, '')
        print(f"{key:<{max_width}} : {value}")


def display_table(records, column_names):
    """Display records in a nice table format"""
    if not records:
        print("(no records found)")
        return

    # Calculate column widths
    col_widths = {}
    for col in column_names:
        col_widths[col] = len(col)

    for record in records:
        for col in column_names:
            val_str = str(record.get(col, ""))
            if len(val_str) > col_widths[col]:
                col_widths[col] = len(val_str)

    # Print header
    header_parts = []
    for col in column_names:
        header_parts.append(col.ljust(col_widths[col]))
    header = " | ".join(header_parts)
    print(header)

    # Print separator line
    sep_parts = []
    for col in column_names:
        sep_parts.append("-" * col_widths[col])
    separator = "-+-".join(sep_parts)
    print(separator)

    # Print each row
    for record in records:
        row_parts = []
        for col in column_names:
            val = str(record.get(col, ""))
            row_parts.append(val.ljust(col_widths[col]))
        row_data = " | ".join(row_parts)
        print(row_data)


# ==============================
# INPUT VALIDATION
# ==============================
def try_parse_date(date_string):
    """Try to parse date string in various formats"""
    date_string = date_string.strip()
    date_string = date_string.replace(",", " ")  # Remove commas if any

    # Try different date formats
    fmts = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d %B %Y",  # Like "15 January 2024"
        "%d %b %Y",  # Like "15 Jan 2024"
        "%B %d %Y",  # Like "January 15 2024"
        "%b %d %Y",  # Like "Jan 15 2024"
    ]

    for fmt in fmts:
        try:
            parsed = datetime.strptime(date_string, fmt).date()
            return parsed
        except ValueError:
            continue

    return None


def get_valid_name(prompt_message):
    """Get a valid name from user input"""
    while True:
        v = input(prompt_message).strip()
        if not v:
            print("Name cannot be empty.")
            continue
        if not NAME_RE.match(v):
            print("Only letters/spaces and . ' - allowed (no @#$%).")
            continue
        return v


def get_valid_phone(prompt_message):
    """Get valid phone number"""
    while True:
        v = input(prompt_message).strip()
        if not v:
            print("Phone number cannot be empty.")
            continue
        # Simple phone validation - numbers, plus, hyphen, spaces
        if not re.fullmatch(r"[0-9+\- ]{7,20}", v):
            print("Invalid phone format.")
            continue
        return v


def get_valid_birth_date(prompt_message):
    """Get valid birth date (cannot be future)"""
    while True:
        d = try_parse_date(input(prompt_message).strip())
        if not d:
            print("Invalid date format.")
            continue
        if d > date.today():
            print("Birth date cannot be in the future.")
            continue
        return d.strftime("%Y-%m-%d")


def get_future_date(prompt_message):
    """Get a date that must be in the future"""
    while True:
        d = try_parse_date(input(prompt_message).strip())
        if not d:
            print("Invalid date format.")
            continue
        if d <= date.today():
            print("Appointment date must be AFTER today (no same-day booking).")
            continue
        return d.strftime("%Y-%m-%d")


def get_valid_time(prompt_message):
    """Get valid time in HH:MM format"""
    while True:
        t = input(prompt_message).strip()
        try:
            datetime.strptime(t, "%H:%M")
            return t
        except ValueError:
            print("Invalid time format. Use HH:MM (example: 14:30)")


def calculate_age_from_birthdate(birthdate_string):
    """Calculate current age from birthdate"""
    birth_date = datetime.strptime(birthdate_string, "%Y-%m-%d").date()
    today = date.today()

    age = today.year - birth_date.year
    # Adjust if birthday hasn't occurred yet this year
    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    if age < 0:
        age = 0  # Just in case

    return age


# ==============================
# ID GENERATION
# ==============================
def extract_prefix_and_number(id_string):
    """Extract prefix and number from ID like 'P123' -> ('P', 123)"""
    s = str(id_string).strip()
    prefix = ""
    num = ""

    for ch in s:
        if ch.isdigit():
            num += ch
        else:
            # Only add to prefix if we haven't started collecting numbers
            if not num:
                prefix += ch

    num_val = int(num) if num.isdigit() else 0
    return prefix, num_val


def generate_next_id(file_path, id_prefix, id_field_name):
    """Generate next ID with given prefix"""
    rows = load_json_data(file_path)

    if not rows:
        return f"{id_prefix}1"

    mx = 0
    for r in rows:
        p, n = extract_prefix_and_number(r.get(id_field_name, ""))
        if p.upper() == id_prefix.upper():
            if n > mx:
                mx = n

    next_num = mx + 1
    return f"{id_prefix}{next_num}"


# ==============================
# DOCTORS FROM user.txt ONLY
# ==============================
def get_doctors_from_user_file():
    """Get all doctors from user.txt where role=doctor"""
    users = load_json_data(USER_FILE)
    doctors = []

    for u in users:
        role = str(u.get("role", "")).strip().lower()
        if role == "doctor":
            # Try to get doctor ID - might be userID or doctorID field
            did = u.get("userID")
            if not did:
                did = u.get("doctorID")

            name = u.get("username")
            if not name:
                name = u.get("name")

            if did and name:
                doctors.append({
                    "doctorID": str(did),
                    "name": str(name),
                    "phone": u.get("phone", "")
                })

    # Sort by ID for consistency
    doctors.sort(key=lambda x: x["doctorID"])
    return doctors


def doctor_exists_by_id(doctor_id):
    """Check if doctor with this ID exists and has doctor role"""
    doctors = get_doctors_from_user_file()
    for d in doctors:
        if str(d.get("doctorID")) == str(doctor_id):
            return d
    return None


def select_doctor_by_id_show_all():
    """Show all doctors and let user select by ID"""
    doctors = get_doctors_from_user_file()

    if not doctors:
        print("No doctors found in user.txt (role=doctor).")
        return None

    print("\n=== AVAILABLE DOCTORS (from user.txt) ===")
    display_table(doctors, ["doctorID", "name", "phone"])

    did = input("\nEnter Doctor ID to assign: ").strip()
    if not did:
        print("Doctor ID is required.")
        return None

    chosen = doctor_exists_by_id(did)
    if not chosen:
        print("Doctor ID not found OR user does not have doctor role.")
        return None

    return chosen


# ==============================
# APPOINTMENT CONFLICT RULES
# - same doctor cannot have another appt within 2 hours same day
# ==============================
def parse_appt_datetime(appt_date_str, appt_time_str):
    """Parse appointment date and time into datetime object"""
    dt_str = f"{appt_date_str} {appt_time_str}"
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M")


def is_doctor_available(doctor_id, appt_date_str, appt_time_str, exclude_apt_id=None):
    """Check if doctor is available at given date/time (2-hour window rule)"""
    appts = load_json_data(APPT_FILE)

    target_dt = parse_appt_datetime(appt_date_str, appt_time_str)

    for a in appts:
        # Skip the appointment we're updating
        if exclude_apt_id:
            if str(a.get("aptID")) == str(exclude_apt_id):
                continue

        # Only check same doctor
        if str(a.get("doctorID", "")) != str(doctor_id):
            continue

        # Skip cancelled appointments
        status = str(a.get("status", "")).lower()
        if status in ("cancelled", "canceled"):
            continue

        # Only check same date
        if a.get("date") != appt_date_str:
            continue

        # Parse existing appointment time
        try:
            existing_dt = parse_appt_datetime(a.get("date", ""), a.get("time", ""))
        except Exception:
            continue

        # Check if within 2 hours
        time_diff = abs((target_dt - existing_dt).total_seconds())
        two_hours = 2 * 3600

        if time_diff < two_hours:
            return False, a

    return True, None
def is_patient_available(patient_id, appt_date_str, appt_time_str, exclude_apt_id=None):
    """Check if patient already has an appointment at the same date and time"""
    appts = load_json_data(APPT_FILE)

    for a in appts:
        # Skip the appointment we're updating
        if exclude_apt_id:
            if str(a.get("aptID")) == str(exclude_apt_id):
                continue

        # Same patient
        if str(a.get("patientID")) != str(patient_id):
            continue

        # Skip cancelled appointments
        status = str(a.get("status", "")).lower()
        if status in ("cancelled", "canceled"):
            continue

        # Same date and same time
        if a.get("date") == appt_date_str and a.get("time") == appt_time_str:
            return False, a

    return True, None


# ==============================
# PATIENT LOOKUP
# ==============================
def find_person_by_name(file_path, id_field, extra_display_columns=()):
    """Search for a person by name with fuzzy matching"""
    rows = load_json_data(file_path)

    if not rows:
        print("No records found.")
        return None

    q = get_valid_name("Enter name to search: ").strip().lower()

    # First try exact match
    exact = []
    for r in rows:
        if r.get("name", "").strip().lower() == q:
            exact.append(r)

    if len(exact) == 1:
        return exact[0]

    # Try partial match
    partial = []
    for r in rows:
        if q in r.get("name", "").lower():
            partial.append(r)

    if partial:
        partial.sort(key=lambda x: str(x.get(id_field, "")))
        preview = partial[:5]  # Show first 5

        cols = [id_field, "name"]
        for col in extra_display_columns:
            cols.append(col)

        display_table(preview, cols)

        chosen = input(f"Enter {id_field} to select: ").strip()
        for r in partial:
            if str(r.get(id_field, "")) == chosen:
                return r

        print("Invalid selection.")
        return None

    # Try fuzzy matching
    names = []
    for r in rows:
        if r.get("name"):
            names.append(r.get("name", ""))

    near = difflib.get_close_matches(q, names, n=5, cutoff=0.35)

    if not near:
        print("No close matches.")
        return None

    fuzzy = []
    for r in rows:
        if r.get("name") in near:
            fuzzy.append(r)

    cols = [id_field, "name"]
    for col in extra_display_columns:
        cols.append(col)

    display_table(fuzzy, cols)

    chosen = input(f"Enter {id_field} to select: ").strip()
    for r in fuzzy:
        if str(r.get(id_field, "")) == chosen:
            return r

    print("Invalid selection.")
    return None


def find_patient_by_id(pid):
    """Find patient by their ID"""
    patients = load_json_data(PATIENT_FILE)
    for p in patients:
        if str(p.get("patientID", "")) == str(pid):
            return p
    return None


def add_names_to_appointments(appts):
    """Add patient and doctor names to appointment records for display"""
    out = []
    for a in appts:
        a2 = dict(a)  # Make a copy

        p = find_patient_by_id(a.get("patientID"))
        d = doctor_exists_by_id(a.get("doctorID"))

        a2["patient_name"] = p.get("name", "") if p else ""
        a2["patient_phone"] = p.get("phone", "") if p else ""
        a2["doctor_name"] = d.get("name", "") if d else "(unassigned)"

        out.append(a2)

    return out


# ==============================
# PATIENT MANAGEMENT
# ==============================
def register_new_patient():
    """Register a new patient in the system"""
    name = get_valid_name("Enter patient full name: ").strip()
    dob = get_valid_birth_date("Enter date of birth: ")
    phone = get_valid_phone("Enter phone number: ")

    age = calculate_age_from_birthdate(dob)

    patients = load_json_data(PATIENT_FILE)

    # Check if patient already exists
    for p in patients:
        existing_name = p.get("name", "").strip().lower()
        existing_dob = p.get("dob")

        if existing_name == name.lower() and existing_dob == dob:
            print("Patient already exists (same name + DOB).")
            display_single_record(p)
            input("\nPress Enter to continue...")
            return

    pid = generate_next_id(PATIENT_FILE, "P", "patientID")

    rec = {
        "patientID": pid,
        "name": name,
        "dob": dob,
        "age": age,
        "phone": phone,
        "status": "active"
    }

    patients.append(rec)
    save_json_data(PATIENT_FILE, patients)

    print("\nPatient registered successfully!")
    display_single_record(rec)
    input("\nPress Enter to continue...")


def update_existing_patient():
    """Update an existing patient's information"""
    p = find_person_by_name(PATIENT_FILE, "patientID", extra_display_columns=("phone", "dob", "age"))

    if not p:
        input("\nPress Enter to continue...")
        return

    print("\nCurrent patient information:")
    display_single_record(p)
    print()

    new_name = get_valid_name("Enter updated name: ").strip()
    new_dob = get_valid_birth_date("Enter updated DOB: ")
    new_phone = get_valid_phone("Enter updated phone number: ")
    new_age = calculate_age_from_birthdate(new_dob)

    patients = load_json_data(PATIENT_FILE)

    for row in patients:
        if str(row.get("patientID")) == str(p.get("patientID")):
            row["name"] = new_name
            row["dob"] = new_dob
            row["age"] = new_age
            row["phone"] = new_phone

            save_json_data(PATIENT_FILE, patients)

            print("\nPatient updated successfully!")
            display_single_record(row)
            input("\nPress Enter to continue...")
            return

    print("Update failed.")
    input("\nPress Enter to continue...")


# ==============================
# APPOINTMENT MANAGEMENT (doctor REQUIRED)
# ==============================
def schedule_new_appointment():
    """Schedule a new appointment - requires selecting a doctor"""
    # Find the patient first
    patient = find_person_by_name(PATIENT_FILE, "patientID", extra_display_columns=("phone", "dob", "age"))

    if not patient:
        input("\nPress Enter to continue...")
        return

    # Select doctor by ID and verify they have doctor role
    doctor = select_doctor_by_id_show_all()
    if not doctor:
        input("\nPress Enter to continue...")
        return

    appt_date = get_future_date("Enter appointment date: ")
    appt_time = get_valid_time("Enter appointment time (HH:MM): ")

    # Check if doctor is available (2-hour window rule)
    ok, conflict = is_doctor_available(doctor["doctorID"], appt_date, appt_time)
    # Check if patient already has appointment at same date & time
    ok, conflict = is_patient_available(
        patient["patientID"], appt_date, appt_time
    )

    if not ok:
        print("\n❌ Patient already has an appointment at this date and time.")
        print("Conflicting appointment:")
        display_single_record(conflict)
        input("\nPress Enter to continue...")
        return


    if not ok:
        print("\n❌ Doctor is NOT available within 2 hours of that time.")
        print("Conflicting appointment:")
        display_single_record(conflict)
        input("\nPress Enter to continue...")
        return

    appts = load_json_data(APPT_FILE)
    aid = generate_next_id(APPT_FILE, "A", "aptID")

    rec = {
        "aptID": aid,
        "patientID": patient["patientID"],
        "doctorID": doctor["doctorID"],
        "date": appt_date,
        "time": appt_time,
        "status": "booked"  # Doctor will approve later
    }

    appts.append(rec)
    save_json_data(APPT_FILE, appts)

    print("\n✅ Appointment scheduled (status: Pending).")
    display_single_record(rec)
    input("\nPress Enter to continue...")


def reschedule_existing_appointment():
    """Reschedule an existing appointment"""
    apt_id = input("Enter appointment ID to reschedule (e.g., A1): ").strip()

    if not apt_id:
        return

    appts = load_json_data(APPT_FILE)

    target = None
    for a in appts:
        if str(a.get("aptID", "")) == apt_id:
            target = a
            break

    if not target:
        print("Appointment not found.")
        input("\nPress Enter to continue...")
        return

    # Re-check doctor is valid
    doc = doctor_exists_by_id(target.get("doctorID", ""))
    if not doc:
        print("❌ This appointment has an invalid doctorID (doctor not found in user.txt).")
        print("You must re-assign a doctor.")
        doc = select_doctor_by_id_show_all()
        if not doc:
            input("\nPress Enter to continue...")
            return
        target["doctorID"] = doc["doctorID"]

    print("\nCurrent appointment:")
    display_single_record(target)
    print()

    new_date = get_future_date("Enter new appointment date: ")
    new_time = get_valid_time("Enter new appointment time (HH:MM): ")

    # Check conflicts
    ok, conflict = is_doctor_available(target["doctorID"], new_date, new_time, exclude_apt_id=apt_id)
    # Check patient conflict
    ok, conflict = is_patient_available(
        target["patientID"], new_date, new_time, exclude_apt_id=apt_id
    )

    if not ok:
        print("\n❌ Patient already has another appointment at this date and time.")
        print("Conflicting appointment:")
        display_single_record(conflict)
        input("\nPress Enter to continue...")
        return


    if not ok:
        print("\n❌ Doctor is NOT available within 2 hours of that time.")
        print("Conflicting appointment:")
        display_single_record(conflict)
        input("\nPress Enter to continue...")
        return

    target["date"] = new_date
    target["time"] = new_time
    target["status"] = "Pending"  # Reset status

    save_json_data(APPT_FILE, appts)

    print("\n✅ Appointment rescheduled (status reset to Pending).")
    display_single_record(target)
    input("\nPress Enter to continue...")


def cancel_existing_appointment():
    """Cancel an existing appointment"""
    apt_id = input("Enter appointment ID to cancel (e.g., A1): ").strip()

    if not apt_id:
        return

    appts = load_json_data(APPT_FILE)

    target = None
    for a in appts:
        if str(a.get("aptID", "")) == apt_id:
            target = a
            break

    if not target:
        print("Appointment not found.")
        input("\nPress Enter to continue...")
        return

    target["status"] = "Cancelled"
    save_json_data(APPT_FILE, appts)

    print("\n✅ Appointment cancelled.")
    display_single_record(target)
    input("\nPress Enter to continue...")


# ==============================
# AUTO-ASSIGN DOCTORS ON THE DAY
# (for legacy appointments with doctorID="")
# ==============================
def auto_assign_doctors_for_today():
    """Automatically assign doctors to today's appointments that don't have one"""
    today_str = date.today().strftime("%Y-%m-%d")
    doctors = get_doctors_from_user_file()

    if not doctors:
        return  # No doctors available

    appts = load_json_data(APPT_FILE)
    changed = False

    for a in appts:
        # Only process today's appointments
        if a.get("date") != today_str:
            continue

        # Skip cancelled ones
        status = str(a.get("status", "")).lower()
        if status in ("cancelled", "canceled"):
            continue

        # Skip if already has doctor
        if str(a.get("doctorID", "")).strip():
            continue

        # Try to find an available doctor
        for d in doctors:
            ok, _ = is_doctor_available(d["doctorID"], a.get("date", ""), a.get("time", ""))
            if ok:
                a["doctorID"] = d["doctorID"]
                a["status"] = "Pending"
                changed = True
                break

    if changed:
        save_json_data(APPT_FILE, appts)


# ==============================
# VIEW & SEARCH
# ==============================
def view_appointments_for_date():
    """View all appointments for a specific date"""
    d = try_parse_date(input("Enter date to view appointments: ").strip())

    if not d:
        print("Invalid date.")
        input("\nPress Enter to continue...")
        return

    d_str = d.strftime("%Y-%m-%d")
    appts = load_json_data(APPT_FILE)

    rows = []
    for a in appts:
        if a.get("date") == d_str:
            rows.append(a)

    rows = add_names_to_appointments(rows)

    print(f"\nAppointments for {d_str}:")
    display_table(rows, ["aptID", "date", "time", "patientID", "patient_name", "patient_phone",
                         "doctorID", "doctor_name", "status"])
    input("\nPress Enter to continue...")


def view_all_appointments():
    """View all appointments in the system"""
    clear_screen()
    appts = load_json_data(APPT_FILE)
    appts = add_names_to_appointments(appts)

    print("=== ALL APPOINTMENTS ===\n")
    display_table(appts, ["aptID", "date", "time", "patientID", "patient_name", "patient_phone",
                          "doctorID", "doctor_name", "status"])
    input("\nPress Enter to go back...")


def search_and_view_patient_appointments():
    """Search for a patient and view their appointments"""
    patient = find_person_by_name(PATIENT_FILE, "patientID", extra_display_columns=("phone", "dob", "age"))

    if not patient:
        input("\nPress Enter to continue...")
        return

    appts = load_json_data(APPT_FILE)

    rows = []
    for a in appts:
        if a.get("patientID") == patient.get("patientID"):
            rows.append(a)

    rows = add_names_to_appointments(rows)

    patient_name = patient.get('name', '')
    print(f"\nAppointments for {patient_name}:")
    display_table(rows, ["aptID", "date", "time", "patientID", "patient_name",
                         "doctorID", "doctor_name", "status"])
    input("\nPress Enter to continue...")


# ==============================
# MENUS
# ==============================
def patient_management_menu():
    """Patient management submenu"""
    while True:
        clear_screen()
        print("=== Patient Management ===")
        print("1) Register new patient")
        print("2) Update existing patient information")
        print("0) Return")
        c = input("Select: ").strip()

        if c == "1":
            register_new_patient()
        elif c == "2":
            update_existing_patient()
        elif c == "0":
            return
        else:
            input("Invalid choice. Press Enter...")


def appointment_management_menu():
    """Appointment management submenu"""
    while True:
        clear_screen()
        print("=== Appointment Management ===")
        print("1) Schedule new appointment (doctor required)")
        print("2) Reschedule existing appointment")
        print("3) Cancel appointment")
        print("0) Return")
        c = input("Select: ").strip()

        if c == "1":
            schedule_new_appointment()
        elif c == "2":
            reschedule_existing_appointment()
        elif c == "3":
            cancel_existing_appointment()
        elif c == "0":
            return
        else:
            input("Invalid choice. Press Enter...")


def view_and_search_menu():
    """View and search submenu"""
    while True:
        clear_screen()
        print("=== View & Search ===")
        print("1) View appointments by date")
        print("2) Search patient and view appointments")
        print("3) View ALL appointments")
        print("0) Return")
        c = input("Select: ").strip()

        if c == "1":
            view_appointments_for_date()
        elif c == "2":
            search_and_view_patient_appointments()
        elif c == "3":
            view_all_appointments()
        elif c == "0":
            return
        else:
            input("Invalid choice. Press Enter...")


def receptionist_menu():
    """Main receptionist menu - entry point"""
    # Make sure all our data files exist
    ensure_data_file_exists(PATIENT_FILE)
    ensure_data_file_exists(USER_FILE)
    ensure_data_file_exists(APPT_FILE)

    while True:
        # Auto-assign doctors for today whenever menu loads
        auto_assign_doctors_for_today()

        clear_screen()
        print("=== Receptionist Management System ===")
        print("1) Patient Management")
        print("2) Appointment Management")
        print("3) View & Search")
        print("0) Exit")
        c = input("Select: ").strip()

        if c == "1":
            patient_management_menu()
        elif c == "2":
            appointment_management_menu()
        elif c == "3":
            view_and_search_menu()
        elif c == "0":
            print("Goodbye!")
            break
        else:
            input("Invalid choice. Press Enter...")


# Run the program
if __name__ == "__main__":
    receptionist_menu()