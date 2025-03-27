
import requests
import time

class SmsHubAPI:
    BASE_URL = "https://smshub.org/stubs/handler_api.php"

    def __init__(self, api_key, country):
        self.api_key = api_key
        self.country = country

    def get_number(self):
        operator = "any"
        request_url = f"{self.BASE_URL}?api_key={self.api_key}&action=getNumber&service=bz&operator={operator}&country={self.country}"
        response = requests.get(request_url)
        print("The response from smshub: " + str(response.text))

        if response.text.strip() == "API_KEY_NOT_VALID":
            raise Exception("The provided API key is not valid.")

        if response.text.strip() == "NO_NUMBERS":
            raise Exception("There are currently no available numbers.")

        split_response = response.text.split(":")
        if len(split_response) >= 3 and split_response[0] == "ACCESS_NUMBER":
            id_ = split_response[1]
            phone_number = f"+{split_response[2]}"
            return id_, phone_number
        else:
            raise Exception(f"Unexpected response from SmsHub: {response.text}")

    def get_sms_code(self, id_, wait_sec):
        request_url = f"{self.BASE_URL}?api_key={self.api_key}&action=getStatus&id={id_}"
        attempt = 0
        max_attempts = wait_sec // 3

        while attempt < max_attempts:
            response = requests.get(request_url)
            result = response.text.strip()
            print("Result for sms hub" + str(result))
            if result.startswith("STATUS_OK:"):
                print("Got SMS code")
                return result.split(":")[1]

            elif result == "STATUS_WAIT_CODE":
                print("Waiting on SMS code...")
                time.sleep(3)
                attempt += 1

            else:
                raise Exception(f"Unexpected response from SmsHub: {result}")

        return None


    def cancel_number(self, id_):
        url = f"https://smshub.org/stubs/handler_api.php?api_key={self.api_key}&action=setStatus&status=8&id={id_}"
        response = requests.get(url)
        print(f"SmsHub cancel response: {response.text}")