
import re
import threading
import random
import string
import time
import traceback
from bs4 import BeautifulSoup
from Email import Email
import requests
from faker import Faker
from EmailReader import EmailReader
from FiveSimRequest import FiveSimAPI
from SmsHubRequest import SmsHubAPI
from SmsPvaRequest import SmsPvaRequest
import concurrent.futures
from PySide6.QtCore import QObject, Signal
from EmailsReader import EmailsReader

class SignUp:
    def __init__(self, config, console_updater, thread_index,mainapp, proxies):
        self.session = None
        self.sessionid = None
        self.initid = None
        self.gid = None
        self.sitekey = ""
        self.s = ""
        self.captchaResponse = ""
        self.refreshToken = None
        self.steamID = ""
        self.auth = ""
        self.nonce = ""
        self.creationid = ""
        self.config = config
        self.console_updater = console_updater
        self.thread_index = thread_index
        self.main_app = mainapp
        self.email_api = Email(self.config.kopeechka_api_key,self.config.kopeechka_email_pref)
        self.steamEmail = None
        self.emailId = None
        self.email = None
        self.password = None
        self.proxies = proxies
        self.proxy = None
        self.csrf_token = None
        self.xsrf_token = None
        self.arkose_blob = ""
        self.accountPassword = ""

    def generate_rand_num(self):
        return random.randint(1000, 999999)

    def generate_password(self, min_length=8, max_length=15):
        uppercase = string.ascii_uppercase
        lowercase = string.ascii_lowercase
        digits = string.digits
        symbols = "$#@!&"
        all_characters = uppercase + lowercase + digits + symbols

        password_length = random.randint(min_length, max_length)

        password = [
            random.choice(uppercase),
            random.choice(lowercase),
            random.choice(digits),
            random.choice(symbols)
        ]

        password += [random.choice(all_characters) for _ in range(password_length - 4)]
        random.shuffle(password)
        password = ''.join(password).strip()

        while len(password) < min_length:
            password += random.choice(all_characters)

        return password

        return password
    def generate_random_dob(self):
        year = random.randint(1980, 2004)
        month = random.randint(1, 12)

        if month == 2:
            day = random.randint(1, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28)
        elif month in [4, 6, 9, 11]:
            day = random.randint(1, 30)
        else:
            day = random.randint(1, 31)

        dob_day = str(day).zfill(2)
        dob_month = str(month).zfill(2)
        dob_year = str(year)

        return dob_day, dob_month, dob_year
    def generate_email(self):
        fake = Faker()
        name = fake.first_name().lower()
        random_digits = ''.join(str(random.randint(0, 9)) for _ in range(6))
        domains = ['gmail.com', 'yahoo.com', 'outlook.com', 'hotmail.com']
        domain = random.choice(domains)
        email = f"{name}{random_digits}@{domain}"
        return email
    def generate_random_tag(self,max_length=12):
        fake = Faker()
        first_name = fake.first_name()

        max_number_length = max_length - len(first_name)

        if max_number_length > 0:
            number_part = ''.join(random.choices("0123456789", k=random.randint(1, max_number_length)))
        else:
            number_part = ""

        return first_name + number_part

    def append_email_and_password(self,email, password):
        with open('emails.txt', 'a+') as file:
            file.seek(0, 2)
            if file.tell() != 0:
                file.seek(-1, 2)
                if file.read(1) != '\n':
                    file.write('\n')
            file.write(f"{email}:{password}\n")
        print(f"Appended to file: {email}:{password}")

    def save_account_info_txt(self,username, password, email, email_password, phone_number, file_path='accounts.txt'):

        with open(file_path, 'a', encoding='utf-8') as file:
            account_info = f"{username} | {password} | {email} | {email_password} | {phone_number}\n"
            file.write(account_info)

        print(f"Account info for {username} saved successfully in text file using tab-separated values.")

    def generate_random_password(self):
        length = random.randint(15, 25)
        characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits)
        ]
        password += random.choices(characters, k=length - 4)
        random.shuffle(password)
        return ''.join(password)

    def generate_random_name(self):
        fake = Faker()
        first_name = fake.first_name()
        last_name = fake.last_name()
        return first_name, last_name
    def create_session(self):
        """Method to initiate a session."""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.3124.85',
        })

        if self.config.use_proxies:
            proxy = random.choice(self.proxies)
            self.proxy = {
                'http': proxy,
                'https': proxy
            }
        else:
            self.proxy = {
                'http': None,
                'https': None
            }
    def initial_request(self):
        try:
            headers = {
                'upgrade-insecure-requests': '1',
                'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'sec-fetch-site': 'cross-site',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-user': '?1',
                'sec-fetch-dest': 'document',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-ch-ua-model': '""',
                'accept-encoding': 'gzip, deflate, br, zstd',
                'priority': 'u=0, i',
            }
            response0 = self.session.get("https://account.battle.net/creation/flow/creation-full", headers=headers,proxies=self.proxy, timeout=15)
            print(response0.text)
            soup = BeautifulSoup(response0.text, 'html.parser')
            csrf_token_input = soup.find('input', {'name': '_csrf'})
            if csrf_token_input:
                self.csrf_token = csrf_token_input.get('value')
                print("Found the csrf")
                return True
            else:
                print("CSRF token not found.")
                return False
        except:
            print("Got proxy error")
            return False

    def dob(self,country):
        self.console_updater.update_status(self.thread_index, "DOB done")
        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryd0VAAxBm8TNdirny',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }
        print(country)
        dob_day, dob_month, dob_year = self.generate_random_dob()
        print(dob_day,dob_month,dob_year)
        payload = (
                b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                b"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
                + self.csrf_token.encode() + b"\r\n"
                 b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                 b"Content-Disposition: form-data; name=\"webdriver\"\r\n\r\n"
                 b"false\r\n"
                 b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                 b"Content-Disposition: form-data; name=\"country\"\r\n\r\n"
                + country.encode() + b"\r\n"
                 b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                 b"Content-Disposition: form-data; name=\"dob-plain\"\r\n\r\n"
                 b"\r\n"
                 b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                 b"Content-Disposition: form-data; name=\"dob-format\"\r\n\r\n"
                 b"MDY\r\n"
                 b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                 b"Content-Disposition: form-data; name=\"dob-month\"\r\n\r\n"
                + dob_month.encode() + b"\r\n"
                   b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                   b"Content-Disposition: form-data; name=\"dob-day\"\r\n\r\n"
                + dob_day.encode() + b"\r\n"
                     b"------WebKitFormBoundaryd0VAAxBm8TNdirny\r\n"
                     b"Content-Disposition: form-data; name=\"dob-year\"\r\n\r\n"
                + dob_year.encode() + b"\r\n"
                  b"------WebKitFormBoundaryd0VAAxBm8TNdirny--\r\n"
        )

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/get-started",headers=headers, data=payload, proxies=self.proxy, timeout=15)
        print("response from dob")

        if 'data-step-has-errors="true"' in response0.text:
            return False
        else:
            return True

    def name(self):
        self.console_updater.update_status(self.thread_index, "Name done")
        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryFb6gfNNITep06R6n',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }
        first_name, last_name = self.generate_random_name()
        boundary = "------WebKitFormBoundaryFb6gfNNITep06R6n"

        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"first-name\"\r\n\r\n"
            f"{first_name}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"last-name\"\r\n\r\n"
            f"{last_name}\r\n"
            f"{boundary}--\r\n"
        ).encode()
        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/provide-name",headers=headers, data=payload, proxies=self.proxy, timeout=15)
        print("response from name")

        if 'data-step-has-errors="true"' in response0.text:
            return False
        else:
            return True

    def submit_email(self):
        self.console_updater.update_status(self.thread_index, "Email done")
        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryDWu23O3RZ5iMDtP4',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }

        boundary = "------WebKitFormBoundaryDWu23O3RZ5iMDtP4"
        print("Email being used" + str(self.email))
        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"email\"\r\n\r\n"
            f"{self.email}\r\n"
            f"{boundary}\r\n"
            "Content-Disposition: form-data; name=\"phone-number\"\r\n\r\n"
            "\r\n"
            f"{boundary}--\r\n"
        ).encode()

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/provide-credentials",headers=headers, data=payload, proxies=self.proxy, timeout=15)
        print("response from email")



        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryWJxP6NSOZY5ggCaR',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }
        boundary = "------WebKitFormBoundaryWJxP6NSOZY5ggCaR"

        response_text = response0.text
        soup = BeautifulSoup(response_text, 'html.parser')
        matches = soup.find_all("input", {"name": "tou-agreements-implicit"})
        filtered_matches = [match['value'] for match in matches if match.get('value').lower() != "none"]
        filtered_matches.append("none")

        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            "Content-Disposition: form-data; name=\"opt-in-blizzard-news-special-offers\"\r\n\r\n"
            "false\r\n"
        )

        for agreement in filtered_matches:
            payload += (
                f"{boundary}\r\n"
                f"Content-Disposition: form-data; name=\"tou-agreements-implicit\"\r\n\r\n"
                f"{agreement}\r\n"
            )

        payload += f"{boundary}--\r\n"
        payload = payload.encode()

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/legal-and-opt-ins",headers=headers, data=payload, proxies=self.proxy, timeout=15)
        self.console_updater.update_status(self.thread_index, "Accepting terms")
        print("response from terms")



    def set_password(self):
        self.console_updater.update_status(self.thread_index, "Password done")
        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundary3bJ7CFiwL0JHm0g8',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }

        self.accountPassword = self.generate_password()

        boundary = "------WebKitFormBoundary3bJ7CFiwL0JHm0g8"

        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"password\"\r\n\r\n"
            f"{self.accountPassword}\r\n"
            f"{boundary}--\r\n"
        ).encode()

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/set-password",headers=headers, data=payload, proxies=self.proxy, timeout=15)




    def battleTag(self,battleTag):
        headers = {
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryWJmBgi8FqbT50tdk',
            'x-flow-fragment': 'true',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-model': '""',
            'accept': '*/*',
            'origin': 'https://account.battle.net',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'priority': 'u=1, i',
        }

        boundary = "------WebKitFormBoundaryWJmBgi8FqbT50tdk"

        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"battletag\"\r\n\r\n"
            f"{battleTag}\r\n"
            f"{boundary}--\r\n"
        ).encode()

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/set-battletag",
                                 headers=headers, data=payload, proxies=self.proxy, timeout=15)
        print("Response from battle tag request")
        print(response0.text)


        soup = BeautifulSoup(response0.text, 'html.parser')

        input_element = soup.find("input", {"id": "capture-arkose"})
        if input_element:
            print("Arkose blob: ")
            self.arkose_blob = input_element.get("data-arkose-exchange-data")
            print(str(self.arkose_blob))
        else:
            print("Blob not found in the response")

        if 'data-step-has-errors="true"' in response0.text:
            return True
        else:
            return False

    def finalize(self,solution):
        boundary = "------WebKitFormBoundaryqnasKuWcNN4xOkAf"
        payload = (
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"_csrf\"\r\n\r\n"
            f"{self.csrf_token}\r\n"
            f"{boundary}\r\n"
            f"Content-Disposition: form-data; name=\"arkose\"\r\n\r\n"
            f"{solution}\r\n"
            f"{boundary}--\r\n"
        ).encode()

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'content-type': 'multipart/form-data; boundary=----WebKitFormBoundaryqnasKuWcNN4xOkAf',
            'sec-fetch-site': 'same-origin',
            'origin': 'https://account.battle.net',
            'sec-fetch-mode': 'navigate',
            'referer': 'https://account.battle.net/creation/flow/creation-full',
            'sec-fetch-dest': 'document',
            'priority': 'u=0, i',
            'accept-encoding': 'gzip, deflate, br',
        }

        response0 = self.session.post("https://account.battle.net/creation/flow/creation-full/step/captcha-gate",headers=headers, data=payload, proxies=self.proxy, timeout=15)
        print("response from captcha:")
        print(response0.text)
        soup = BeautifulSoup(response0.text, 'html.parser')

        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if href.startswith('https://') and 'account.battle.net/login/ticket-login' in href:
                target_url = href
                print(f"Parsed url: " + str(target_url))
                loginUrlRequest = self.session.get(target_url, proxies=self.proxy, timeout=15)
                print("Made the login request")
                return True
            else:
                print("Got bad captcha canceling")
                return False


    def account(self):
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-model': '""',
            'Referer': 'https://us.account.battle.net/',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }

        response0 = self.session.get("https://us.account.battle.net/", headers=headers, proxies=self.proxy, timeout=15)

    def oauth(self):
        headers = {
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-model': '""',
            'Referer': 'https://us.account.battle.net/',
            'Accept-Encoding': 'gzip, deflate, br, zstd'
        }

        response0 = self.session.get("https://us.account.battle.net/oauth2/authorization/account-settings", headers=headers,proxies=self.proxy, timeout=15)

    def oauth2(self):
        headers = {
            'Connection': 'keep-alive',
            'sec-ch-ua-mobile': '?0',

            'sec-ch-ua-model': '""',
            'Upgrade-Insecure-Requests': '1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Dest': 'document',
            'Referer': 'https://us.account.battle.net/overview',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }

        response0 = self.session.get("https://us.account.battle.net/oauth2/authorization/account-settings?ref=%2Foverview", headers=headers, proxies=self.proxy, timeout=15)


    def overview(self):
        self.xsrf_token = self.session.cookies.get("XSRF-TOKEN", domain="us.account.battle.net")
        headers = {
            'Connection': 'keep-alive',
            'X-XSRF-TOKEN': self.xsrf_token,
            'Content-Type': 'application/json',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-mobile': '?0',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://us.account.battle.net/overview',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }

        response0 = self.session.get("https://us.account.battle.net/api/overview", headers=headers,proxies=self.proxy, timeout=15)

    def add(self):
        headers = {
            'Connection': 'keep-alive',
            'X-XSRF-TOKEN': self.xsrf_token,
            'Content-Type': 'application/json',
            'sec-ch-ua-model': '""',
            'sec-ch-ua-mobile': '?0',
            'Accept': '*/*',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://us.account.battle.net/details/sms/setup/add',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }
        response0 = self.session.get("https://us.account.battle.net/api/security/sms/add", headers=headers, proxies=self.proxy,timeout=15)

    def add_phone(self,phoneNumber,solution):
        headers = {
            'X-XSRF-TOKEN': self.xsrf_token,
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'Accept': '*/*',
            'Origin': 'https://us.account.battle.net',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://us.account.battle.net/details/sms/setup/add',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }
        payload = {
            "phoneNumber": phoneNumber,
            "arkoseToken": solution
        }
        response0 = self.session.post("https://us.account.battle.net/api/security/sms/notification", headers=headers,json=payload, proxies=self.proxy, timeout=15)

    def sms(self,sms):
        headers = {
            'X-XSRF-TOKEN': self.xsrf_token,
            'Content-Type': 'application/json',
            'sec-ch-ua-mobile': '?0',
            'Accept': '*/*',
            'Origin': 'https://us.account.battle.net',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://us.account.battle.net/details/sms/setup/add',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
        }
        payload = {
            "verificationCode": sms
        }
        response0 = self.session.post("https://us.account.battle.net/api/security/sms", headers=headers, json=payload,proxies=self.proxy, timeout=15)



    def completeAll(self):
        try:
            self.console_updater.update_status(self.thread_index, "Starting up thread...")
            self.create_session()
            self.initial_request()

            country = self.config.kopeechka_email_pref
            print("The country is: " + str(country))
            self.dob(country)
            self.name()
            if self.config.use_emails:
                email_and_password = EmailsReader.get_first_email_and_password()
                if email_and_password:
                    self.email, self.password = email_and_password
                    print(f"Email and password set: {self.email}, {self.password}")
                else:
                    print("No email or password could be retrieved.")
            else:
                email_details = self.email_api.email_request()
                self.email = email_details.get("email")
                self.emailId = email_details.get("id")
                self.password = email_details.get("password")

            self.submit_email()
            self.set_password()


            if not self.config.account_username:
                username = self.generate_random_tag()
            else:
                username = self.config.account_username + str(self.generate_rand_num())
            print("Using username " + str(username))
            self.console_updater.update_status(self.thread_index, f"Using battle tag {username}")
            battleTagCheck = self.battleTag(username)

            if battleTagCheck:
                print("Exiting battle tag had errors")
                return


            print("The blob data in sign up all:")
            print(self.arkose_blob)

            capApiKey = self.config.capsolver_api_key
            capSolution = ""
            self.console_updater.update_status(self.thread_index, "Waiting for captcha")
            if self.config.use_two_captcha:
                print("2captcha selected for captcha service ")
                payload = {
                    "clientKey": capApiKey,
                    "task": {
                        "type": "FunCaptchaTaskProxyless",
                        "websiteURL": "https://account.battle.net",
                        "websitePublicKey": "E8A75615-1CBA-5DFF-8032-D16BCF234E10",
                        "funcaptchaApiJSSubdomain": "https://blizzard-api.arkoselabs.com",
                        "data": f"{{\"blob\":\"{self.arkose_blob}\"}}",
                        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.3124.85"
                    }
                }
                task_id = ""
                try:
                    max_retries = 3
                    retry_count = 0
                    while retry_count < max_retries:
                        try:
                            response = requests.post("https://api.2captcha.com/createTask", json=payload)
                            response.raise_for_status()
                            result = response.json()

                            if result.get("errorId") == 0:
                                task_id = result.get("taskId")
                                print(f"Task created successfully. Task ID: {task_id}")
                                break
                            elif "overloaded" in result.get("errorDescription", "").lower():
                                print("Server is overloaded, retrying in 5 seconds...")
                                time.sleep(5)
                                retry_count += 1
                            else:
                                self.console_updater.update_status(self.thread_index, "Check captcha api key")
                                print(f"Error in task creation: {result.get('errorDescription')}")
                                return
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred: {e}")
                            break
                    if retry_count == max_retries:
                        return
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")

                endpoint = "https://api.2captcha.com/getTaskResult"
                payload = {
                    "clientKey": capApiKey,
                    "taskId": task_id
                }

                timeout_intervals = 140 // 10
                interval_count = 0

                while True:
                    if interval_count >= timeout_intervals:
                        self.console_updater.update_status(self.thread_index, "Failed to get captcha.")
                        self.completeAll()
                        return

                    try:
                        response = requests.post(endpoint, json=payload)
                        response.raise_for_status()

                        result = response.json()
                        if result.get("status") == "ready":
                            capSolution = result.get("solution", {}).get("token")
                            print(f"Captcha solved successfully. Solution token: {capSolution}")
                            print(result)
                            break
                        elif result.get("status") == "processing":
                            print("Captcha is still being processed. Retrying in 10 seconds...")
                            time.sleep(10)
                            interval_count += 1
                        else:
                            print(f"Unexpected status: {result.get('status')}")
                            break
                    except requests.exceptions.RequestException as e:
                        print(f"An error occurred: {e}")
                        break
            else:
                print("Best capsolver selected for captcha service ")
                url = 'https://bcsapi.xyz/api/captcha/funcaptcha'
                data = {
                    'page_url': "https://account.battle.net/creation/flow/creation-full",
                    "s_url": "https://blizzard-api.arkoselabs.com",
                    'site_key': "E8A75615-1CBA-5DFF-8032-D16BCF234E10",
                    "data": "{\"blob\": \"" + self.arkose_blob + "\"}",
                    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36 Edg/134.0.3124.85",
                    'access_token': capApiKey,
                }

                response = requests.post(url, data=data)
                result = response.json()
                print("Captcha result:")
                print(result)
                if result.get('status') == 'submitted':
                    task_id = result['id']
                    print(f"Task submitted successfully. Task ID: {task_id}")

                else:
                    print(f"Error: {result.get('error')}")

                url = f'https://bcsapi.xyz/api/captcha/{task_id}?access_token={capApiKey}'
                timeout_intervals = 140 // 10
                interval_count = 0

                while True:
                    if interval_count >= timeout_intervals:
                        self.console_updater.update_status(self.thread_index, "Failed captcha canceling and retrying.")
                        self.completeAll()
                        return
                    response = requests.get(url)
                    result = response.json()

                    if result.get('status') == 'completed':
                        capSolution = result.get('solution')
                        print("Solution found:", result)
                        break
                    elif result.get('status') == 'pending':
                        print("Task is still in progress. Waiting...")
                        time.sleep(10)
                        interval_count += 1
                    else:
                        print(f"Error: {result.get('error')}")
                        break
            self.console_updater.update_status(self.thread_index, "Captcha solved!")
            successCaptcha = self.finalize(capSolution)
            if not successCaptcha:
                self.console_updater.update_status(self.thread_index, "BNET rejected token reporting it bad.")
                if self.config.use_two_captcha:
                    url = f"https://2captcha.com/res.php?key={capApiKey}&action=reportbad&id={task_id}"
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        print(response)
                    except requests.exceptions.RequestException:
                        print("ERROR in report bad")
                else:
                    url = f"https://bcsapi.xyz/api/captcha/bad/{task_id}"
                    payload = {
                        "access_token": capApiKey
                    }
                    try:
                        response = requests.post(url, json=payload)
                        response.raise_for_status()
                        print(response)
                    except requests.exceptions.RequestException:
                        print("ERROR in report bad")
                self.completeAll()
                return
            else:
                if self.config.use_two_captcha:
                    url = f"https://2captcha.com/res.php?key={capApiKey}&action=reportgood&id={task_id}"
                    try:
                        response = requests.get(url)
                        response.raise_for_status()
                        print(response)
                    except requests.exceptions.RequestException:
                        print("ERROR in report good")

            self.console_updater.update_status(self.thread_index, "Successfully made account!")
            self.console_updater.update_second_console(username, self.accountPassword)
            if not self.config.use_sms_api:
                self.save_account_info_txt(username, self.accountPassword, self.email, self.password, "none")
                return

            if self.config.use_sms_api:

                self.account()
                self.oauth()
                self.oauth2()
                self.overview()
                self.add()
                self.console_updater.update_status(self.thread_index, "Waiting for phone captcha")
                capSolution1 = ""
                if self.config.use_two_captcha:
                    payload = {
                        "clientKey": capApiKey,
                        "task": {
                            "type": "FunCaptchaTaskProxyless",
                            "websiteURL": "https://account.battle.net/details/sms/setup/add",
                            "websitePublicKey": "9C3260E3-AD4C-6719-E0A9-56D21BFB0BCD",
                        }
                    }
                    task_id = ""
                    try:
                        max_retries = 3
                        retry_count = 0
                        while retry_count < max_retries:
                            try:
                                response = requests.post("https://api.2captcha.com/createTask", json=payload)
                                response.raise_for_status()
                                result = response.json()

                                if result.get("errorId") == 0:
                                    task_id = result.get("taskId")
                                    print(f"Task created successfully. Task ID: {task_id}")
                                    break
                                elif "overloaded" in result.get("errorDescription", "").lower():
                                    print("Server is overloaded, retrying in 5 seconds...")
                                    time.sleep(5)
                                    retry_count += 1
                                else:
                                    print(f"Error in task creation: {result.get('errorDescription')}")
                                    break
                            except requests.exceptions.RequestException as e:
                                print(f"An error occurred: {e}")
                                break
                        if retry_count == max_retries:
                            return
                    except requests.exceptions.RequestException as e:
                        print(f"An error occurred: {e}")
                        return

                    endpoint = "https://api.2captcha.com/getTaskResult"
                    payload = {
                        "clientKey": capApiKey,
                        "taskId": task_id
                    }

                    timeout_intervals = 120 // 10
                    interval_count = 0

                    while True:
                        if interval_count >= timeout_intervals:
                            print("Timed out after 45 seconds.")
                            try:
                                if self.config.use_emails:
                                    self.append_email_and_password(self.email, self.password)
                                else:
                                    self.email_api.cancel_mailbox(self.email)
                            except:
                                print("Error with email save")
                            return

                        try:
                            response = requests.post(endpoint, json=payload)
                            response.raise_for_status()

                            result = response.json()
                            if result.get("status") == "ready":
                                capSolution1 = result.get("solution", {}).get("token")
                                print(f"Captcha solved successfully. Solution token: {capSolution1}")
                                print(result)
                                break
                            elif result.get("status") == "processing":
                                print("Captcha is still being processed. Retrying in 10 seconds...")
                                time.sleep(10)
                                interval_count += 1
                            else:
                                print(f"Unexpected status: {result.get('status')}")
                                break
                        except requests.exceptions.RequestException as e:
                            print(f"An error occurred: {e}")
                            break

                else:

                    url = 'https://bcsapi.xyz/api/captcha/funcaptcha'
                    data = {
                        'page_url': "https://account.battle.net/details/sms/setup/add",
                        'site_key': "9C3260E3-AD4C-6719-E0A9-56D21BFB0BCD",
                        'access_token': capApiKey,
                    }

                    response = requests.post(url, data=data)
                    print(response.text)
                    result = response.json()

                    if result.get('status') == 'submitted':
                        task_id = result['id']
                        print(f"Task submitted successfully. Task ID: {task_id}")

                    else:
                        print(f"Error: {result.get('error')}")
                        return None

                    url = f'https://bcsapi.xyz/api/captcha/{task_id}?access_token={capApiKey}'
                    timeout_intervals = 125 // 5
                    interval_count = 0
                    capSolution1 = ""
                    while True:
                        if interval_count >= timeout_intervals:
                            print("Timed out after 45 seconds.")
                            try:
                                if self.config.use_emails:
                                    self.append_email_and_password(self.email, self.password)
                                else:
                                    self.email_api.cancel_mailbox(self.email)
                            except:
                                print("Error with email save")
                            return
                        response = requests.get(url)
                        result = response.json()

                        if result.get('status') == 'completed':
                            capSolution1 = result.get('solution')
                            print("Solution found:", capSolution1)
                            break
                        elif result.get('status') == 'pending':
                            print("Task is still in progress. Waiting...")
                            time.sleep(5)
                            interval_count += 1
                        else:
                            print(f"Error: {result.get('error')}")
                            break
                self.console_updater.update_status(self.thread_index, "Captcha solved!")
                phoneNumber = ""
                id = ""
                countryCode = None
                apiKey = self.config.api_key
                sms_service = None
                smshub = None
                five_sim = None
                try:
                    if self.config.use_smspva:
                        sms_service = SmsPvaRequest(apiKey, self.config.sms_country)
                        response = sms_service.get_sms_number()
                        phoneNumber = f"{response.country_code}{response.number}"
                        id = response.id
                    if self.config.use_smshub:
                        smshub = SmsHubAPI(apiKey, self.config.sms_country)
                        response = smshub.get_number()
                        id, phoneNumber = response
                    if self.config.use_5sim:
                        five_sim = FiveSimAPI(apiKey)
                        phoneNumber, id = five_sim.get_number_and_country_code(self.config.sms_country, "any")
                    print(f"Acquired Phone Number: {phoneNumber}, ID: {id}, Country Code: {countryCode or 'Not Available'}")

                except Exception as e:
                    print(f"Error during SMS service: {str(e)}")
                self.console_updater.update_status(self.thread_index, f"Got the phone number {phoneNumber}")
                match = re.match(r"(\+\d+)(\d+)$", phoneNumber)
                if match:
                    country_code, main_number = match.groups()
                    formatted_number = f"{country_code}{main_number}"
                else:
                    formatted_number = phoneNumber

                self.add_phone(formatted_number,capSolution1)


                sms = None
                wait_sec = self.config.wait_code_sec
                self.console_updater.update_status(self.thread_index, "Waiting for sms code")
                if self.config.use_smspva and sms_service:
                    sms = sms_service.get_sms_message(id, wait_sec)
                    if sms is None:
                        self.console_updater.update_status(self.thread_index, "Didn't get sms in time canceling number and trying new thread")
                        print("Canceling SmsPva number due to no SMS received.")
                        sms_service.cancel_number(id)
                        self.completeAll()
                        return
                if self.config.use_smshub and smshub:
                    sms = smshub.get_sms_code(id, wait_sec)
                    if sms is None:
                        self.console_updater.update_status(self.thread_index, "Didn't get sms in time canceling number and trying new thread")
                        smshub.cancel_number(id)
                        self.completeAll()
                        return

                if self.config.use_5sim and five_sim:
                    sms = five_sim.get_sms_code(id, wait_sec)
                    if sms is None:
                        self.console_updater.update_status(self.thread_index, "Didn't get sms in time canceling number and trying new thread")
                        five_sim.cancel_number(id)
                        self.completeAll()
                        return

                self.console_updater.update_status(self.thread_index, "Got the sms and saving account info!")
                self.sms(sms)
                self.main_app.setMadeAccounts()
                self.main_app.setTotalAttempted()
                self.save_account_info_txt(username, self.accountPassword, self.email, self.password, phoneNumber)
        except Exception as e:
            self.main_app.setFailedAccounts()
            self.main_app.setTotalAttempted()
            traceback.print_exc()

class Config:
    def __init__(self, data):
        self.use_proxies = bool(data.get('use_proxies', False))
        self.use_emails = bool(data.get('use_emails', False))
        self.accounts_to_create = int(data.get('accounts_to_create', 1))
        self.threads_to_run = int(data.get('threads_to_run', 1))
        self.account_username = data.get('account_username', '')
        self.kopeechka_api_key = data.get('kopeechka_api_key', '')
        self.kopeechka_email_pref = data.get('kopeechka_email_pref', '')
        self.capsolver_api_key = data.get('captcha_api_key', '')
        self.use_sms_api = bool(data.get('use_sms_api', False))
        self.use_smspva = bool(data.get('use_smspva', False))
        self.use_smshub = bool(data.get('use_smshub', False))
        self.use_5sim = bool(data.get('use_5sim', False))
        self.api_key = data.get('api_key', '')
        self.sms_country = data.get('sms_country', '')
        self.wait_code_sec = int(data.get('wait_code_sec', 30))
        self.use_best_capsolver = bool(data.get('use_best_capsolver', False))
        self.use_two_captcha = bool(data.get('use_two_captcha', False))

class ProxyManager:
    def __init__(self, filename='proxy.txt'):
        self.filename = filename
        self.proxies = self.load_proxies()

    def load_proxies(self):
        proxies = []
        try:
            with open(self.filename, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line:
                        proxy = self.format_proxy(line)
                        if proxy:
                            proxies.append(proxy)
                        else:
                            print(f"Line skipped, no match found: {line}")
        except FileNotFoundError:
            print(f"Error: The file {self.filename} was not found.")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        return proxies

    def format_proxy(self, proxy_line):
        patterns = {
            'host_port_user_pass': re.compile(r'^([\w\.]+):(\d+):([\w+\-]+):([\w+\-]+)$'),
            'user_pass_host_port': re.compile(r'^([\w+\-]+):([\w+\-]+)@([\w\.]+):(\d+)$'),
            'ip_port': re.compile(r'^([\w\.]+):(\d+)$')
        }

        for key, pattern in patterns.items():
            match = pattern.match(proxy_line)
            if match:
                if key == 'host_port_user_pass':
                    hostname, port, username, password = match.groups()
                    return f"http://{username}:{password}@{hostname}:{port}"
                elif key == 'user_pass_host_port':
                    username, password, hostname, port = match.groups()
                    return f"http://{username}:{password}@{hostname}:{port}"
                elif key == 'ip_port':
                    ip, port = match.groups()
                    return f"http://{ip}:{port}"
        return None

    def get_proxies(self):
        return self.proxies




class SignUpThreads:
    def __init__(self, config, console_updater, mainapp):
        self.mainapp = mainapp
        self.config = config
        self.threads = []
        self.console_updater = console_updater
        self.proxy_manager = ProxyManager()
        self.proxies = self.proxy_manager.get_proxies()
        print("Loaded proxies:", self.proxies)
        self.accounts_remaining = self.config.accounts_to_create
        self.lock = threading.Lock()

    def start_processes(self):
        num_threads = self.config.threads_to_run
        for i in range(num_threads):
            thread_index = str(i + 1)
            thread = threading.Thread(target=self.run_signup, args=(thread_index,))
            thread.daemon = True
            thread.start()
            self.threads.append(thread)

    def run_signup(self, thread_index):
        while True:
            with self.lock:
                if self.accounts_remaining <= 0:
                    break
                self.accounts_remaining -= 1
            current_account = self.config.accounts_to_create - self.accounts_remaining
            print(f"Thread {thread_index} starting signup for account {current_account}")
            try:
                signup = SignUp(self.config, self.console_updater, thread_index, self.mainapp, self.proxies)
                signup.completeAll()
            except Exception as e:
                print(f"Error in thread {thread_index}: {e}")

        print(f"Thread {thread_index} completed all tasks.")