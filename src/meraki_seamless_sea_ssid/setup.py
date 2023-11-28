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

from meraki_funcs import get_meraki_dashboard, get_org_id, get_networks_in_org
import os


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
    dashboard = get_meraki_dashboard()
    org_id = get_org_id(dashboard)

    if org_id:
        meraki_networks = get_networks_in_org(dashboard, org_id)
        if meraki_networks:
            # Display networks and let the user choose
            for index, network in enumerate(meraki_networks):
                print(f"{index + 1}. {network['name']} (ID: {network['id']})")

            while True:
                choice = input("Enter the number of the network you want to use: ")
                try:
                    choice_index = int(choice) - 1
                    if 0 <= choice_index < len(meraki_networks):
                        selected_network_id = meraki_networks[choice_index]['id']
                        save_network_id_to_env(selected_network_id)
                        break
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
