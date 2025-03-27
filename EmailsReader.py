from pathlib import Path


class EmailsReader:
    FILE_PATH = "emails.txt"

    @staticmethod
    def get_first_email_and_password():
        try:
            path = Path(EmailsReader.FILE_PATH)
            lines = path.read_text().splitlines()

            if not lines:
                return None

            first_line = lines[0]
            email_and_password = EmailsReader.extract_email_and_password(first_line)

            if not email_and_password:
                print("Invalid format in the file.")
                return None

            path.write_text('\n'.join(lines[1:]))

            return email_and_password
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    @staticmethod
    def extract_email_and_password(line):
        parts = line.split('|')

        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()

        parts = line.split(':')

        if len(parts) >= 2:
            return parts[0].strip(), parts[1].strip()

        return None
