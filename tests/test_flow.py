import unittest
import os
import sys
import json
import shutil
from unittest.mock import patch
from datetime import date, datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import receptionist
import doctor
import accountant
import pharmacist
import utils

class TestEndToEndFlow(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Setup paths
        cls.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        cls.data_dir = os.path.join(cls.base_dir, "data")
        cls.backup_dir = os.path.join(cls.base_dir, "data_backup_test")
        
        # Backup existing data
        if os.path.exists(cls.data_dir):
            if os.path.exists(cls.backup_dir):
                shutil.rmtree(cls.backup_dir)
            shutil.copytree(cls.data_dir, cls.backup_dir)
            
    @classmethod
    def tearDownClass(cls):
        # Restore backup
        if os.path.exists(cls.backup_dir):
            if os.path.exists(cls.data_dir):
                shutil.rmtree(cls.data_dir)
            shutil.copytree(cls.backup_dir, cls.data_dir)
            shutil.rmtree(cls.backup_dir)

    def test_full_flow(self):
        print("\n\n=== STARTING END-TO-END FLOW TEST ===")
        
        # --- 1. RECEPTIONIST: Register Patient ---
        print("\n[Step 1] Registering Patient...")
        patient_name = "TestPatientFlow"
        dob = "1990-01-01"
        phone = "012-9999999"
        
        inputs = [patient_name, dob, phone, ""] # Name, DOB, Phone, Enter to continue
        with patch('builtins.input', side_effect=inputs):
            # We mock print to avoid cluttering output, but we might want to see errors
            receptionist.register_new_patient()
            
        # Verify Patient Created
        patients = utils.read_records(os.path.join(self.data_dir, "patient.txt"))
        patient = next((p for p in patients if p['name'] == patient_name), None)
        self.assertIsNotNone(patient, "Patient was not registered")
        patient_id = patient['patientID']
        print(f"✓ Patient registered: {patient_id}")

        # --- 2. RECEPTIONIST: Schedule Appointment ---
        print("\n[Step 2] Scheduling Appointment...")
        doctor_id = "D1" # Assuming D1 exists from user.txt view earlier
        future_date = (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")
        time = "10:00"
        
        # Inputs: Name Search -> Select ID -> Enter Doctor ID -> valid doctor or not (logic dependent)
        # Re-reading logic: 
        # schedule_new_appointment() -> find_person_by_name() -> input name -> input ID -> select_doctor_by_id_show_all() -> input Doc ID -> date -> time -> enter to continue
        
        inputs = [
            patient_name,      # Search name
            # patient_id,      # REMOVED: Exact match returns immediately, so no ID prompt!
            doctor_id,         # Select Doctor ID
            future_date,       # Date
            time,              # Time
            ""                 # Enter to continue
        ]
        
        with patch('builtins.input', side_effect=inputs):
            receptionist.schedule_new_appointment()
            
        # Verify Appointment Created
        appts = utils.read_records(os.path.join(self.data_dir, "appointment.txt"))
        appt = next((a for a in appts if a['patientID'] == patient_id and a['date'] == future_date), None)
        self.assertIsNotNone(appt, "Appointment was not scheduled")
        appt_id = appt['aptID']
        self.assertEqual(appt['status'], "booked")
        print(f"✓ Appointment scheduled: {appt_id}")

        # --- 3. DOCTOR: Consultation ---
        print("\n[Step 3] Doctor Consultation...")
        med_id = "M1" # Assuming M1 exists
        note = "Patient has flu"
        
        # prescription_and_notes() inputs:
        # check_medicine() -> 'n' (no view)
        # Loop for Appt ID -> appt_id
        # Loop for Med ID -> med_id
        # Note -> note
        # Enter to continue
        
        inputs = [
            'n',        # View medicine? No
            appt_id,    # Appt ID
            med_id,     # Med ID
            note,       # Note
            ""          # Enter to continue
        ]
        
        with patch('builtins.input', side_effect=inputs):
            doctor.prescription_and_notes()
            
        # Verify Consultation
        appts = utils.read_records(os.path.join(self.data_dir, "appointment.txt"))
        appt = next((a for a in appts if a['aptID'] == appt_id), None)
        self.assertEqual(appt['status'], "consulted")
        self.assertEqual(appt['medicine'], med_id)
        self.assertEqual(appt['note'], note)
        print(f"✓ Consultation done. Status: {appt['status']}")

        # --- 4. ACCOUNTANT: Payment ---
        print("\n[Step 4] Accountant Payment...")
        consult_fee = "50"
        
        # calculate_patient_bill() inputs:
        # Appt ID -> appt_id
        # Consult Price -> 50
        # Record bill? -> yes
        
        inputs = [
            appt_id,
            consult_fee,
            "yes"
        ]
        
        with patch('builtins.input', side_effect=inputs):
            accountant.calculate_patient_bill()
            
        # Verify Payment
        appts = utils.read_records(os.path.join(self.data_dir, "appointment.txt"))
        appt = next((a for a in appts if a['aptID'] == appt_id), None)
        self.assertEqual(appt['status'], "paid")
        
        # Verify Income Record
        incomes = utils.read_records(os.path.join(self.data_dir, "income.txt"))
        bill = next((b for b in incomes if b.get('appointmentID') == appt_id), None)
        self.assertIsNotNone(bill, "Bill not created")
        self.assertEqual(bill['status'], "paid")
        print(f"✓ Payment processed. Status: {appt['status']}")

        # --- 5. PHARMACIST: Dispense ---
        print("\n[Step 5] Pharmacist Dispense...")
        
        # Get initial stock of M1
        meds_before = utils.read_records(os.path.join(self.data_dir, "medicine.txt"))
        m1_before = next((m for m in meds_before if m['medID'] == med_id), None)
        stock_before = int(m1_before['stock'])
        print(f"  Stock before: {stock_before}")
        
        # print_medication_list() inputs:
        # Appt ID -> appt_id
        # Confirm -> y
        
        inputs = [
            appt_id,
            "y"
        ]
        
        with patch('builtins.input', side_effect=inputs):
            pharmacist.print_medication_list()
            
        # Verify Completed Status
        appts = utils.read_records(os.path.join(self.data_dir, "appointment.txt"))
        appt = next((a for a in appts if a['aptID'] == appt_id), None)
        self.assertEqual(appt['status'], "completed")
        print(f"✓ Appointment completed. Status: {appt['status']}")
        
        # --- 6. VERIFY STOCK DEDUCTION ---
        print("\n[Step 6] Verifying Stock Deduction...")
        meds_after = utils.read_records(os.path.join(self.data_dir, "medicine.txt"))
        m1_after = next((m for m in meds_after if m['medID'] == med_id), None)
        stock_after = int(m1_after['stock'])
        print(f"  Stock after: {stock_after}")
        
        if stock_after == stock_before:
             print("❌ FAIL: Stock was NOT deducted!")
        else:
             print("✓ PASS: Stock was deducted.")

        self.assertLess(stock_after, stock_before, "Stock should be deducted after dispensing!")

if __name__ == '__main__':
    unittest.main()
