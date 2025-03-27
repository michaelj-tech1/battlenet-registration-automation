import requests
import json
from threading import Thread

class BalanceFetcher:

    def __init__(self, ui):
        self.ui = ui

    BASE_URL_KOPEECHKA = "https://api.kopeechka.store/user-balance"
    BASE_URL_CAPSOLVER = "https://bcsapi.xyz/api/user/balance?access_token="
    BASE_URL_SMSPVA = "https://smspva.com/priemnik.php"
    BASE_URL_SMSHUB = "https://smshub.org/stubs/handler_api.php"
    BASE_URL_5SIM = "https://5sim.net/v1/user/profile"

    def fetch_all_balances(self):
        thread = Thread(target=self._fetch_balances_thread)
        thread.start()

    def _fetch_balances_thread(self):
        try:
            self.update_kopeechka_balance(self.fetch_kopeechka_balance())
            self.update_capsolver_balance(self.fetch_captcha_balance())
            self.update_smspva_balance(self.fetch_smspva_balance())
            self.update_smshub_balance(self.fetch_smshub_balance())
            self.update_5sim_balance(self.fetch_5sim_balance())
        except json.JSONDecodeError as e:
            print(f"Failed to fetch or parse balance: {e}")

    def fetch_kopeechka_balance(self):
        api_token = self.ui.txtKopeechkaApiKey.text().strip()
        print(f"Kopeechka API Token: {api_token}")
        url = f"{self.BASE_URL_KOPEECHKA}?token={api_token}&cost=USD&type=json&api=2.0"
        response = self.execute_request(url)
        return self.parse_balance(response, "balance")

    def fetch_captcha_balance(self):
        api_key = self.ui.txtCaptchaApiKey.text().strip()

        bcs_url = self.BASE_URL_CAPSOLVER + api_key
        bcs_response = self.execute_request(bcs_url)
        bcs_balance = self.parse_balance(bcs_response, "balance")

        if bcs_balance != "0.00":
            return bcs_balance


        captcha_url = "https://api.2captcha.com/getBalance"
        captcha_payload = {"clientKey": api_key}
        captcha_response = self.execute_post_request(captcha_url, captcha_payload)
        captcha_balance = self.parse_balance(captcha_response, "balance")

        if captcha_balance != "0.00":
            return captcha_balance

        return "0.00"

    def fetch_smspva_balance(self):
        api_key = self.ui.txtApiKey.text().strip()
        print(f"SMSPVA API Key: {api_key}")
        url = f"{self.BASE_URL_SMSPVA}?apikey={api_key}&service=opt4&metod=get_userinfo&method=get_userinfo"
        response = self.execute_request(url)
        return self.parse_balance(response, "balance")

    def fetch_smshub_balance(self):
        api_key = self.ui.txtApiKey.text().strip()
        print(f"SMSHUB API Key: {api_key}")
        url = f"{self.BASE_URL_SMSHUB}?api_key={api_key}&action=getBalance"
        response = self.execute_request_text(url)
        return self.parse_smshub_balance(response)

    def fetch_5sim_balance(self):
        api_key = self.ui.txtApiKey.text().strip()
        print(f"5SIM API Key: {api_key}")
        url = self.BASE_URL_5SIM
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        response = self.execute_request(url, headers)
        return self.parse_balance(response, "balance")


    def execute_request(self, url, headers=None):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network or request error: {e}")
            return {}

    def execute_post_request(self, url, json_payload):
        """Executes a POST request with a JSON payload."""
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, json=json_payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Network or request error: {e}")
            return {}

    def execute_request_text(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Network or request error: {e}")
            return "ACCESS_BALANCE:0.00"

    def parse_balance(self, response, key):
        try:
            if key in response:
                balance = float(response[key])
                return f"{balance:.2f}"
            else:
                print(f"Key '{key}' not found in the response.")
        except (json.JSONDecodeError, KeyError, ValueError):
            print(f"Error parsing the balance for key: {key}")
        return "0.00"

    def parse_smshub_balance(self, response_text):
        if response_text.startswith("ACCESS_BALANCE:"):
            try:
                balance = float(response_text.split(":")[1].strip())
                return f"{balance:.2f}"
            except ValueError:
                print("Error parsing SMSHUB balance.")
        return "0.00"


    def update_kopeechka_balance(self, balance):
        self.ui.lblKopeechkaBalance.setText(balance)

    def update_capsolver_balance(self, balance):
        self.ui.lblCapsolverBalance.setText(balance)

    def update_smspva_balance(self, balance):
        self.ui.lblSMSPVABalance.setText(balance)

    def update_smshub_balance(self, balance):
        self.ui.lblSMSHUBBalance.setText(balance)

    def update_5sim_balance(self, balance):
        self.ui.lbl5SimBalance.setText(balance)
