
import requests
import time


class FiveSimAPI:
    BASE_URL = "https://5sim.net/v1"

    def __init__(self, api_key):
        self.api_key = api_key

    def get_number_and_country_code(self, country, operator):
        product = "blizzard"
        request_url = f"{self.BASE_URL}/user/buy/activation/{country}/{operator}/{product}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json"
        }
        response = requests.get(request_url, headers=headers)
        if response.status_code != 200:
            raise RuntimeError(f"HTTP GET Request Failed with Error code: {response.status_code}")

        response_json = response.json()
        phone_number = response_json["phone"]
        id_ = response_json["id"]

        return [phone_number, id_]

    def get_sms_code(self, id_, wait_sec):
        sms_code = None
        interval = 3
        max_attempts = wait_sec // interval

        attempt = 0
        while sms_code is None and attempt < max_attempts:
            request_url = f"{self.BASE_URL}/user/check/{id_}"
            headers = {
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.get(request_url, headers=headers)
            if response.status_code != 200:
                raise RuntimeError(f"HTTP GET Request Failed with Error code: {response.status_code}")

            response_json = response.json()
            if response_json["status"] == "RECEIVED":
                sms_data = response_json.get("sms", [])
                if sms_data and isinstance(sms_data, list) and len(sms_data) > 0:
                    sms_code = sms_data[0]["code"]
                    break
            time.sleep(interval)
            attempt += 1

        return sms_code

    def cancel_number(self, id_):
        url = f"https://5sim.net/v1/user/cancel/{id_}"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        print(f"5sim cancel response: {response.text}")

