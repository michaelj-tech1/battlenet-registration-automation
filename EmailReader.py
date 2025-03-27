import imaplib
import email
import time

class EmailReader:
    def __init__(self, email, password, max_attempts=15):
        self.email = email
        self.password = password
        self.max_attempts = max_attempts
        if 'gmx' in email:
            self.imap_host = 'imap.gmx.com'
        else:
            self.imap_host = 'outlook.office365.com'
        self.imap_port = 993

    def get_steam_guard_link(self):
        return self.search_inbox("Disable Steam Guard Confirmation", "Steam Guard disable link")

    def get_steam_verification_link(self):
        return self.search_inbox("New Steam Account Email Verification", "Steam verification link")

    def process_steam_phone_link(self):
        return self.search_inbox("Adding a phone number to your Steam account", "Steam phone link")

    def search_inbox(self, subject_filter, description):
        link = None
        attempts = 0
        while link is None and attempts < self.max_attempts:
            attempts += 1
            print(f'Attempt {attempts}: Checking for {description}...')
            try:
                mail = self.init_mailbox()
                status, messages = mail.search(None, f'(SUBJECT "{subject_filter}")')
                if status == 'OK':
                    for num in messages[0].split():
                        typ, data = mail.fetch(num, '(RFC822)')
                        for response_part in data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1])
                                link = self.find_link_in_message(msg)
                                if link:
                                    return link
                if link is None:
                    print(f'No {description} found. Waiting for 3 sec before next attempt...')
                    time.sleep(3)
            except Exception as e:
                print(f"An error occurred: {str(e)}")
                break
        return None

    def find_link_in_message(self, message):
        content_type = message.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            return self.extract_link(message.get_payload(decode=True).decode())
        elif message.is_multipart():
            for part in message.walk():
                content_type = part.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    return self.extract_link(part.get_payload(decode=True).decode())
        return None

    def extract_link(self, text):
        words = text.split()
        for word in words:
            if word.startswith('http') and '://' in word:
                return word
        return None

    def init_mailbox(self):
        mail = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        mail.login(self.email, self.password)
        mail.select('inbox')
        return mail
