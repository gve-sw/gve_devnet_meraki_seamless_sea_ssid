# gve_devnet_meraki_seamless_sea_ssid
This project presents an advanced solution for automating Cisco Meraki Wi-Fi networks, specifically 
designed to facilitate seamless sea-to-dock roaming with dynamic VLAN management. It leverages the 
power of the Meraki Dashboard API to provide real-time network configuration adjustments based on 
device connectivity, ensuring optimal network performance and user experience in maritime environments.

## Contacts
* Mark Orszycki

## Solution Components
* Meraki MS
* Merak MR
* Meraki API
* Python
* FastAPI


## Prerequisites
#### Meraki API Keys
In order to use the Meraki API, you need to enable the API for your organization first. After enabling API access, 
you can generate an API key. Follow these instructions to enable API access and generate an API key:
1. Login to the Meraki dashboard
2. In the left-hand menu, navigate to `Organization > Settings > Dashboard API access`
3. Click on `Enable access to the Cisco Meraki Dashboard API`
4. Go to `My Profile > API access`
5. Under API access, click on `Generate API key`
6. Save the API key in a safe place. The API key will only be shown once for security purposes, so it is very important to take note of the key then. In case you lose the key, then you have to revoke the key and a generate a new key. Moreover, there is a limit of only two API keys per profile.

> For more information on how to generate an API key, please click [here](https://developer.cisco.com/meraki/api-v1/#!authorization/authorization). 

> Note: You can add your account as Full Organization Admin to your organizations by following the instructions [here](https://documentation.meraki.com/General_Administration/Managing_Dashboard_Access/Managing_Dashboard_Administrators_and_Permissions).


## Installation/Configuration
1. Clone this repository with `git clone https://github.com/gve-sw/gve_devnet_meraki_seamless_sea_ssid.git`.
2. Update .env with the following variables:
    ```script
    CSV_FILE = '/data/boats.csv'
    MERAKI_BASE_URL=https://api.meraki.com/api/v1/
    MERAKI_API_KEY=YOUR_MERAKI_API_KEY
    MERAKI_NETWORK_ID=YOUR_MERAKI_NETWORK_ID
    APP_NAME='Meraki Seamless Sea SSID'
    UVICORN_LOG_LEVEL=warning
    MY_PSK=YOUR_PSK
    MERAKI_SSID_NAME=YOUR_SSID_NAME
    ```
3. Retrieving your Meraki Network ID:
This project includes a setup.py script to assist in obtaining your Meraki Network ID. The script uses 
functions from meraki_funcs to interact with the Meraki API and save your network ID to the .env file.
To get your Network_ID, navigate to src/meraki_seamless_sea_ssid and run:
```script
python3 setup.py
```
Follow the prompts to select your organization and network.
The script will automatically update your .env file with the MERAKI_NETWORK_ID.

### Webhook Configuration
1. Run ngrok http 8000 to expose your local server.
2. Create a Webhook in the Meraki dashboard (Network-wide > Alerts > Webhooks).
3. Set the URL to your ngrok URL (ngrok_url/webhook). 
4. Configure alert settings to use the webhook for relevant events.

### boats.csv file
Input data for appropriately for each boat in boats.csv:
![/IMAGES/boats_csv.png](/IMAGES/boats_csv.png)<br>

## Usage
To run locally the program, use the command:
```script
uvicorn app:app --reload
```

To run locally the program & silence logs:
```script
uvicorn app:app --log-level warning
```

To run with Docker:
```script
docker-compose up
```

# Screenshots
Application Startup:
![/IMAGES/app_startup.png](/IMAGES/app_startup.png)<br>

Enabling SSID upon webhook:
![/IMAGES/enable_ssid.png](/IMAGES/enable_ssid.png)<br>

Disabling SSID upon webhook:
![/IMAGES/disable_ssid.png](/IMAGES/disable_ssid.png)<br><br>

![/IMAGES/0image.png](/IMAGES/0image.png)


### LICENSE

Provided under Cisco Sample Code License, for details see [LICENSE](LICENSE.md)

### CODE_OF_CONDUCT

Our code of conduct is available [here](CODE_OF_CONDUCT.md)

### CONTRIBUTING

See our contributing guidelines [here](CONTRIBUTING.md)

#### DISCLAIMER:
<b>Please note:</b> This script is meant for demo purposes only. All tools/ scripts in this repo are released for use "AS IS" without any warranties of any kind, including, but not limited to their installation, use, or performance. Any use of these scripts and tools is at your own risk. There is no guarantee that they have been through thorough testing in a comparable environment and we are not responsible for any damage or data loss incurred with their use.
You are responsible for reviewing and testing any scripts you run thoroughly before use in any non-testing environment.
