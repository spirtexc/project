# utils.py
import os
import json

# ------------------------------
# Read all records from JSON file
# ------------------------------
def read_records(source, headers=None):
    if not os.path.exists(source):
        return [] 
    #read records from JSON file
    with open(source, "r") as file:
        try:
            records = json.load(file)
        except json.JSONDecodeError:
            return []  # Empty or corrupt JSON file

    # If no headers specified, return all records
    if not headers:
        return records

    result = []
    for record in records:
        result.append({h: record.get(h, "") for h in headers})
    
    return result



# ------------------------------
# Find record by any field
# ------------------------------
def find_record(source, mode, filters):
    records = read_records(source)
    mode = mode.lower()

    result = []

    for record in records:
        # Convert record to lowercase strings for comparison
        matches = [
            str(record.get(key, "")).lower() == str(value).lower()
            for key, value in filters.items()
        ]

        if mode == "and":
            if all(matches):
                result.append(record)

        elif mode == "or":
            if any(matches):
                result.append(record)

        else:
            raise ValueError("Mode must be 'and' or 'or'.")
    return result
# ------------------------------
# saperate ID into prefix and number
# ------------------------------
def split_id(value):
    prefix = ""
    number = ""

    for ch in value:
        if ch.isalpha():
            prefix += ch
        elif ch.isdigit():
            number += ch

    return prefix, int(number) if number else 0

# ------------------------------
# Get ID key based on source file
# ------------------------------
def next_id(source):
    records = read_records(source)
    if not records:
        return None, None

    # detect ID key (ends with ID)
    id_key = None
    for key in records[0]:
        if key.lower().endswith("id"):
            id_key = key
            break

    if not id_key:
        return None, None

    max_num = 0
    prefix = ""

    for record in records:
        pid, num = split_id(record.get(id_key, ""))
        prefix = pid
        max_num = max(max_num, num)

    return id_key, f"{prefix}{max_num + 1}"



# ------------------------------
# Add a new record
# ------------------------------
def add_record(source, value):
    records = read_records(source)
    # Generate new ID
    id_key, new_id = next_id(source)
    if id_key and new_id:
        value[id_key] = new_id
    # Append new record
    records.append(value)

    with open(source, "w") as file:
        json.dump(records, file, indent=4)

    print("Record added successfully!")



# ------------------------------
# Update a record by ID
# ------------------------------
def update_record(source, record_id, updates):
    records = read_records(source)
    updated = False

    for record in records:
        id_key = next((k for k in record if k.lower().endswith("id")), None)
        if id_key and record.get(id_key) == record_id:
            record.update(updates)
            updated = True
            break
    if updated:
        with open(source, "w") as file:
            json.dump(records, file, indent=4)
        print("Record updated successfully!")
    else:
        print("Record not found!")
        


# ------------------------------
# Delete record by ID
# ------------------------------
def delete_record(source, record_id):
    records = read_records(source)

    new_records = []
    deleted = False

    for record in records:
        id_key = next((k for k in record if k.lower().endswith("id")), None)
        if id_key and record.get(id_key) == record_id:
            deleted = True
            continue
        new_records.append(record)

    if deleted:
        with open(source, "w") as file:
            json.dump(new_records, file, indent=4)
        print("Record deleted successfully!")
    else:
        print("Record not found!")



#Pretty print section
#Pretty print a single record in a box
def pretty_print_box(record):
    # Find the longest key for alignment
    max_key_length = max(len(key) for key in record.keys())
    # Calculate box width
    max_value_length = max(len(str(value)) for value in record.values())
    box_width = max(max_key_length + max_value_length + 3, 40)
    # Print top border
    print("┌" + "─" * box_width + "┐")
    # Print each field
    for key, value in record.items():
        key_str = key.ljust(max_key_length)
        value_str = str(value)
        padding = box_width - len(key_str) - len(value_str) - 3
        print(f"│ {key_str} : {value_str}{' ' * padding} │")
    # Print bottom border
    print("└" + "─" * box_width + "┘")

#Pretty print multiple records in a formatted table style
def pretty_print_records(records, headers=None):
    if not records:
        print("No records to display.")
        return
    if headers is None:
        headers = list(records[0].keys())
    # Calculate the maximum width needed for each column
    col_widths = {}
    for header in headers:
        # Start with header length
        max_width = len(header)
        # Check all records for longest values
        for record in records:
            value_len = len(str(record.get(header, "")))
            max_width = max(max_width, value_len)
        col_widths[header] = max_width
    # Print header row
    header_row = " | ".join(header.ljust(col_widths[header]) for header in headers)
    separator = "-+-".join("-" * col_widths[header] for header in headers)

    print(header_row)
    print(separator)

    # Print data rows
    for record in records:
        data_row = " | ".join(str(record.get(header, "")).ljust(col_widths[header]) for header in headers)
        print(data_row)
