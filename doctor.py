
#================================================================
#Imported stuff ya know? Pretty neat heh?
#================================================================

import datetime
from unittest import case
import utils
import os


#================================================================
#Zong taught me that I need to mention the path of the files before using them in the code...
#So here they are shining with their full glory!!!
#================================================================

current_path = os.path.dirname(os.path.abspath(__file__))

appointment = os.path.join(current_path, "data//appointment.txt")

medicine = os.path.join(current_path, "data//medicine.txt")

#================================================================
#Wrote it here incase I forget about it...
#================================================================

'''
- View assigned patient appointments.
- Record diagnosis and consultation notes.
- Generate consultation summary report.
'''

#================================================================
#the main menu for doctor(s) to find their task and navigate them
#================================================================

def doctor_menu():
    while True:
        print("\n--- Doctor Menu ---")
        print("1. View Patient Appointments")
        print("2. Prescription and Consultation Notes")
        print("3. Generate Consultation Summary Report")
        print("4. Exit")

        choice = input("\nEnter your choice: ")
        match choice:
            case "1":
                viewpatient()
            case "2":
                prescription_and_notes()
            case "3":
                generate_report()
            case "4":
                return
            case _:
                print("\n--- Invalid choice ----" )
                print("please input valid selection")

#================================================================
#This function is what i use to vew patient, there are two option.
#================================================================

def viewpatient():
    records = utils.read_records(appointment)
    print("\n--- Welcome To Patient Appointments ---")
    print("Select by specific date (y) or display all (n)")
    p = input('Would You Like To Select by Date? ').lower()
    match p:
        case 'y':
            while True:
                # assign the function output into a variable, which is a list
                date = datechecker()
                # checks if the date is inside the database or not
                fd = [r for r in records if r.get("date") == date]

                if not fd:
                    print('\n No records found on that day...')
                    exit = input("Do you want to continue? (y/n) ").lower()
                    match exit:
                        case 'n':
                            print('\n--- Returning to Menu ---')
                            return
                        case 'y':
                            print('\n Please reinput the date')
                            continue
                        case _:
                            print('\n Invalid Selection Inputted')
                            print('--- Returning to Menu ---')
                            return

                if fd:
                    break

            print('\n-- Displaying Record --')
            utils.pretty_print_records(fd)
            input('\n Press Enter to Continue...')
            return

        case 'n':
            print('\n-- Displaying all records --')
            utils.pretty_print_records(records)
            input('\n Press Enter to Continue...')
            return

        case _:
            print('\nInvalid Selection Inputted')
    return

#================================================================
#Got lazy to write so yee, vozo
#================================================================

def prescription_and_notes():

    check_medicine()

    while True:
        records = utils.read_records(appointment)
        ap = input("\nAppointment ID? ")

        fd = [r for r in records if r.get("aptID") == ap]

        if fd:
            break
        if not fd:
            print('\n No appointment found with that Identification...')
            c = input("Do you want to continue? (y/n) ").lower()
            match c:
                case 'y':
                    pass
                case 'n':
                    print('\n-- Returning to Menu ---')
                    return
        else:
            print("\n Invalid Input")
            c = input("Do you want to continue? (y/n) ").lower()
            match c:
                case 'y':
                    pass
                case 'n':
                    print('\n-- Returning to Menu ---')
                    return

    while True:
        print("\nHow to enter: M1, M2, M3")
        pres = input("Enter Medicine ID: ")

        sorted = [x.strip().upper() for x in pres.split(",")]

        invalid = [m for m in sorted if not valid_medicine_id(m)]

        if invalid:
            print("Invalid format for:", ", ".join(invalid))
        elif len(sorted) == 1:
            print("Single medicine selected:", sorted[0])
            break
        else:
            print("Multiple medicines selected:", sorted)
            break

    print("\nPlease write your note regarding the patient appointment")
    note = input("Enter Note: ")

    utils.update_record(appointment, ap, {"status": "consulted", "medicine": pres, "note": note})

    input("\nPress Enter to Continue...")

    return

def generate_report():

    apt = input("Appointment ID? ")

    if apt.startswith("A"):
        pass
    else:
        print("\nPlease Input valid ID Format. Example: A1")
        input("Press Enter to Continue...")

        return

    records = utils.read_records(appointment)

    fd = [r for r in records if r.get("aptID") == apt and r.get("status") in ("consulted", "paid", "completed")]
    selected = [r for r in records if r.get("aptID") == apt]

    if fd:
        print("\n--- Welcome To Report ---\n")
        print("Record found, Displaying Record Details\n")

        utils.pretty_print_records(selected, headers=["aptID", "note", "medicine"])

        input("\npress enter to continue...")

        return

    if not fd:
        print("\n The record your referring to is not eligible for this action, please provide the prescription and note")
        print("This action could be completed in the previous Menu.")
        input("Press Enter to Continue...")

        return

#Penting
def datechecker():
    while True:
        try:
            year = input("Enter year: ")
            if len(year) == 4 and int(year) >= 1900:

                break
            else:
                print('\nInvalid Year Inputted')
        except ValueError:
            print('\n Invalid Year Inputted')
    while True:
        try:
            month = input("Enter month: ")
            if len(month) == 2 and 0 < int(month) <= 12:

                break
            else:
                print('\nInvalid Month Inputted')
        except ValueError:
            print('\n Invalid Month Inputted')
    while True:
        try:
            day = input("Enter day: ")
            if len(day) == 2 and 0 < int(day) <= 31:

                break
            else:
                print('\nInvalid Day Inputted')
        except ValueError:
            print('\n Invalid Character(s) Inputted')
    date = f"{year}-{month}-{day}"
    return date

def check_medicine():
    record = utils.read_records(medicine)
    while True:
        w = input("\nWould like to view the list of medicine available? (y/n)").lower()
        match w:
            case "y":
                print("\nDisplaying Medicine\n")
                utils.pretty_print_records(record)
                input("\nPress Enter to Continue...")
                return
            case "n":
                print("\nContinuing...")
                return
            case _:
                print("\nInvalid Selection Inputted")
                print("Please enter a valid selection")
                input("Press Enter to Continue...")

def valid_medicine_id(value):
    return (
        len(value) >= 2 and
        value[0] == "M" and
        value[1:].isdigit()
    )

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")