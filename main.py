# main.py
import utils
import accountant
import receptionist
import doctor
import pharmacist
import os
import admin

##login
##current file path
current_path = os.path.dirname(os.path.abspath(__file__))
user_data = os.path.join(current_path, "data/user.txt")
#global record variable
current_user_record = {}

#login function
def login():
    """Authenticate user with max 3 attempts. Returns True/False."""
    records = utils.read_records(user_data)  # JSON returns list only

    if not records:
        print("User data file is empty or missing.")
        return False

    for attempt in range(3):
        if attempt > 0:
            print(f"Attempt {attempt+1} of 3.")

        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        # Find matching user (username OR email)
        user = next(
            (r for r in records
             if username.lower() in [r["username"].lower(), r.get("email", "").lower()]),
            None
        )

        # Password check
        if user and user["password"] == password:
            global current_user_record
            current_user_record = user
            print("Login successful!")
            return True

        print("Invalid username or password.\n")

    print("Invalid credentials. Access denied.")
    return False


#run..... of course we're going to run the main program
def main_menu():
    os.system('cls||clear')
    print("HealthPlus Management System")
    login_success = login()
    if login_success:
        role = current_user_record.get("role", "").lower()

        if role == "administrator":
            admin.admin_menu()
        elif role == "receptionist":
            receptionist.receptionist_menu()
        elif role == "doctor":
            doctor.doctor_menu()
        elif role == "accounts personnel":
            accountant.accountant_menu()
        elif role == "pharmacist":
            pharmacist.pharmacist_menu()
        else:
            print("You do not have permission to access the system.")

if __name__ == "__main__":
    while True:
        main_menu()
        restart = input("Do you want to login again? (yes/no): ")
        if restart.lower() == "yes":
            main_menu()
        if restart.lower() == "no":
            break
