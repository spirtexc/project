# utils.py
import os
# --- Read all records ---
import json
import os

# ------------------------------
# Read all records from JSON file
# ------------------------------
def read_records(source, headers=None):
    if not os.path.exists(source):
        return []  # File not created yet

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
# Helper: find ID key dynamically
# ------------------------------
def _get_id_key(record):
    for key in record:
        if key.lower().endswith("id"):
            return key
    return None

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
# Add a new record
# ------------------------------
def add_record(source, values):
    records = read_records(source)

    # Add new record
    records.append(values)

    # Save back to JSON file
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
        if record["id"] == record_id:
            for k, v in updates.items():
                if k in record:
                    record[k] = v
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
        id_key = _get_id_key(record)
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
