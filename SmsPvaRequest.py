
import requests
import time
from collections import namedtuple

SmsResponse = namedtuple('SmsResponse', ['number', 'id', 'country_code'])

class SmsPvaRequest:
    def __init__(self, api_key, country):
        self.api_key = api_key
        self.country = country

    def get_sms_number(self):
        """Get an SMS number from the SMSPVA API."""
        while True:
            try:
                headers = {'apikey': self.api_key}
                url = f"https://api.smspva.com/activation/number/{self.country}/opt78"
                response = requests.get(url,headers=headers)


                if response.status_code == 200:
                    data = response.json()

                    if data.get("response") == "1":
                        number = data.get("number")
                        print("Got the number" + str(number))
                        id_ = data.get("id")
                        country_code = data.get("CountryCode")

                        return SmsResponse(number, id_, country_code)
                    else:
                        print(f"Bad response ({data.get('response')}). Retrying in 60 seconds...")
                        time.sleep(5)
                else:
                    print(f"Error: HTTP {response.status_code}")
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                time.sleep(5)

    def get_sms_message(self, id_, wait_sec):
        """Get the SMS message from the SMSPVA API using the ID returned by get_sms_number."""
        sms = None
        attempt = 0
        max_attempts = wait_sec // 3

        while sms is None and attempt < max_attempts:
            try:
                headers = {'partnerkey': self.api_key}
                url = f"https://api.smspva.com/activation/sms/{id_}"
                response = requests.get(url,headers=headers)

                if response.status_code == 200:
                    print("API response:", response.text)
                    data = response.json()

                    if data.get("response") == "1":
                        sms = data.get("sms")
                        break
                    else:
                        print(f"Waiting for SMS... Attempt {attempt + 1}")
                else:
                    print(f"Error: HTTP {response.status_code}")
                    break

                time.sleep(3)
                attempt += 1
            except Exception as e:
                print(f"Exception occurred: {str(e)}")
                break

        return sms


    def cancel_number(self, id_):
        url = f"https://smspva.com/priemnik.php?metod=ban&service=opt78&apikey={self.api_key}&id={id_}"
        response = requests.get(url)
        print(f"SmsPva cancel response: {response.text}")