import csv
from rich.console import Console
from rich.panel import Panel
from config import Config
import sys

# Constants; set in .env
CSV_FILE = Config.CSV_FILE

# Rich console
console = Console()


def signal_handler(sig, frame):
    # Implement any clean-up tasks that may be necessary, i.e. closing files or database connections.
    print_exit_panel()
    sys.exit(0)  # Exit the app gracefully


def print_start_panel(app_name=Config.APP_NAME):
    console.print(Panel.fit(f"[bold bright_green]{app_name}[/bold bright_green]"))


def print_exit_panel():
    console.print("\n")
    console.print(Panel.fit("Shutting down...", title="[bright_red]Exit[/bright_red]"))


def find_boat_in_csv(mac_address):
    with open(CSV_FILE, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['mac_address'] == mac_address:
                return row['ssid_number'], row['vlan']
    return None, None


