import os
import json
from rich.console import Console
from rich.table import Table

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    The EnvironmentManager class is responsible for loading and validating the necessary environment variables
    that the app relies on.

    Attributes:


    Methods:
        validate_env_variables() - Validates that all required environment variables are set,
                                   ignoring attributes related to the class internals or the os module.
    """

    # Construct the absolute path for dir
    dir_path = os.path.dirname(os.path.realpath(__file__))

    # Define mandatory environment variables
    MANDATORY_ENV_VARS = ['MERAKI_API_KEY', 'MERAKI_BASE_URL']

    # Construct the absolute path for boats.csv
    CSV_FILE = os.path.join(dir_path, '..', '..', 'data', 'boats.csv')

    MERAKI_API_KEY = os.getenv('MERAKI_API_KEY')
    MERAKI_BASE_URL = os.getenv('MERAKI_BASE_URL')
    MERAKI_NETWORK_ID = os.getenv('MERAKI_NETWORK_ID')

    LOGGER_LEVEL = os.getenv('LOGGER_LEVEL', '').upper() or 'DEBUG'
    MERAKI_SSID_NAME = os.getenv('MERAKI_SSID_NAME')
    MY_PSK = os.getenv('MY_PSK')

    APP_NAME = os.environ.get('APP_NAME') or "Update your APP_NAME in .env"

    # For Handling SOME_INTEGER with a default value and error check (for integer type).
    # try:
    #     SOME_INTEGER = int(os.getenv('SOME_INTEGER', '100'))  # Default to 100 seconds if left blank
    # except ValueError:
    #     TIMESPAN_IN_SECONDS = 100  # Default to 100 seconds if the provided value is invalid, so it won't break program.


    @classmethod
    def handle_error(cls, error_message):
        """Handles errors by printing an error message and exiting the program."""
        console = Console()
        console.print(f"[bold red]Error:[/bold red] {error_message}", highlight=False)
        exit(1)

    @classmethod
    def validate_env_variables(cls):
        missing_vars = []
        console = Console()  # Instantiate a console object for rich

        table = Table(title="Environment Variables")
        table.add_column("Variable", justify="left", style="bright_white", width=30)
        table.add_column("Value", style="bright_white", width=60)

        for var_name, var_value in cls.__dict__.items():
            if "os" in var_name or "__" in var_name or isinstance(var_value, classmethod) or var_name == 'MANDATORY_ENV_VARS':
                continue
            # Check if mandatory variables are set. if var_name in cls.MANDATORY_ENV_VARS and not var_value: Add variable to the table
            table.add_row(var_name, str(var_value) if var_value not in [None, ""] else "Not Set")
            if var_name in cls.MANDATORY_ENV_VARS and var_value in [None, ""]:
                missing_vars.append(var_name)

        # Display the table
        console.print(table)

        if missing_vars:
            cls.handle_error(f"The following environment variables are not set: {', '.join(missing_vars)}")
