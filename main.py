# main.py
import utils
import admin
import os

##login
##current file path
current_path = os.path.dirname(os.path.abspath(__file__))
user_data = os.path.join(current_path, "data/user.txt")
#global record variable
current_user_record = {}

#login function
def login():
    records = utils.read_records(user_data)

    for attempt in range(3):
        if attempt > 0:
            print(f"Attempt {attempt+1} of 3.")

        username = input("Enter username: ").strip()
        password = input("Enter password: ").strip()

        user = next(
            (u for u in records
             if u.get("username") == username and u.get("password") == password),
            None
        )

        if user:
            global current_user
            current_user = {"userID": user["userID"]}
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
        user_id = current_user["userID"]
        user = utils.find_record(user_data, "and", {"userID": user_id})[0]
        role = user.get("role", "").lower()


        if role == "administrator":
            admin.admin_menu()
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
