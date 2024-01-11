from rich.prompt import Prompt
from rich.panel import Panel
from meraki.exceptions import APIError
import meraki
from config import config
import sys
from logrr import lm
from funcs import read_csv_data, write_to_csv, check_serial_in_csv, extract_system_name, check_boat_in_csv, update_csv_row
import csv


class MerakiOps:
    """ Class that encapsulates all the Meraki operations"""
    def __init__(self):
        try:
            self.dashboard = meraki.DashboardAPI(api_key=config.MERAKI_API_KEY, suppress_logging=True)
        except Exception as e:
            lm.tsp(f"[bold red]Error initializing Meraki Dashboard: {e}[/bold red]")
            raise e

    def get_org_id(self):
        """
        Fetch the org ID based on org name, or prompt the user to select
        an organization if the name is left blank or is invalid. If there is only one
        organization, it selects that organization automatically. Exits the script if
        the organization is not found or if there's an error fetching the organizations.
        """

        with lm.console.status("[bold green]Fetching Meraki Organizations....", spinner="dots"):
            try:
                orgs = self.dashboard.organizations.getOrganizations()
            except APIError as e:
                lm.tsp(f"Failed to fetch organizations. Error: {e.message['errors'][0]}")
                sys.exit(1)

        lm.tsp("[bold bright_green]Connected to Meraki dashboard!")
        print(f"Found {len(orgs)} organization(s).")

        # If one org, return early
        if len(orgs) == 1:
            print(f"Working with Org: {orgs[0]['name']}\n")
            return orgs[0]["id"]
        org_names = [org["name"] for org in orgs]
        print("Available organizations:")
        for org in orgs:
            lm.tsp(f"- {org['name']}")
        lm.tsp("[bold red]\nNote: Meraki organization names are case sensitive")
        selection = Prompt.ask(
            "Which organization should we use?", choices=org_names, show_choices=False
        )
        organization_name = selection  # Update organization_name with the user's selection

        for org in orgs:
            if org["name"] == organization_name:
                return org["id"]

        lm.tsp(f"[bold red]Organization with name '{organization_name}' not found.[/bold red]")
        exit(1)

    def get_networks_in_org(self, org_id, product_type=None):
        """
        Collect existing Meraki network names / IDs
        """
        lm.tsp(Panel.fit("[bold bright_green]Retrieving Network(s) Information[/bold bright_green]", title="Step 3"))
        # Fetching the networks before applying any filter.
        try:
            response = self.dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
        except Exception as e:  # Handle exception for API call
            lm.tsp(f"[bold red]Failed to retrieve networks: {str(e)}[/bold red]")
            raise e

        # Filter networks by product type
        if product_type:
            response = [network for network in response if product_type in network['productTypes']]

        print(f"Found {len(response)} network(s).")
        return response

    """ NEW """

    def get_meraki_network_switches(self, network_id):
        response = self.dashboard.networks.getNetworkDevices(network_id)
        switch_List = []
        for device in response:
            if 'MS320' in device['model']:
                switch_List.append(device)
        return switch_List

    def get_meraki_switch_port_status(self, serial_number):
        response = self.dashboard.switch.getDeviceSwitchPortsStatuses(serial_number)

    def setup_meraki_network(self, ssid_number, meraki_network_id, psk, vlan):
        """
        Set up a Meraki network with the given SSID and VLAN.
        """
        self.change_ssid_status(ssid_number, meraki_network_id, True, psk, vlan)

    def teardown_meraki_network(self, ssid_number, meraki_network_id):
        """
        Tear down a Meraki network with the given SSID.
        """
        self.change_ssid_status(ssid_number, meraki_network_id, False)

    def change_ssid_status(self, ssid_number, meraki_network_id, status, psk=None, vlan=None):
        """
        Change the status of a specific SSID.
        """
        ssid_payload = {
            'name': f"{config.MERAKI_SSID_NAME}",
            'enabled': status,
            'authMode': "psk" if status else "open",
            'vlan': vlan if status else None,
            'encryptionMode': 'wpa'
        }
        # Include 'psk' only when enabling the SSID
        if status and psk is not None:
            ssid_payload['psk'] = psk

        try:
            self.dashboard.wireless.updateNetworkWirelessSsid(meraki_network_id, ssid_number, **ssid_payload)
            lm.tsp(f"[bright_green]Successfully {'enabled' if status else 'disabled'} SSID settings for {ssid_number}[/bright_green]")
        except Exception as e:
            lm.tsp(f"[red]Failed to {'enable' if status else 'disable'} SSID settings for {ssid_number}. Error: {e}[/red]")


    async def handle_webhook(self, data):
        lm.tsp("Webhook received:", style="webhook")
        lm.pp(data)  # pretty print received webhook

        device_serial = data.get("deviceSerial")
        alertTypeId = data.get("alertTypeId")
        networkId = data.get("networkId")
        port_number = data.get("alertData", {}).get('portNum', {})

        lm.tsp("Device Serial: ", device_serial)
        lm.tsp("Alert TypeId: ", alertTypeId)
        lm.tsp("Network Id: ", networkId)
        lm.tsp("PortNum: ", port_number)

        serial_found = check_serial_in_csv(device_serial)
        # alertTypeId = "port_connected"    # For testing
        if serial_found:
            lm.tsp(f"Serial found in CSV: {device_serial}")
            await self.process_alert(device_serial, alertTypeId, port_number)
        else:
            lm.tsp(f"Serial does not exist in CSV: {device_serial}")

    async def process_alert(self, device_serial, alert_type_id, port_number):
        csv_file_path = config.CSV_DB
        boats_csv_path = config.BOATS_CSV
        updated_rows, fieldnames = read_csv_data(csv_file_path)
        update_needed = False
        network_id = config.MERAKI_NETWORK_ID
        psk = config.PSK

        # FOR TESTING WITHOUT HAVING TO WAIT FOR MERAKI WEBHOOK TO COME THROUGH (5 min...)
        # TO USE COMMENT OUT LINES 169 (system_name = extract_system_name(response, port_number) & 170 (ssid_number, vlan = check_boat_in_csv(boats_csv_path, system_name)
        # alert_type_id = 'port_connected'    # SET TO 'port_connected' TO TEST WIFI NETWORK SETUP, 'port_disconnected' TO TEST NETWORK TEARDOWN
        # system_name = "SOME_SYSTEM_NAME"     # TO USE, COMMENT OUT LINE 166 "system_name = extract_system_name(response, port_number)"
        # ssid_number = 1
        # vlan = 10
        # TO USE WITH MERAKI WEBHOOK COMMENT OUT 158-161 and uncomment 169 & 170
        # MAKE SURE THE SERIAL NUMBERS YOU ARE USING FOR TESTING ARE IN data/ms_120_device_list.csv

        if alert_type_id == 'port_connected':
            response = self.dashboard.devices.getDeviceLldpCdp(device_serial)
            lm.tsp("LLDP CDP Response: ", response)

            system_name = extract_system_name(response, port_number)
            ssid_number, vlan = check_boat_in_csv(boats_csv_path, system_name)
            lm.tsp(f"Using system name:{system_name} \n"
                   f"Using ssid_number: {ssid_number} \n"
                   f"Using vlan: {vlan}")
            if system_name and ssid_number and vlan:
                update_csv_row(updated_rows, device_serial, switch_port_connected=True, system_name=system_name)
                self.setup_meraki_network(ssid_number=ssid_number, meraki_network_id=network_id, psk=psk, vlan=vlan)
                update_needed = True

        elif alert_type_id == 'port_disconnected':
            system_name = self.get_system_name_for_serial(updated_rows, device_serial)
            if system_name:
                ssid_number, vlan = check_boat_in_csv(boats_csv_path, system_name)
                if ssid_number:
                    self.teardown_meraki_network(ssid_number=ssid_number, meraki_network_id=network_id)
                    update_needed = True
            update_csv_row(updated_rows, device_serial, switch_port_connected=False, system_name="N/A")

        if update_needed:
            write_to_csv(csv_file_path, updated_rows, fieldnames)

    def get_system_name_for_serial(self, updated_rows, device_serial):
        """
        Retrieve system_name for the given device_serial from the updated_rows.
        """
        for row in updated_rows:
            if row["Serial Number"] == device_serial:
                return row.get("SystemName")
        return None
