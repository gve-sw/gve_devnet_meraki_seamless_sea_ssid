import os
import json
import pathlib
from dotenv import load_dotenv
from pydantic import field_validator, model_validator, validator, root_validator
from pydantic_settings import BaseSettings
from typing import Optional, ClassVar, List, Dict, Any
import re

# Adjust the path to load the .env file from the project root.
env_path = pathlib.Path(__file__).parents[2] / '.env'
print(f'env path: {env_path}')  # for debugging
load_dotenv(dotenv_path=env_path)

load_dotenv()


class Config(BaseSettings):
    """
    The EnvironmentManager class is responsible for loading and validating the necessary environment variables
    that the app relies on.

    Attributes:


    Methods:
        validate_env_variables() - Validates that all required environment variables are set,
                                   ignoring attributes related to the class internals or the os module.
    """

    # Construct the absolute path for dir
    DIR_PATH: ClassVar[pathlib.Path] = pathlib.Path(__file__).parents[2]
    ENV_FILE_PATH: ClassVar[str] = str(DIR_PATH / ".env")
    BOATS_CSV: ClassVar[str] = str(DIR_PATH / "data" / "boats.csv")     # Construct the absolute path for boats.csv
    CSV_DB: ClassVar[str] = str(DIR_PATH / "data" / "ms_120_device_list.csv")     # Construct the absolute path for boats.csv
    BOAT_NAMES: ClassVar[str] = str(DIR_PATH / "data" / "test.csv")

    # Meraki Integration settings
    MERAKI_API_KEY: str
    MERAKI_BASE_URL: str
    MERAKI_NETWORK_ID: str
    PSK: str
    MERAKI_SSID_NAME: str

    # FastAPI Settings
    APP_NAME: Optional[str] = 'Update your app name in .env'
    APP_VERSION: Optional[str] = 'Update your ap'
    DEV_ENV: Optional[str] = 'development'
    IS_PRODUCTION: bool = DEV_ENV.lower() == 'production'  # True if FLASK_ENV is "production," otherwise False
    LOGGER_LEVEL: str = 'DEBUG'

    _instance: ClassVar[Optional['Config']] = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @field_validator('MERAKI_BASE_URL', mode='before')
    def validate_meraki_base_url(cls, v):
        if not re.match(r'https://api.meraki\.com/api/v1', v):
            raise ValueError('WEBEX_BASE_URL must be: https://api.meraki.com/api/v1/')
        return v

    @field_validator('MERAKI_API_KEY', mode='before')
    def validate_api_key(cls, v):
        if not v:
            raise ValueError('MREAKI_API_KEY must not be empty')
        return v


config = Config.get_instance()
