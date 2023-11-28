from rich.prompt import Prompt
from rich.panel import Panel
from meraki.exceptions import APIError
import meraki
from rich.console import Console
from config import Config
import sys
from funcs import find_boat_in_csv

console = Console()

# Constants; set in .env
MERAKI_API_KEY = Config.MERAKI_API_KEY
MERAKI_BASE_URL = Config.MERAKI_BASE_URL
MERAKI_SSID_NAME = Config.MERAKI_SSID_NAME


def get_meraki_dashboard():
    try:
        dashboard = meraki.DashboardAPI(api_key=Config.MERAKI_API_KEY, suppress_logging=False)
        return dashboard
    except Exception as e:
        console.print(f"[bold red]Error initializing Meraki Dashboard: {e}[/bold red]")
        sys.exit(1)


def get_org_id(dashboard):
    """
    Fetch the org ID based on org name, or prompt the user to select
    an organization if the name is left blank or is invalid. If there is only one
    organization, it selects that organization automatically. Exits the script if
    the organization is not found or if there's an error fetching the organizations.
    """

    with console.status("[bold green]Fetching Meraki Organizations....", spinner="dots"):
        try:
            orgs = dashboard.organizations.getOrganizations()
        except APIError as e:
            console.print(f"Failed to fetch organizations. Error: {e.message['errors'][0]}")
            sys.exit(1)

    console.print("[bold bright_green]Connected to Meraki dashboard!")
    print(f"Found {len(orgs)} organization(s).")

    # If one org, return early
    if len(orgs) == 1:
        print(f"Working with Org: {orgs[0]['name']}\n")
        return orgs[0]["id"]
    org_names = [org["name"] for org in orgs]
    print("Available organizations:")
    for org in orgs:
        console.print(f"- {org['name']}")
    console.print("[bold red]\nNote: Meraki organization names are case sensitive")
    selection = Prompt.ask(
        "Which organization should we use?", choices=org_names, show_choices=False
    )
    organization_name = selection  # Update organization_name with the user's selection

    for org in orgs:
        if org["name"] == organization_name:
            return org["id"]

    console.print(f"[bold red]Organization with name '{organization_name}' not found.[/bold red]")
    exit(1)


def get_networks_in_org(dashboard, org_id, product_type=None):
    """
    Collect existing Meraki network names / IDs
    """
    console.print(Panel.fit("[bold bright_green]Retrieving Network(s) Information[/bold bright_green]", title="Step 3"))
    # Fetching the networks before applying any filter.
    try:
        response = dashboard.organizations.getOrganizationNetworks(organizationId=org_id)
    except Exception as e:  # Handle exception for API call
        console.print(f"[bold red]Failed to retrieve networks: {str(e)}[/bold red]")
        sys.exit(1)

    if product_type:
        # Filter networks by product type
        response = [network for network in response if product_type in network['productTypes']]

    print(f"Found {len(response)} network(s).")
    return response


def setup_meraki_network(dashboard, ssid_number, meraki_network_id, psk, vlan):
    """
    Set up a Meraki network with the given SSID and VLAN.
    """
    change_ssid_status(dashboard, ssid_number, meraki_network_id, True, psk, vlan)


def teardown_meraki_network(dashboard, ssid_number, meraki_network_id, psk):
    """
    Tear down a Meraki network with the given SSID.
    """
    change_ssid_status(dashboard, ssid_number, meraki_network_id, False, psk)


def change_ssid_status(dashboard, ssid_number, meraki_network_id, status, psk=None, vlan=None):
    """
    Change the status of a specific SSID.
    """
    ssid_payload = {
        'name': f"{MERAKI_SSID_NAME}",
        'enabled': status,
        'authMode': "psk" if status else "open",
        'vlan': vlan if status else None
    }

    if status:
        ssid_payload['psk'] = psk
        ssid_payload['encryptionMode'] = 'wpa'  # or 'wpa2', depending on your requirements

    try:
        response = dashboard.wireless.updateNetworkWirelessSsid(meraki_network_id, ssid_number, **ssid_payload)
        console.print(f"[bright_green]Successfully {'enabled' if status else 'disabled'} SSID settings for {ssid_number}[/bright_green]")
    except Exception as e:
        console.print(f"[red]Failed to {'enable' if status else 'disable'} SSID settings for {ssid_number}. Error: {e}[/red]")


async def handle_webhook(dashboard, data):
    print("Webhook received:", data)

    # Extract MAC address and connection status from the webhook data
    mac_address = data.get('alertData', {}).get('mac')
    is_connected = data.get('alertData', {}).get('connected') == 'true'

    # is_connected = True       # For testing webhook. Uncomment to enable SSID, comment out to disable SSID.
    mac_address = "test_mac_address"  # For testing webhook. This should match CSV file. Won't need later.

    meraki_network_id = Config.MERAKI_NETWORK_ID  # using NETWORK_ID from .env
    psk = Config.MY_PSK

    print(f'Using Meraki network id: {meraki_network_id}')

    if mac_address:
        ssid_number, vlan = find_boat_in_csv(mac_address)
        print(f'SSID_NUMBER ME: {ssid_number}')
        print(f'VLAN {vlan}')
        if ssid_number and vlan:
            if is_connected:
                setup_meraki_network(dashboard, ssid_number, meraki_network_id, psk, vlan)
                return {"message": f"Network setup for MAC {mac_address}"}
            else:
                teardown_meraki_network(dashboard, ssid_number, meraki_network_id, psk)
                return {"message": f"Network teardown for MAC {mac_address}"}
        else:
            return {"message": f"No matching boat found for MAC address {mac_address}"}
    else:
        return {"message": "MAC address not found in webhook data"}
