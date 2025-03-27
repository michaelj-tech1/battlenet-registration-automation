import requests
import time
import re
from html import unescape


class Email:
    def __init__(self, api_key, email_pref):
        self.api_key = api_key
        self.email_pref = "gmx"

    def email_request(self):
        while True:
            try:
                url = f"https://api.kopeechka.store/mailbox-get-email?site=steam.com&mail_type={self.email_pref}&token={self.api_key}&password=1&regex=&subject=&investor=&soft=&type=json&api=2.0"
                response = requests.get(url)
                response.raise_for_status()
                response_data = response.json()
                print(response_data)
                if response_data.get("status") == "OK":
                    email = response_data.get("mail")
                    email_id = response_data.get("id")
                    password = response_data.get("password")

                    return {"email": email, "id": email_id, "password": password}

                time.sleep(5)
            except Exception as e:
                print(e)
                time.sleep(5)

    def get_steam_link(self, email_id, link_regex):
        max_attempts = 20
        for _ in range(max_attempts):
            try:
                url = f"https://api.kopeechka.store/mailbox-get-message?id={email_id}&token={self.api_key}&full=1&type=json&api=2.0"
                response = requests.get(url)
                response.raise_for_status()
                response_data = response.json()

                status = response_data.get("status")
                value = response_data.get("value", "")
                print(f"The status is: {status}, The value is: {value}")

                if status == "OK":
                    full_message = response_data.get("fullmessage", "")
                    print(f"Got ok response with full message: {full_message}")

                    decoded_message = unescape(full_message)
                    return self.extract_link(decoded_message, link_regex)

                elif status == "ERROR" and value == "WAIT_LINK":
                    print("Waiting for 5 seconds")
                    time.sleep(5)
                else:
                    break

            except Exception as e:
                print(f"Error: {e}")
                break

        return None

    def extract_link(self, html_text, link_regex):
        pattern = re.compile(link_regex)
        matcher = pattern.search(html_text)

        if matcher:
            return matcher.group()
        return None

    def cancel_mailbox(self, email_id):
        try:
            url = f"https://api.kopeechka.store/mailbox-cancel?id={email_id}&token={self.api_key}&type=json&api=2.0"
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()

            return response_data.get("status") == "OK"
        except Exception as e:
            print(f"Error in cancel_mailbox: {e}")
            return False

    def reorder_mailbox(self, email):
        try:
            url = f"https://api.kopeechka.store/mailbox-reorder?site=steam.com&email={email}&token={self.api_key}&password=0&subject=&regex=&type=json&api=2.0"
            response = requests.get(url)
            response.raise_for_status()
            response_data = response.json()

            if response_data.get("status") == "OK":
                return response_data.get("id")
            else:
                print("Error: Unexpected response status")
                return None

        except Exception as e:
            print(f"Error in reorder_mailbox: {e}")
            return None
