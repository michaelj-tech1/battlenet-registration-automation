

import keyring
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class LoginWindow(QMainWindow):
    login_successful = Signal(str)


    def __init__(self, keyauthapp):
        super(LoginWindow, self).__init__()
        self.api = keyauthapp
        self.setupUi()
        self.init_license_check()
    def setupUi(self):
        self.setObjectName("LoginWindow")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(325, 250)

        self.centralwidget = QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.centralwidget.setStyleSheet("""
            background: #2c2c2c;
            border-radius: 15px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.5);
        """)
        self.setCentralWidget(self.centralwidget)


        self.layout = QVBoxLayout(self.centralwidget)
        self.layout.setContentsMargins(20, 10, 20, 10)
        self.layout.setSpacing(10)

        self.topLayout = QHBoxLayout()
        self.topLayout.setAlignment(Qt.AlignRight)
        self.topLayout.setSpacing(5)

        self.minimizeButton = QPushButton()
        self.minimizeButton.setIcon(QIcon("Icons/minimize.png"))
        self.minimizeButton.setIconSize(QSize(20, 20))
        self.minimizeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #1f1f1f;
                border-radius: 5px;
            }
        """)
        self.minimizeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.topLayout.addWidget(self.minimizeButton)

        self.closeButton = QPushButton()
        self.closeButton.setIcon(QIcon("Icons/close.png"))
        self.closeButton.setIconSize(QSize(20, 20))
        self.closeButton.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
            }
            QPushButton:hover {
                background-color: #1f1f1f;
                border-radius: 5px;
            }
        """)
        self.closeButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.topLayout.addWidget(self.closeButton)

        self.layout.addLayout(self.topLayout)

        self.title = QLabel("BNET Gen")
        self.title.setStyleSheet("""
            font-size: 24px;
            font-family: 'Roboto', sans-serif;
            font-weight: bold;
            color: white;
            background-color: transparent;
        """)
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        self.status = QLabel("Loading...")
        self.status.setStyleSheet("""
            font-size: 14px;
            font-family: 'Roboto', sans-serif;
            color: #cccccc;
            background-color: transparent;
        """)
        self.status.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.status)

        self.progressBar = QProgressBar(self.centralwidget)
        self.progressBar.setRange(0, 100)
        self.progressBar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #444;
                border-radius: 10px;
                color: white;
                text-align: center;
                background-color: transparent;
            }
            QProgressBar::chunk {
                background-color: #27ae60;
                border-radius: 10px;
            }
        """)
        self.progressBar.setValue(20)
        self.layout.addWidget(self.progressBar)

        self.keyInput = QLineEdit()
        self.keyInput.setPlaceholderText("Enter your key")
        self.keyInput.setStyleSheet("""
            QLineEdit {
                border: 1px solid #777;
                border-radius: 10px;
                padding: 8px;
                color: white;
                background: rgba(255, 255, 255, 0.1);
                font-size: 16px;
            }
            QLineEdit:hover {
                border-color: #999;
            }
        """)
        self.keyInput.setAlignment(Qt.AlignCenter)
        self.keyInput.setMaximumWidth(300)
        self.keyInput.setVisible(False)
        self.layout.addWidget(self.keyInput)

        self.loginButton = QPushButton("Login")
        self.loginButton.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
                transition: background-color 0.3s;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.loginButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.loginButton.setVisible(False)
        self.layout.addWidget(self.loginButton, alignment=Qt.AlignCenter)

        self.progressBarTimer = QTimer()
        self.progressBarTimer.timeout.connect(self.updateProgressBar)
        self.progressBarTimer.start(30)

        self.minimizeButton.clicked.connect(self.showMinimized)
        self.closeButton.clicked.connect(QApplication.quit)
        self.loginButton.clicked.connect(self.handle_login)

    def init_license_check(self):
        saved_key = keyring.get_password("BNET GEN", "license_key")
        if saved_key is None or saved_key == "":
            print("No key found, showing setup page.")
            self.show_setup_page()
        else:
            print("Key found, showing login window.")
            self.show()

    def show_setup_page(self):
        print("Opening setup page...")
        try:
            setup_page = SetupPage(self)
            result = setup_page.exec_()
            print("Setup page closed, result:", result)

            if result == QDialog.Accepted:
                self.show()
            else:
                print("Setup page was not accepted, check for issues.")
        except Exception as e:
            print("Error showing setup page:", e)

    def updateProgressBar(self):
        value = self.progressBar.value() + 1
        if value > 100:
            self.progressBarTimer.stop()
            self.progressBar.setVisible(False)
            self.status.setText("")
            self.keyInput.setVisible(True)
            self.loginButton.setVisible(True)
        else:
            self.progressBar.setValue(value)

    def handle_login(self):
        try:
            license_key = self.keyInput.text().strip()
            if license_key:
                self.verify_license(license_key, prompt_on_fail=True)
            else:
                self.show_custom_message("Please enter a valid key")
        except Exception as error:
            print(str(error))

    def verify_license(self, license_key, prompt_on_fail=False):
        result = self.api.license(license_key)
        if result:
            keyring.set_password("BNET GEN", "license_key", license_key)
            self.login_successful.emit('Login successful')
            self.close()
            return True
        else:
            if prompt_on_fail:
                self.show_custom_message("The provided key is invalid. Please try again.")
            return False

    def check_saved_license_and_login(self):
        saved_key = keyring.get_password("BNET GEN", "license_key")
        if saved_key:
            return self.verify_license(saved_key, prompt_on_fail=False)
        return False

    def show_custom_message(self, message):
        QTimer.singleShot(0, lambda: self._show_message(message))

    def _show_message(self, message):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.NoIcon)
        msg_box.setText(message)
        msg_box.setWindowTitle("Input Error")
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.button(QMessageBox.Ok).setText("OK")

        msg_box.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)

        msg_box.setModal(True)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #2c2c2c;  /* Gray background to match login UI */
                color: white;  /* White text */
                font-size: 16px;
            }
            QMessageBox QLabel {
                color: white;  /* Ensures that labels are explicitly white */
            }
            QPushButton {
                background-color: #27ae60;  /* Green button */
                color: white;  /* White text on buttons */
                border-radius: 5px;
                padding: 6px;
                min-width: 60px;
            }
            QPushButton:hover {
                background-color: #2ecc71;  /* Lighter green on hover */
            }
        """)

        msg_box.exec_()


class SetupPage(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setup")
        self.resize(600, 350)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)

        self.setStyleSheet("""
            QDialog {
                background-color: #2c2c2c;
                border-radius: 50px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.5);
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        title = QLabel("Welcome to BNET Gen!")
        title.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: white;
                padding-bottom: 10px;
            }
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        steps = [
            "2. Enter the key into the license key input field on the login screen that appears after you click below.",
            "3. You need residential proxies, captcha balance, sms balance, and kopeechka balance or use own emails (outlook or gmx).",
            "4. Fill out the settings to your liking and put API KEYS where they are labeled.",
            "5. On the right side of the UI it will display balance info and creation stats.",
            "6. When filling SMS Country info needs to be as follows, country ID for smshub like 22 for Vietnam, 5SIM lowercase russia for Russia, SMSPVA like FR for France.",
            "7. For the wait code sec field that is how many seconds to wait for sms so enter 30 for example 30 seconds.",
            "8. If you don't have your own emails the default will be Kopeechka and that will work but you can only access emails for short time. So it is best to use own emails.",
            "9 Proxy supported formats are as follows hostname:port:username:password, username:password@hostname:port, and ip:port"
        ]
        for step in steps:
            step_label = QLabel(step)
            step_label.setStyleSheet("color: #CCCCCC; padding: 3px; font-size: 14px;")
            step_label.setWordWrap(True)
            layout.addWidget(step_label)

        links_title = QLabel("Useful Links")
        links_title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: white;
                margin-top: 20px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(links_title)

        links_info = [
            ("Captcha", "https://bestcaptchasolver.com/"),
            ("Kopeechka", "https://kopeechka.store/"),
            ("SMSPVA", "https://smspva.com/"),
            ("SMSHUB", "https://smshub.org/"),
            ("5SIM", "https://5sim.net/")
        ]
        for name, url in links_info:
            link_label = QLabel(f"<a href='{url}' style='color: #27ae60; text-decoration: none;'>{name}</a>")
            link_label.setOpenExternalLinks(True)
            link_label.setStyleSheet("font-size: 14px; color: white;")
            layout.addWidget(link_label)

        continue_button = QPushButton("Continue to Application")
        continue_button.setCursor(QCursor(Qt.PointingHandCursor))
        continue_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                padding: 12px 20px;
                border-radius: 10px;
                font-size: 16px;
                font-family: 'Roboto', sans-serif;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        continue_button.clicked.connect(self.close)
        layout.addWidget(continue_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)
