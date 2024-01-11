"""
Copyright (c) 2023 Cisco and/or its affiliates.
This software is licensed to you under the terms of the Cisco Sample
Code License, Version 1.1 (the "License"). You may obtain a copy of the
License at
               https://developer.cisco.com/docs/licenses
All use of the material herein must be in accordance with the terms of
the License. All rights not expressly granted by the License are
reserved. Unless required by applicable law or agreed to separately in
writing, software distributed under the License is distributed on an "AS
IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
or implied.
"""

# from meraki_funcs import get_meraki_dashboard, get_org_id, get_networks_in_org, get_meraki_network_switches
from meraki_funcs import MerakiOps
from funcs import save_devices_to_csv
import os
from logrr import lm
import json


def save_network_id_to_env(network_id):
    # Path to the .env file located two directories up
    env_file = os.path.join('..', '..', '.env')

    # Read the existing content of the .env file
    if os.path.exists(env_file):
        with open(env_file, 'r') as file:
            lines = file.readlines()

        # Update or add the MERAKI_NETWORK_ID variable
        updated = False
        for i, line in enumerate(lines):
            if line.startswith('MERAKI_NETWORK_ID='):
                lines[i] = f'MERAKI_NETWORK_ID={network_id}\n'
                updated = True
                break

        if not updated:
            lines.append(f'MERAKI_NETWORK_ID={network_id}\n')

        # Write the updated content back to the .env file
        with open(env_file, 'w') as file:
            file.writelines(lines)
    else:
        # If the .env file doesn't exist, create it with the network ID
        with open(env_file, 'w') as file:
            file.write(f'MERAKI_NETWORK_ID={network_id}\n')

    print(f"Network ID saved to {env_file}: {network_id}")


def main():
    meraki_ops = MerakiOps()
    # dashboard = get_meraki_dashboard()
    # org_id = get_org_id(dashboard)
    org_id = meraki_ops.get_org_id()

    if org_id:
        meraki_networks = meraki_ops.get_networks_in_org(org_id)
        if meraki_networks:
            # Display networks and let the user choose
            for index, network in enumerate(meraki_networks):
                print(f"{index + 1}. {network['name']} (ID: {network['id']})")

            while True:
                network_choice = input("Enter the number of the network you want to use: ")
                try:
                    network_choice_index = int(network_choice) - 1
                    if 0 <= network_choice_index < len(meraki_networks):
                        selected_network_id = meraki_networks[network_choice_index]['id']
                        save_network_id_to_env(selected_network_id)
                        ms_list = meraki_ops.get_meraki_network_switches(selected_network_id)
                        lm.tsp(ms_list)
                        if ms_list:
                            # Display devices in network and let the user choose
                            for index, device in enumerate(ms_list):
                                print(f"{index + 1}. {device['model']} (Serial Number: {device['serial']})")

                            while True:
                                device_choices = input("Enter the number(s) of the device(s) you want to use (comma-separated): ")
                                try:
                                    choice_indices = [int(choice.strip()) - 1 for choice in device_choices.split(',')]
                                    if all(0 <= idx < len(ms_list) for idx in choice_indices):
                                        selected_devices = [ms_list[idx]['serial'] for idx in choice_indices]
                                        print(f"Selected devices: {selected_devices}")
                                        save_devices_to_csv(selected_devices, ms_list)
                                        break
                                    else:
                                        print("Invalid selection. Please enter numbers from the list, separated by commas.")
                                except ValueError:
                                    print("Invalid input. Please enter numeric values, separated by commas.")
                            break
                        else:
                            print("No devices found in the selected network.")
                    else:
                        print("Invalid selection. Please enter a number from the list.")
                except ValueError:
                    print("Invalid input. Please enter a numeric value.")
        else:
            print("No networks found.")
    else:
        print("Organization ID not found.")


if __name__ == "__main__":
    main()
