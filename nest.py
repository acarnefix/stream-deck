import json
import os

from dotenv import load_dotenv
import requests


load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
REDIRECT_URI = os.getenv("REDIRECT_URI")
PROJECT_ID = os.getenv("PROJECT_ID")
DEVICE_NAME = os.getenv("DEVICE_NAME")
AUTH_URL = "https://www.googleapis.com/oauth2/v4/token"
DEVICE_API_URL = "https://smartdevicemanagement.googleapis.com/v1"
DEVICE_URL = f"{DEVICE_API_URL}/{DEVICE_NAME}"
BASE_PARAMS = {
    "client_id": CLIENT_ID,
    "client_secret": "eVxaBhS0mN_lKVOtPVJI_ma9",
}



def print_login_url():
    print(
        f"https://nestservices.google.com/partnerconnections/{PROJECT_ID}/auth?redirect_uri={REDIRECT_URI}"
        f"&access_type=offline&prompt=consent&client_id={CLIENT_ID}&response_type=code"
        f"&scope=https://www.googleapis.com/auth/sdm.service"
    )


def get_tokens():
    token_params = dict(
        {
            "code": os.getenv("CODE"),
            "grant_type": "authorization_code",
            "redirect_uri": REDIRECT_URI,
        },
        **BASE_PARAMS,
    )
    response_json = requests.post(AUTH_URL, params=token_params).json()
    access_token = f"{response_json['token_type']} {response_json['access_token']}"
    refresh_token = response_json["refresh_token"]
    return access_token, refresh_token


def refresh_access_token():
    refresh_params = dict(
        {
            "refresh_token": os.getenv("REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        },
        **BASE_PARAMS,
    )
    response_json = requests.post(AUTH_URL, params=refresh_params).json()
    return f"{response_json['token_type']} {response_json['access_token']}"


def request_headers():
    return {"Content-Type": "application/json", "Authorization": refresh_access_token()}


def get_device_name():
    url_get_devices = f"{DEVICE_API_URL}/enterprises/{PROJECT_ID}/devices"
    response_json = requests.get(url_get_devices, headers=request_headers()).json()
    return response_json["devices"][0]["name"]


def get_current_temperature():
    response_json = requests.get(DEVICE_URL, headers=request_headers()).json()
    return response_json["traits"]["sdm.devices.traits.Temperature"]["ambientTemperatureCelsius"]


def get_current_set_temperature():
    response_json = requests.get(DEVICE_URL, headers=request_headers()).json()
    return response_json["traits"]["sdm.devices.traits.ThermostatTemperatureSetpoint"]["coolCelsius"]


def execute_command(command_name, params):
    url_set_mode = f"{DEVICE_URL}:executeCommand"
    data = json.dumps({"command": f"sdm.devices.commands.{command_name}", "params": params})
    response = requests.post(url_set_mode, headers=request_headers(), data=data)
    print(response)


def set_new_temperature(increment):
    execute_command(
        "ThermostatTemperatureSetpoint.SetCool",
        params={"coolCelsius": get_current_set_temperature() + increment}
    )


def set_fan_time(minutes):
    execute_command("Fan.SetTimer", params={"timerMode": "ON", "duration": f"{minutes*60}s"})
