
from PySide6.QtWidgets import QApplication
from api import keyauthapp
from LoginForm import LoginWindow
from MainWindow import MainWindow
import sys





if __name__ == "__main__":
    app = QApplication(sys.argv)

    login_window = LoginWindow(keyauthapp)

    def show_main_window(message):
        print(message)
        main_window = MainWindow(keyauthapp)
        main_window.show()
        login_window.close()

    login_window.login_successful.connect(show_main_window)
    if not login_window.check_saved_license_and_login():
        login_window.show()
    sys.exit(app.exec())
