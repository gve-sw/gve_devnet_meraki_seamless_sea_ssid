import csv
from rich.console import Console
from rich.panel import Panel
from config import config
import sys
import json
from logrr import lm


def read_csv_data(csv_file_path):
    with open(csv_file_path, mode='r', newline='') as file:
        reader = csv.DictReader(file)
        return list(reader), reader.fieldnames


def write_to_csv(csv_file_path, updated_rows, fieldnames):
    """
    Write updated data to the CSV file.

    :param csv_file_path: Path to the CSV file.
    :param updated_rows: List of updated rows to write.
    :param fieldnames: Fieldnames for the CSV file.
    """
    with open(csv_file_path, mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_rows)


def save_devices_to_csv(serial_numbers, ms_list):
    """
    Save selected device information to a CSV file using the write_to_csv function.

    :param serial_numbers: A list of serial numbers of the selected devices.
    :param ms_list: A list of all devices, each as a dictionary with "serial" and "model" keys.
    """
    headers = ["Serial Number", "Model", "switch_port_connected", "SystemName"]
    csv_file_path = config.CSV_DB

    # Prepare data to be written to CSV
    updated_rows = []
    for serial in serial_numbers:
        for device in ms_list:
            if device["serial"] == serial:
                updated_rows.append({
                    "Serial Number": device["serial"],
                    "Model": device["model"],
                    "switch_port_connected": False,  # Default to False
                    "SystemName": "N/A"  # Default to N/A
                })

    # Use write_to_csv function to write data
    write_to_csv(csv_file_path, updated_rows, headers)
    lm.tsp(f"Devices saved to {csv_file_path}")


def check_serial_in_csv(device_serial):
    """
    Check if a given device serial number exists in the CSV file.

    :param csv_file_path: Path to the CSV file.
    :param device_serial: The device serial number to search for.
    :return: True if the serial number is found in the CSV, False otherwise.
    """
    csv_file_path = config.CSV_DB
    try:
        with open(csv_file_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["Serial Number"] == device_serial:
                    return True
    except FileNotFoundError:
        print(f"CSV file not found at {csv_file_path}")

    return False


def update_csv_row(updated_rows, device_serial, switch_port_connected, system_name):
    for row in updated_rows:
        if row["Serial Number"] == device_serial:
            row["switch_port_connected"] = switch_port_connected
            row["SystemName"] = system_name
            break


def extract_system_name(response, port_number):
    """
    Extract the system name from the LLDP response for a specific port number.

    :param response: The LLDP/CDP response data.
    :param port_number: The port number to extract the system name from.
    :return: The system name if found, otherwise "N/A".
    """
    ports_data = response.get("ports", {})
    port_data = ports_data.get(str(port_number))

    if port_data and "lldp" in port_data:
        system_name = port_data["lldp"].get("systemName")
        if system_name:
            print(f"System name for port {port_number}: {system_name}")
            return system_name
    return "N/A"


def check_boat_in_csv(boats_csv_path, system_name):
    try:
        with open(boats_csv_path, mode="r", newline="") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["SystemName"] == system_name:
                    lm.tsp("System Name found in boats.csv", system_name)
                    return row["ssid_number"], row["vlan"]
    except FileNotFoundError:
        print(f"Boats CSV file not found at {boats_csv_path}")
    return None, None
