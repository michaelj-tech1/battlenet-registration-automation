
import base64
import ctypes
import re
import sys
import keyring
import psutil
from PySide6 import QtCore
from PySide6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from BalanceFether import BalanceFetcher
import configparser
from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize,
    Qt)
from PySide6.QtGui import (QColor, QCursor, QFont, QIcon,
                           QPainter, QMouseEvent)
from PySide6.QtWidgets import (QCheckBox, QFrame, QGridLayout, QGroupBox,
    QHBoxLayout, QLabel, QLineEdit, QMainWindow,
    QPushButton, QScrollArea, QSizePolicy, QSpacerItem,
    QStackedWidget, QTextEdit, QVBoxLayout, QWidget)
from PySide6.QtCore import Qt, Signal, QThread, QObject, QMutex
import threading
import resources_rc
import time
import json
import os
from PySide6.QtCore import QObject, QTimer, QCoreApplication
from SignUp import SignUpThreads, Config

SECRET_KEY = 'X3lqH71tQw1nKPsk9dLcbNm0VRZoJx2G'

def xor_encrypt_decrypt(input_string, key=SECRET_KEY):
    """Encrypt or decrypt input string using XOR and a secret key"""
    return ''.join(chr(ord(c) ^ ord(key[i % len(key)])) for i, c in enumerate(input_string))

def encrypt(plaintext):
    """Encrypt plaintext using XOR and Base64 encode"""
    xor_encrypted = xor_encrypt_decrypt(plaintext)
    return base64.b64encode(xor_encrypted.encode('utf-8')).decode('utf-8')

def decrypt(ciphertext):
    """Decrypt Base64 encoded ciphertext using XOR"""
    decoded_ciphertext = base64.b64decode(ciphertext).decode('utf-8')
    return xor_encrypt_decrypt(decoded_ciphertext)



class FAQPage(QWidget):
    def __init__(self,faqs):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        for question, answer in faqs:
            section = self.create_collapsible_section(question, answer)
            layout.addWidget(section)

        layout.addStretch()

    def create_collapsible_section(self, question, answer):
        section = QWidget()

        section_layout = QVBoxLayout()
        section_layout
        section.setLayout(section_layout)
        question_button = QPushButton(question)
        question_button.setStyleSheet("text-align: left; padding: 10px;")
        question_button.setCheckable(True)
        question_button.setChecked(False)

        section_layout.addWidget(question_button)

        answer_label = QLabel(answer)
        answer_label.setWordWrap(True)
        answer_label.setVisible(False)
        section_layout.addWidget(answer_label)

        def toggle_answer(checked):
            answer_label.setVisible(checked)

        question_button.toggled.connect(toggle_answer)

        section.setStyleSheet("""
            QPushButton {
                background-color: #2c2c2c; 
                color: white; 
                border: none; 
                font-size: 14px;
                text-align: left;
            }
            QPushButton:checked {
                background-color: #666;
            }
            QLabel {
                color: white;
                background-color: #2c2c2c;
                padding: 10px;
                padding-left:20px;
                border-radius: 5px;
            }
            QWidget {
               background-color: #2c2c2c;
                border-radius: 5px;
                              
                
            }
            
        """)

        return section


class OneTimeKeyChecker(QObject):
    def __init__(self, keyauthapp):
        super().__init__()
        self.keyauthapp = keyauthapp
        if not self.check_saved_license_and_login():
            print("License key validation failed. Exiting application...")
            QCoreApplication.quit()

    def check_saved_license_and_login(self):
        saved_key = keyring.get_password("BNET GEN", "license_key")
        if saved_key:
            return self.verify_license(saved_key)
        return False

    def verify_license(self, license_key):
        result = self.keyauthapp.license(license_key)
        if result:
            keyring.set_password("BNET GEN", "license_key", license_key)
            return True
        return False


class ContinuousKeyChecker(QObject):
    def __init__(self, keyauthapp):
        super().__init__()
        self.keyauthapp = keyauthapp
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_key)
        self.timer.start(600000)

    def check_key(self):
        if not self.check_saved_license_and_login():
            print("License key validation failed. Exiting application...")
            QCoreApplication.quit()

    def check_saved_license_and_login(self):
        saved_key = keyring.get_password("BNET GEN", "license_key")
        if saved_key:
            return self.verify_license(saved_key)
        return False

    def verify_license(self, license_key):
        result = self.keyauthapp.license(license_key)
        if result:
            keyring.set_password("BNET GEN", "license_key", license_key)
            return True
        return False


class SecurityMonitor(QObject):
    def __init__(self):
        super().__init__()
        self.suspicious_tools = {
            'network': [
                'wireshark', 'fiddler', 'charles', 'burpsuite', 'tcpdump',
                'networkminer', 'mitmproxy', 'etherape', 'ngrep', 'kismet', 'snort', 'tshark',
                'netwitness', 'cain', 'nmap'
            ],
            'debugging': [
                'ollydbg', 'idaq', 'idaq64', 'idaw', 'idaw64', 'x32dbg', 'x64dbg', 'gdb',
                'windbg', 'softice', 'frida', 'radare2', 'peid', 'hex-rays', 'cheat engine',
                'process hacker', 'immunity debugger'
            ]
        }
        self.common_ports = [8888, 8080]
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.monitor_security)
        self.timer.start(3000)

    def monitor_security(self):
        if not self.perform_security_check():
            print("Security issue detected. Exiting application...")
            QCoreApplication.exit(1)

    def perform_security_check(self):
        if self.is_tool_running() or self.detect_debugger() or self.check_network_traffic():
            return False
        return True

    def is_tool_running(self):
        for category, tools in self.suspicious_tools.items():
            for process in psutil.process_iter(['name']):
                if any(tool.lower() in process.info['name'].lower() for tool in tools):
                    print(f"Suspicious tool detected: {process.info['name']}")
                    return True
        return False

    def detect_debugger(self):
        if sys.platform == 'win32':
            if ctypes.windll.kernel32.IsDebuggerPresent():
                print("Debugger is detected!")
                return True

            dr0 = ctypes.c_int()
            dr1 = ctypes.c_int()
            dr2 = ctypes.c_int()
            dr3 = ctypes.c_int()
            context = ctypes.windll.kernel32.GetCurrentThread()
            if ctypes.windll.kernel32.GetThreadContext(context, ctypes.byref(dr0)):
                if any([dr0.value, dr1.value, dr2.value, dr3.value]):
                    print("Hardware breakpoints detected!")
                    return True
        return False

    def check_network_traffic(self):
        for conn in psutil.net_connections(kind='inet'):
            if conn.laddr.port in self.common_ports:
                print(f"Unusual network traffic on port {conn.laddr.port}")
                return True
        return False


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1041, 646)
        MainWindow.setMinimumSize(QSize(1041, 646))
        self.styleSheet = QWidget(MainWindow)
        self.styleSheet.setObjectName(u"styleSheet")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        self.styleSheet.setFont(font)
        self.styleSheet.setStyleSheet("""
        /* General UI styles */
        QWidget {
            color: rgb(0, 0, 0);
            font: 10pt "Segoe UI";
        }

        QToolTip {
            color: #ffffff;
            background-color: rgba(33, 37, 43, 180);
            border: 1px solid rgb(44, 49, 58);
            background-image: none;
            background-position: left center;
            background-repeat: no-repeat;
            border-left: 4px solid #2c2c2c;
            text-align: left;
            padding-left: 10px;
            margin: 0px;
        }

        #bgApp {
            background-color: #1f1f1f;
            border: 1px solid rgb(44, 49, 58);
        }

        #leftMenuBg {
            background-color: #2c2c2c;
        }

        #topMenu .QPushButton {
            background-position: left center;
            background-repeat: no-repeat;
            border: none;
            border-left: 22px solid transparent;
            background-color: transparent;
            text-align: left;
            color: rgb(113, 126, 149);
            padding-left: 44px;
        }

        #topMenu .QPushButton:hover {
            background-color: #1f1f1f;
            color:white;
        }

        #topMenu .QPushButton:pressed {
            background-color: rgb(85, 170, 255);
            color: rgb(255, 255, 255);
        }

        #toggleButton {
            background-position: left center;
            background-repeat: no-repeat;
            border: none;
            border-left: 20px solid transparent;
            background-color: #1f1f1f;
            text-align: left;
            padding-left: 44px;
            color: rgb(113, 126, 149);
        }

        #toggleButton:hover {
            color: white;
        }

        #toggleButton:pressed {
            background-color: rgb(85, 170, 255);
        }

        #contentBottom {
            border-top: 3px solid rgb(44, 49, 58);
        }

        #rightButtons .QPushButton {
            background-color: white; 
            border: none;  
            border-radius: 5px;
        }

        #rightButtons .QPushButton:hover {
            background-color: #2c2c2c; 
            border-style: solid; 
            border-radius: 4px;
        }

        #rightButtons .QPushButton:pressed {
            background-color: rgb(23, 26, 30); 
            border-style: solid; 
            border-radius: 4px;
        }

        /* Scrollbar styles */
        QScrollBar:vertical {
            border: none;
            background: #333;
            width: 10px;
            margin: 10px 0 10px 0;
            border-radius: 5px;
        }

        QScrollBar::handle:vertical {
            background: #555;
            min-height: 20px;
            border-radius: 5px;
        }

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            border: none;
            background: none;
        }

        QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
            width: 0px;
            height: 0px;
            background: none;
        }

        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: none;
        }
        """)

        self.appMargins = QVBoxLayout(self.styleSheet)
        self.appMargins.setSpacing(0)
        self.appMargins.setObjectName(u"appMargins")
        self.appMargins.setContentsMargins(0, 0, 0, 0)
        self.bgApp = QFrame(self.styleSheet)
        self.bgApp.setObjectName(u"bgApp")
        self.bgApp.setStyleSheet(u"")
        self.bgApp.setFrameShape(QFrame.NoFrame)
        self.bgApp.setFrameShadow(QFrame.Raised)
        self.appLayout = QHBoxLayout(self.bgApp)
        self.appLayout.setSpacing(0)
        self.appLayout.setObjectName(u"appLayout")
        self.appLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenuBg = QFrame(self.bgApp)
        self.leftMenuBg.setObjectName(u"leftMenuBg")
        self.leftMenuBg.setEnabled(True)
        self.leftMenuBg.setMinimumSize(QSize(60, 0))
        self.leftMenuBg.setMaximumSize(QSize(60, 16777215))
        self.leftMenuBg.setFrameShape(QFrame.NoFrame)
        self.leftMenuBg.setFrameShadow(QFrame.Raised)
        self.verticalLayout_3 = QVBoxLayout(self.leftMenuBg)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.topLogoInfo = QFrame(self.leftMenuBg)
        self.topLogoInfo.setObjectName(u"topLogoInfo")
        self.topLogoInfo.setMinimumSize(QSize(271, 50))
        self.topLogoInfo.setMaximumSize(QSize(16777215, 50))
        self.topLogoInfo.setStyleSheet(u"background-color: #2c2c2c;")
        self.topLogoInfo.setFrameShape(QFrame.NoFrame)
        self.topLogoInfo.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_11 = QHBoxLayout(self.topLogoInfo)
        self.horizontalLayout_11.setSpacing(28)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(17, 0, 0, 0)
        self.label = QLabel(self.topLogoInfo)
        self.label.setObjectName(u"label")
        self.label.setStyleSheet(u"")
        self.horizontalLayout_11.addWidget(self.label)
        self.label_19 = QLabel(self.topLogoInfo)
        self.label_19.setObjectName(u"label_19")
        self.label_19.setStyleSheet(u"")
        self.horizontalLayout_11.addWidget(self.label_19)
        self.horizontalSpacer_2 = QSpacerItem(19, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.horizontalLayout_11.addItem(self.horizontalSpacer_2)
        self.verticalLayout_3.addWidget(self.topLogoInfo)
        self.leftMenuFrame = QFrame(self.leftMenuBg)
        self.leftMenuFrame.setObjectName(u"leftMenuFrame")
        self.leftMenuFrame.setFrameShape(QFrame.NoFrame)
        self.leftMenuFrame.setFrameShadow(QFrame.Raised)
        self.verticalMenuLayout = QVBoxLayout(self.leftMenuFrame)
        self.verticalMenuLayout.setSpacing(0)
        self.verticalMenuLayout.setObjectName(u"verticalMenuLayout")
        self.verticalMenuLayout.setContentsMargins(0, 0, 0, 0)
        self.toggleBox = QFrame(self.leftMenuFrame)
        self.toggleBox.setObjectName(u"toggleBox")
        self.toggleBox.setMaximumSize(QSize(16777215, 45))
        self.toggleBox.setFrameShape(QFrame.NoFrame)
        self.toggleBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_4 = QVBoxLayout(self.toggleBox)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.toggleButton = QPushButton(self.toggleBox)
        self.toggleButton.setObjectName(u"toggleButton")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.toggleButton.sizePolicy().hasHeightForWidth())
        self.toggleButton.setSizePolicy(sizePolicy)
        self.toggleButton.setMinimumSize(QSize(0, 45))
        self.toggleButton.setFont(font)
        self.toggleButton.setCursor(QCursor(Qt.PointingHandCursor))
        self.toggleButton.setLayoutDirection(Qt.LeftToRight)
        self.toggleButton.setStyleSheet(u"background-image: url(:/Icons/menu.png);")
        icon = QIcon()
        icon.addFile(u":/icons/icon_minimize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.toggleButton.setIcon(icon)
        self.verticalLayout_4.addWidget(self.toggleButton)
        self.verticalMenuLayout.addWidget(self.toggleBox)
        self.topMenu = QFrame(self.leftMenuFrame)
        self.topMenu.setObjectName(u"topMenu")
        self.topMenu.setFrameShape(QFrame.NoFrame)
        self.topMenu.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.topMenu)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.btnAccountGenerator = QPushButton(self.topMenu)
        self.btnAccountGenerator.setObjectName(u"btnAccountGenerator")
        sizePolicy.setHeightForWidth(self.btnAccountGenerator.sizePolicy().hasHeightForWidth())
        self.btnAccountGenerator.setSizePolicy(sizePolicy)
        self.btnAccountGenerator.setMinimumSize(QSize(0, 45))
        self.btnAccountGenerator.setFont(font)
        self.btnAccountGenerator.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnAccountGenerator.setLayoutDirection(Qt.LeftToRight)
        self.btnAccountGenerator.setStyleSheet(u"background-image: url(:/Icons/home.png);")
        self.verticalLayout.addWidget(self.btnAccountGenerator)
        self.btnAccountBlock = QPushButton(self.topMenu)
        self.btnAccountBlock.setObjectName(u"btnAccountBlock")
        sizePolicy.setHeightForWidth(self.btnAccountBlock.sizePolicy().hasHeightForWidth())
        self.btnAccountBlock.setSizePolicy(sizePolicy)
        self.btnAccountBlock.setMinimumSize(QSize(0, 45))
        self.btnAccountBlock.setFont(font)
        self.btnAccountBlock.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnAccountBlock.setLayoutDirection(Qt.LeftToRight)
        self.btnAccountBlock.setStyleSheet(u"background-image: url(:/Icons/check-circle.png);")
        self.verticalLayout.addWidget(self.btnAccountBlock)
        self.btnFaq = QPushButton(self.topMenu)
        self.btnFaq.setObjectName(u"btnFaq")
        sizePolicy.setHeightForWidth(self.btnFaq.sizePolicy().hasHeightForWidth())
        self.btnFaq.setSizePolicy(sizePolicy)
        self.btnFaq.setMinimumSize(QSize(0, 45))
        self.btnFaq.setFont(font)
        self.btnFaq.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnFaq.setLayoutDirection(Qt.LeftToRight)
        self.btnFaq.setStyleSheet(u"background-image: url(:/Icons/pencil.png);")
        self.verticalLayout.addWidget(self.btnFaq)
        self.verticalMenuLayout.addWidget(self.topMenu, 0, Qt.AlignTop)
        self.verticalLayout_3.addWidget(self.leftMenuFrame)
        self.appLayout.addWidget(self.leftMenuBg)
        self.contentBox = QFrame(self.bgApp)
        self.contentBox.setObjectName(u"contentBox")
        self.contentBox.setFrameShape(QFrame.NoFrame)
        self.contentBox.setFrameShadow(QFrame.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.contentBox)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.contentTopBg = QFrame(self.contentBox)
        self.contentTopBg.setObjectName(u"contentTopBg")
        self.contentTopBg.setMinimumSize(QSize(0, 50))
        self.contentTopBg.setMaximumSize(QSize(16777215, 50))
        self.contentTopBg.setStyleSheet(u"background-color: #2c2c2c;")
        self.contentTopBg.setFrameShape(QFrame.NoFrame)
        self.contentTopBg.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.contentTopBg)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 10, 0)
        self.leftBox = QFrame(self.contentTopBg)
        self.leftBox.setObjectName(u"leftBox")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.leftBox.sizePolicy().hasHeightForWidth())
        self.leftBox.setSizePolicy(sizePolicy1)
        self.leftBox.setFrameShape(QFrame.NoFrame)
        self.leftBox.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.leftBox)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.titleRightInfo = QLabel(self.leftBox)
        self.titleRightInfo.setObjectName(u"titleRightInfo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.titleRightInfo.sizePolicy().hasHeightForWidth())
        self.titleRightInfo.setSizePolicy(sizePolicy2)
        self.titleRightInfo.setMaximumSize(QSize(16777215, 45))
        self.titleRightInfo.setFont(font)
        self.titleRightInfo.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.horizontalLayout_3.addWidget(self.titleRightInfo)
        self.horizontalLayout.addWidget(self.leftBox)

        self.rightButtons = QFrame(self.contentTopBg)
        self.rightButtons.setObjectName(u"rightButtons")
        self.rightButtons.setMinimumSize(QSize(0, 28))
        self.rightButtons.setStyleSheet(u"/* Top Buttons */\n"
"QPushButton { background-color: transparent; border: none;  border-radius: 5px; }\n"
"QPushButton:hover {            background-color: #1f1f1f; border-style: solid; border-radius: 4px; }\n"
"QPushButton:pressed { background-color: rgb(23, 26, 30); border-style: solid; border-radius: 4px; }")
        self.rightButtons.setFrameShape(QFrame.NoFrame)
        self.rightButtons.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_2 = QHBoxLayout(self.rightButtons)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.minimizeAppBtn = QPushButton(self.rightButtons)
        self.minimizeAppBtn.setObjectName(u"minimizeAppBtn")
        self.minimizeAppBtn.setMinimumSize(QSize(28, 28))
        self.minimizeAppBtn.setMaximumSize(QSize(28, 28))
        self.minimizeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon1 = QIcon()
        icon1.addFile(u":/Icons/minimize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.minimizeAppBtn.setIcon(icon1)
        self.minimizeAppBtn.setIconSize(QSize(20, 20))
        self.horizontalLayout_2.addWidget(self.minimizeAppBtn)
        self.maximizeRestoreAppBtn = QPushButton(self.rightButtons)
        self.maximizeRestoreAppBtn.setObjectName(u"maximizeRestoreAppBtn")
        self.maximizeRestoreAppBtn.setMinimumSize(QSize(28, 28))
        self.maximizeRestoreAppBtn.setMaximumSize(QSize(28, 28))
        font1 = QFont()
        font1.setFamilies([u"Segoe UI"])
        font1.setPointSize(10)
        font1.setBold(False)
        font1.setItalic(False)
        font1.setStyleStrategy(QFont.PreferDefault)
        self.maximizeRestoreAppBtn.setFont(font1)
        self.maximizeRestoreAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon2 = QIcon()
        icon2.addFile(u":/Icons/maximize.png", QSize(), QIcon.Normal, QIcon.Off)
        self.maximizeRestoreAppBtn.setIcon(icon2)
        self.maximizeRestoreAppBtn.setIconSize(QSize(20, 20))

        self.horizontalLayout_2.addWidget(self.maximizeRestoreAppBtn)

        self.closeAppBtn = QPushButton(self.rightButtons)
        self.closeAppBtn.setObjectName(u"closeAppBtn")
        self.closeAppBtn.setMinimumSize(QSize(28, 28))
        self.closeAppBtn.setMaximumSize(QSize(28, 28))
        self.closeAppBtn.setCursor(QCursor(Qt.PointingHandCursor))
        icon3 = QIcon()
        icon3.addFile(u":/Icons/close.png", QSize(), QIcon.Normal, QIcon.Off)
        self.closeAppBtn.setIcon(icon3)
        self.closeAppBtn.setIconSize(QSize(20, 20))
        self.horizontalLayout_2.addWidget(self.closeAppBtn)
        self.horizontalLayout.addWidget(self.rightButtons, 0, Qt.AlignRight)
        self.verticalLayout_2.addWidget(self.contentTopBg)
        self.contentBottom = QFrame(self.contentBox)
        self.contentBottom.setObjectName(u"contentBottom")
        self.contentBottom.setFrameShape(QFrame.NoFrame)
        self.contentBottom.setFrameShadow(QFrame.Raised)
        self.verticalLayout_6 = QVBoxLayout(self.contentBottom)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.content = QFrame(self.contentBottom)
        self.content.setObjectName(u"content")
        self.content.setFrameShape(QFrame.NoFrame)
        self.content.setFrameShadow(QFrame.Raised)
        self.verticalLayout_5 = QVBoxLayout(self.content)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(15, 15, 15, 15)
        self.stackedWidget = QStackedWidget(self.content)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.stackedWidget.setStyleSheet(u"background-color:transparent;")
        self.AccountGeneratePage = QWidget()
        self.AccountGeneratePage.setObjectName(u"AccountGeneratePage")
        self.verticalLayout_8 = QVBoxLayout(self.AccountGeneratePage)
        self.verticalLayout_8.setSpacing(7)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(self.AccountGeneratePage)
        self.frame.setObjectName(u"frame")
        self.frame.setStyleSheet(u"QGroupBox {\n"
"                color: #ffffff;\n"
"                font-size: 16px;\n"
"                font-weight: bold;\n"
"                border: 1px solid #ffffff;\n"
"                border-radius: 10px;\n"
"                margin-top: 10px;\n"
"            }\n"
"            QGroupBox::title {\n"
"                subcontrol-origin: margin;\n"
"                subcontrol-position: top left;\n"
"                padding: 0 3px;\n"
"            }\n"
"\n"
"QLineEdit {\n"
"                        background-color: #333333;\n"
"                        border: 1px solid #444444;\n"
"                        border-radius: 5px;\n"
"                        padding: 4px;\n"
"	font: 8pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"                    }\n"
"QLineEdit:hover {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
"                    QLineEdit:focus {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
""
                        "QLabel{\n"
"	font: 8pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"}\n"
"\n"
"QCheckBox {\n"
"                        color: white;\n"
"                        font-size: 14px;\n"
"                    }\n"
"                    QCheckBox::indicator {\n"
"                        width: 20px;\n"
"                        height: 20px;\n"
"                    }\n"
"\n"
"                    QCheckBox::indicator:unchecked {\n"
"                        background-color: #3a3a3a;\n"
"                        border: 1px solid #555555;\n"
"                        border-radius: 4px;\n"
"                    }\n"
"                    QCheckBox::indicator:checked {\n"
"                        background-color: #27ae60;\n"
"                        border: 1px solid #27ae60;\n"
"                        border-radius: 4px;\n"
"                        image: url(icons/checkmark.png);\n"
"                    }\n"
"\n"
"")
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_4 = QHBoxLayout(self.frame)
        self.horizontalLayout_4.setSpacing(7)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.AccountSettingGroupBox = QGroupBox(self.frame)
        self.AccountSettingGroupBox.setObjectName(u"AccountSettingGroupBox")
        self.AccountSettingGroupBox.setStyleSheet(u"color:white;")
        self.verticalLayout_9 = QVBoxLayout(self.AccountSettingGroupBox)
        self.verticalLayout_9.setSpacing(7)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(15, 15, 15, 15)
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setSpacing(0)
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.gridLayout_7.setContentsMargins(-1, 3, -1, 5)
        self.chkBoxUseProxies = QCheckBox(self.AccountSettingGroupBox)
        self.chkBoxUseProxies.setObjectName(u"chkBoxUseProxies")
        self.chkBoxUseProxies.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_7.addWidget(self.chkBoxUseProxies, 0, 0, 1, 1)

        self.chkBoxUseEmailstxt = QCheckBox(self.AccountSettingGroupBox)
        self.chkBoxUseEmailstxt.setObjectName(u"chkBoxUseEmailstxt")
        self.chkBoxUseEmailstxt.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_7.addWidget(self.chkBoxUseEmailstxt, 0, 1, 1, 1)

        self.gridLayout_7.setColumnStretch(0, 1)
        self.gridLayout_7.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_7)

        self.gridLayout = QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_2 = QLabel(self.AccountSettingGroupBox)
        self.label_2.setObjectName(u"label_2")

        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)

        self.txtAccountToCreate = QLineEdit(self.AccountSettingGroupBox)
        self.txtAccountToCreate.setObjectName(u"txtAccountToCreate")
        font2 = QFont()
        font2.setFamilies([u"Segoe UI"])
        font2.setPointSize(8)
        font2.setBold(False)
        font2.setItalic(False)
        self.txtAccountToCreate.setFont(font2)

        self.gridLayout.addWidget(self.txtAccountToCreate, 0, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout)

        self.gridLayout_2 = QGridLayout()
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label_3 = QLabel(self.AccountSettingGroupBox)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_2.addWidget(self.label_3, 0, 0, 1, 1)

        self.txtThreadsToRun = QLineEdit(self.AccountSettingGroupBox)
        self.txtThreadsToRun.setObjectName(u"txtThreadsToRun")
        self.txtThreadsToRun.setFont(font2)

        self.gridLayout_2.addWidget(self.txtThreadsToRun, 0, 1, 1, 1)

        self.gridLayout_2.setColumnStretch(0, 1)
        self.gridLayout_2.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_2)

        self.gridLayout_3 = QGridLayout()
        self.gridLayout_3.setSpacing(0)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_4 = QLabel(self.AccountSettingGroupBox)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_3.addWidget(self.label_4, 0, 0, 1, 1)

        self.txtAccountUsername = QLineEdit(self.AccountSettingGroupBox)
        self.txtAccountUsername.setObjectName(u"txtAccountUsername")
        self.txtAccountUsername.setFont(font2)

        self.gridLayout_3.addWidget(self.txtAccountUsername, 0, 1, 1, 1)

        self.gridLayout_3.setColumnStretch(0, 1)
        self.gridLayout_3.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_3)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.label_5 = QLabel(self.AccountSettingGroupBox)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_4.addWidget(self.label_5, 0, 0, 1, 1)

        self.txtKopeechkaApiKey = QLineEdit(self.AccountSettingGroupBox)
        self.txtKopeechkaApiKey.setObjectName(u"txtKopeechkaApiKey")
        self.txtKopeechkaApiKey.setFont(font2)

        self.gridLayout_4.addWidget(self.txtKopeechkaApiKey, 0, 1, 1, 1)

        self.gridLayout_4.setColumnStretch(0, 1)
        self.gridLayout_4.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_4)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_6 = QLabel(self.AccountSettingGroupBox)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_5.addWidget(self.label_6, 0, 0, 1, 1)

        self.txtKopeechkEmailPref = QLineEdit(self.AccountSettingGroupBox)
        self.txtKopeechkEmailPref.setObjectName(u"txtKopeechkEmailPref")
        self.txtKopeechkEmailPref.setFont(font2)

        self.gridLayout_5.addWidget(self.txtKopeechkEmailPref, 0, 1, 1, 1)

        self.gridLayout_5.setColumnStretch(0, 1)
        self.gridLayout_5.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_5)

        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setSpacing(0)
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_7 = QLabel(self.AccountSettingGroupBox)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)

        self.gridLayout_6.setColumnStretch(0, 1)
        self.gridLayout_6.setColumnStretch(1, 1)

        self.verticalLayout_9.addLayout(self.gridLayout_6)


        self.horizontalLayout_4.addWidget(self.AccountSettingGroupBox)

        self.SMSSettingGroupBox = QGroupBox(self.frame)
        self.SMSSettingGroupBox.setObjectName(u"SMSSettingGroupBox")
        self.SMSSettingGroupBox.setStyleSheet(u"color:white;")
        self.verticalLayout_10 = QVBoxLayout(self.SMSSettingGroupBox)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setSpacing(0)
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.gridLayout_8.setContentsMargins(-1, 0, -1, -1)

        self.captchaBorderFrame = QFrame(self.SMSSettingGroupBox)
        self.captchaBorderFrame.setFrameShape(QFrame.StyledPanel)
        self.captchaBorderFrame.setFrameShadow(QFrame.Raised)

        captchaLayout = QVBoxLayout(self.captchaBorderFrame)

        checkboxLayout = QHBoxLayout()
        self.useBestCapsovler = QCheckBox("Best Capsolver")
        self.useBestCapsovler.setCursor(QCursor(Qt.PointingHandCursor))
        checkboxLayout.addWidget(self.useBestCapsovler)
        self.useTwoCaptcha = QCheckBox("2Captcha")
        self.useTwoCaptcha.setCursor(QCursor(Qt.PointingHandCursor))
        checkboxLayout.addWidget(self.useTwoCaptcha)

        captchaLayout.addLayout(checkboxLayout)

        self.txtCaptchaApiKey = QLineEdit()
        self.txtCaptchaApiKey.setPlaceholderText("Enter Captcha API Key")
        self.txtCaptchaApiKey.setFixedWidth(220)
        captchaLayout.addWidget(self.txtCaptchaApiKey)

        self.verticalLayout_10.insertWidget(0, self.captchaBorderFrame)

        self.chkBoxUseSMSApi = QCheckBox(self.SMSSettingGroupBox)
        self.chkBoxUseSMSApi.setObjectName(u"chkBoxUseSMSApi")
        self.chkBoxUseSMSApi.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_8.addWidget(self.chkBoxUseSMSApi, 0, 0, 1, 1)

        self.chkUseSMSPVA = QCheckBox(self.SMSSettingGroupBox)
        self.chkUseSMSPVA.setObjectName(u"chkUseSMSPVA")
        self.chkUseSMSPVA.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_8.addWidget(self.chkUseSMSPVA, 0, 1, 1, 1)

        self.gridLayout_8.setColumnStretch(0, 1)
        self.gridLayout_8.setColumnStretch(1, 1)

        self.verticalLayout_10.addLayout(self.gridLayout_8)

        self.gridLayout_9 = QGridLayout()
        self.gridLayout_9.setSpacing(0)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.gridLayout_9.setContentsMargins(-1, 3, -1, -1)
        self.chkBoxSMSHUB = QCheckBox(self.SMSSettingGroupBox)
        self.chkBoxSMSHUB.setObjectName(u"chkBoxSMSHUB")
        self.chkBoxSMSHUB.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_9.addWidget(self.chkBoxSMSHUB, 0, 0, 1, 1)

        self.chkBox5Sim = QCheckBox(self.SMSSettingGroupBox)
        self.chkBox5Sim.setObjectName(u"chkBox5Sim")
        self.chkBox5Sim.setCursor(QCursor(Qt.PointingHandCursor))

        self.gridLayout_9.addWidget(self.chkBox5Sim, 0, 1, 1, 1)

        self.gridLayout_9.setColumnStretch(0, 1)
        self.gridLayout_9.setColumnStretch(1, 1)

        self.verticalLayout_10.addLayout(self.gridLayout_9)

        self.gridLayout_10 = QGridLayout()
        self.gridLayout_10.setSpacing(0)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.label_8 = QLabel(self.SMSSettingGroupBox)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_10.addWidget(self.label_8, 0, 0, 1, 1)

        self.txtApiKey = QLineEdit(self.SMSSettingGroupBox)
        self.txtApiKey.setObjectName(u"txtApiKey")
        self.txtApiKey.setFont(font2)

        self.gridLayout_10.addWidget(self.txtApiKey, 0, 1, 1, 1)

        self.gridLayout_10.setColumnStretch(0, 1)
        self.gridLayout_10.setColumnStretch(1, 1)

        self.verticalLayout_10.addLayout(self.gridLayout_10)

        self.gridLayout_11 = QGridLayout()
        self.gridLayout_11.setSpacing(0)
        self.gridLayout_11.setObjectName(u"gridLayout_11")
        self.label_9 = QLabel(self.SMSSettingGroupBox)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_11.addWidget(self.label_9, 0, 0, 1, 1)

        self.txtSMSCountry = QLineEdit(self.SMSSettingGroupBox)
        self.txtSMSCountry.setObjectName(u"txtSMSCountry")
        self.txtSMSCountry.setFont(font2)

        self.gridLayout_11.addWidget(self.txtSMSCountry, 0, 1, 1, 1)

        self.gridLayout_11.setColumnStretch(0, 1)
        self.gridLayout_11.setColumnStretch(1, 1)

        self.verticalLayout_10.addLayout(self.gridLayout_11)

        self.gridLayout_14 = QGridLayout()
        self.gridLayout_14.setSpacing(0)
        self.gridLayout_14.setObjectName(u"gridLayout_14")
        self.label_20 = QLabel(self.SMSSettingGroupBox)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_14.addWidget(self.label_20, 0, 0, 1, 1)

        self.txtWaitCodeSec = QLineEdit(self.SMSSettingGroupBox)
        self.txtWaitCodeSec.setObjectName(u"txtWaitCodeSec")
        self.txtWaitCodeSec.setFont(font2)

        self.gridLayout_14.addWidget(self.txtWaitCodeSec, 0, 1, 1, 1)

        self.gridLayout_14.setColumnStretch(0, 1)
        self.gridLayout_14.setColumnStretch(1, 1)

        self.verticalLayout_10.addLayout(self.gridLayout_14)


        self.horizontalLayout_4.addWidget(self.SMSSettingGroupBox)

        self.frame_4 = QFrame(self.frame)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setFrameShape(QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QFrame.Raised)
        self.verticalLayout_7 = QVBoxLayout(self.frame_4)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.InfoBox1GroupBox = QGroupBox(self.frame_4)
        self.InfoBox1GroupBox.setObjectName(u"InfoBox1GroupBox")
        self.InfoBox1GroupBox.setMaximumSize(QSize(16777215, 16777215))
        self.InfoBox1GroupBox.setStyleSheet(u"QGroupBox{color:white;}\n"
"QLineEdit {\n"
"                        background-color: #333333;\n"
"                        border: 1px solid #444444;\n"
"                        border-radius: 5px;\n"
"                        padding: 4px;\n"
"	font: 7pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"                    }\n"
"QLineEdit:hover {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
"                    QLineEdit:focus {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
"QLabel{\n"
"	font: 7pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"}\n"
"")
        self.verticalLayout_17 = QVBoxLayout(self.InfoBox1GroupBox)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.gridLayout_13 = QGridLayout()
        self.gridLayout_13.setObjectName(u"gridLayout_13")
        self.label_14 = QLabel(self.InfoBox1GroupBox)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_13.addWidget(self.label_14, 0, 0, 1, 1)

        self.lblKopeechkaBalance = QLabel(self.InfoBox1GroupBox)
        self.lblKopeechkaBalance.setObjectName(u"lblKopeechkaBalance")

        self.gridLayout_13.addWidget(self.lblKopeechkaBalance, 0, 1, 1, 1)

        self.label_15 = QLabel(self.InfoBox1GroupBox)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_13.addWidget(self.label_15, 1, 0, 1, 1)

        self.lblCapsolverBalance = QLabel(self.InfoBox1GroupBox)
        self.lblCapsolverBalance.setObjectName(u"lblCapsolverBalance")

        self.gridLayout_13.addWidget(self.lblCapsolverBalance, 1, 1, 1, 1)

        self.label_16 = QLabel(self.InfoBox1GroupBox)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_13.addWidget(self.label_16, 2, 0, 1, 1)

        self.lblSMSPVABalance = QLabel(self.InfoBox1GroupBox)
        self.lblSMSPVABalance.setObjectName(u"lblSMSPVABalance")

        self.gridLayout_13.addWidget(self.lblSMSPVABalance, 2, 1, 1, 1)

        self.label_17 = QLabel(self.InfoBox1GroupBox)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_13.addWidget(self.label_17, 3, 0, 1, 1)

        self.lblSMSHUBBalance = QLabel(self.InfoBox1GroupBox)
        self.lblSMSHUBBalance.setObjectName(u"lblSMSHUBBalance")

        self.gridLayout_13.addWidget(self.lblSMSHUBBalance, 3, 1, 1, 1)

        self.label_18 = QLabel(self.InfoBox1GroupBox)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_13.addWidget(self.label_18, 4, 0, 1, 1)

        self.lbl5SimBalance = QLabel(self.InfoBox1GroupBox)
        self.lbl5SimBalance.setObjectName(u"lbl5SimBalance")

        self.gridLayout_13.addWidget(self.lbl5SimBalance, 4, 1, 1, 1)


        self.verticalLayout_17.addLayout(self.gridLayout_13)


        self.verticalLayout_7.addWidget(self.InfoBox1GroupBox)

        self.InfoBox2GroupBox = QGroupBox(self.frame_4)
        self.InfoBox2GroupBox.setObjectName(u"InfoBox2GroupBox")
        self.InfoBox2GroupBox.setStyleSheet(u"color:white;")
        self.verticalLayout_16 = QVBoxLayout(self.InfoBox2GroupBox)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.gridLayout_12 = QGridLayout()
        self.gridLayout_12.setObjectName(u"gridLayout_12")
        self.label_10 = QLabel(self.InfoBox2GroupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_12.addWidget(self.label_10, 0, 0, 1, 1)

        self.lblFailedAccounts = QLabel(self.InfoBox2GroupBox)
        self.lblFailedAccounts.setObjectName(u"lblFailedAccounts")

        self.gridLayout_12.addWidget(self.lblFailedAccounts, 0, 1, 1, 1)

        self.label_12 = QLabel(self.InfoBox2GroupBox)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_12.addWidget(self.label_12, 1, 0, 1, 1)

        self.lblMadeAccounts = QLabel(self.InfoBox2GroupBox)
        self.lblMadeAccounts.setObjectName(u"lblMadeAccounts")

        self.gridLayout_12.addWidget(self.lblMadeAccounts, 1, 1, 1, 1)

        self.label_13 = QLabel(self.InfoBox2GroupBox)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_12.addWidget(self.label_13, 2, 0, 1, 1)

        self.lblTotalAttempted = QLabel(self.InfoBox2GroupBox)
        self.lblTotalAttempted.setObjectName(u"lblTotalAttempted")

        self.gridLayout_12.addWidget(self.lblTotalAttempted, 2, 1, 1, 1)


        self.verticalLayout_16.addLayout(self.gridLayout_12)


        self.verticalLayout_7.addWidget(self.InfoBox2GroupBox)


        self.horizontalLayout_4.addWidget(self.frame_4)

        self.horizontalLayout_4.setStretch(0, 1)
        self.horizontalLayout_4.setStretch(1, 1)
        self.horizontalLayout_4.setStretch(2, 1)

        self.verticalLayout_8.addWidget(self.frame)

        self.frame_2 = QFrame(self.AccountGeneratePage)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 41))
        self.frame_2.setMaximumSize(QSize(16777215, 51))
        self.frame_2.setStyleSheet(u"QPushButton {\n"
"	border: 2px solid rgb(52, 59, 72);\n"
"	border-radius: 5px;	\n"
"	background-color: rgb(52, 59, 72);\n"
"color:white;\n"
"}\n"
"QPushButton:hover {\n"
"	background-color: rgb(57, 65, 80);\n"
"	border: 2px solid rgb(61, 70, 86);\n"
"}\n"
"QPushButton:pressed {	\n"
"	background-color: rgb(35, 40, 49);\n"
"	border: 2px solid rgb(43, 50, 61);\n"
"}")
        self.frame_2.setFrameShape(QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_6 = QHBoxLayout(self.frame_2)
        self.horizontalLayout_6.setSpacing(26)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.btnStart = QPushButton(self.frame_2)
        self.btnStart.setObjectName(u"btnStart")
        self.btnStart.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnStart.setMinimumSize(QSize(121, 41))
        self.btnStart.setMaximumSize(QSize(121, 41))
        self.btnStart.setStyleSheet(u"\n"
"QPushButton {\n"
"	border-radius: 10px;	\n"
"	background-color: #27AE61;\n"
"	color:white;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: rgb(30, 138, 75);\n"
"	border: 2px solid rgb(85, 170, 255);\n"
"\n"
"}\n"
"")

        self.horizontalLayout_6.addWidget(self.btnStart)

        self.btnStop = QPushButton(self.frame_2)
        self.btnStop.setObjectName(u"btnStop")
        self.btnStop.setMinimumSize(QSize(121, 41))
        self.btnStop.setMaximumSize(QSize(121, 41))
        self.btnStop.setFont(font)
        self.btnStop.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnStop.setStyleSheet(u"\n"
"QPushButton {\n"
"	border-radius: 10px;	\n"
"	background-color: #C1392B;\n"
"	color:white;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: rgb(170, 0, 0);\n"
"	border: 2px solid rgb(0, 170, 255);\n"
"	\n"
"}\n"
"")

        self.horizontalLayout_6.addWidget(self.btnStop)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer)


        self.verticalLayout_8.addWidget(self.frame_2)

        self.frame_3 = QFrame(self.AccountGeneratePage)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setStyleSheet(u"QTextEdit{\n"
"                border: 1px solid white;\n"
"                border-radius: 10px;\n"
"				background-color: #2c2c2c;\n"
"            color: white;\n"
"            font-family: Consolas, monospace;\n"
"            font-size: 14px;\n"
"padding:10px\n"
"\n"
"}\n"
"")
        self.frame_3.setFrameShape(QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_7 = QHBoxLayout(self.frame_3)
        self.horizontalLayout_7.setSpacing(5)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(0, 4, 0, 0)
        self.AccountGeneratorConsole = QTextEdit(self.frame_3)
        self.AccountGeneratorConsole.setObjectName("AccountGeneratorConsole")
        self.AccountGeneratorConsole.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.AccountGeneratorConsole)
        self.SecondConsole = QTextEdit(self.frame_3)
        self.SecondConsole.setObjectName("SecondConsole")
        self.SecondConsole.setReadOnly(True)

        self.horizontalLayout_7.addWidget(self.AccountGeneratorConsole)
        self.horizontalLayout_7.addWidget(self.SecondConsole)

        self.horizontalLayout_7.setStretch(0, 1)
        self.horizontalLayout_7.setStretch(1, 1)

        self.verticalLayout_8.addWidget(self.frame_3)
        self.verticalLayout_8.addWidget(self.frame_3)

        self.verticalLayout_8.setStretch(0, 1)
        self.verticalLayout_8.setStretch(2, 1)
        self.stackedWidget.addWidget(self.AccountGeneratePage)
        self.AccountBanCheckerPage = QWidget()
        self.AccountBanCheckerPage.setObjectName(u"AccountBanCheckerPage")
        self.AccountBanCheckerPage.setStyleSheet(u"QGroupBox {\n"
"                color: #ffffff;\n"
"                font-size: 16px;\n"
"                font-weight: bold;\n"
"                border: 1px solid #ffffff;\n"
"                border-radius: 10px;\n"
"                margin-top: 10px;\n"
"            }\n"
"            QGroupBox::title {\n"
"                subcontrol-origin: margin;\n"
"                subcontrol-position: top left;\n"
"                padding: 0 3px;\n"
"            }\n"
"\n"
"QLineEdit {\n"
"                        background-color: #333333;\n"
"                        border: 1px solid #444444;\n"
"                        border-radius: 5px;\n"
"                        padding: 4px;\n"
"	font: 8pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"                    }\n"
"QLineEdit:hover {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
"                    QLineEdit:focus {\n"
"                        border: 1px solid rgb(85, 170, 255);\n"
"                    }\n"
""
                        "QLabel{\n"
"	font: 8pt \"Segoe UI\";\n"
"                        color: #ffffff;\n"
"}\n"
"\n"
"\n"
"")
        self.verticalLayout_11 = QVBoxLayout(self.AccountBanCheckerPage)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.frame_9 = QFrame(self.AccountBanCheckerPage)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setMinimumSize(QSize(30, 30))
        self.frame_9.setFrameShape(QFrame.StyledPanel)
        self.frame_9.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_12 = QHBoxLayout(self.frame_9)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.label_92 = QLabel(self.frame_9)
        self.label_92.setObjectName(u"label_92")

        self.horizontalLayout_12.addWidget(self.label_92)


        self.verticalLayout_11.addWidget(self.frame_9)

        self.frame_5 = QFrame(self.AccountBanCheckerPage)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setEnabled(False)
        self.frame_5.setFrameShape(QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_8 = QHBoxLayout(self.frame_5)
        self.horizontalLayout_8.setSpacing(0)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.AccountBanCheckerGroupBox = QGroupBox(self.frame_5)
        self.AccountBanCheckerGroupBox.setObjectName(u"AccountBanCheckerGroupBox")
        self.AccountBanCheckerGroupBox.setMinimumSize(QSize(0, 151))
        self.AccountBanCheckerGroupBox.setMaximumSize(QSize(367, 16777215))
        self.AccountBanCheckerGroupBox.setStyleSheet(u"color:white;")
        self.verticalLayout_12 = QVBoxLayout(self.AccountBanCheckerGroupBox)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 11, 0, 7)
        self.frame_7 = QFrame(self.AccountBanCheckerGroupBox)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setMaximumSize(QSize(16777215, 16777215))
        self.frame_7.setFrameShape(QFrame.StyledPanel)
        self.frame_7.setFrameShadow(QFrame.Raised)
        self.verticalLayout_13 = QVBoxLayout(self.frame_7)
        self.verticalLayout_13.setSpacing(0)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(-1, 30, -1, 0)
        self.gridLayout_15 = QGridLayout()
        self.gridLayout_15.setObjectName(u"gridLayout_15")
        self.gridLayout_15.setHorizontalSpacing(20)
        self.gridLayout_15.setVerticalSpacing(0)
        self.txtThreads = QLineEdit(self.frame_7)
        self.txtThreads.setObjectName(u"txtThreads")
        self.txtThreads.setEnabled(False)
        self.txtThreads.setFont(font2)

        self.gridLayout_15.addWidget(self.txtThreads, 0, 1, 1, 1)

        self.label_11 = QLabel(self.frame_7)
        self.label_11.setObjectName(u"label_11")
        self.label_11.setEnabled(False)

        self.gridLayout_15.addWidget(self.label_11, 0, 0, 1, 1)


        self.verticalLayout_13.addLayout(self.gridLayout_15)


        self.verticalLayout_12.addWidget(self.frame_7)

        self.frame_8 = QFrame(self.AccountBanCheckerGroupBox)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setMaximumSize(QSize(16777215, 60))
        self.frame_8.setFrameShape(QFrame.StyledPanel)
        self.frame_8.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_9 = QHBoxLayout(self.frame_8)
        self.horizontalLayout_9.setSpacing(0)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.btnRun = QPushButton(self.frame_8)
        self.btnRun.setObjectName(u"btnRun")
        self.btnRun.setEnabled(False)
        self.btnRun.setMinimumSize(QSize(121, 41))
        self.btnRun.setMaximumSize(QSize(121, 41))
        self.btnRun.setCursor(QCursor(Qt.PointingHandCursor))
        self.btnRun.setStyleSheet(u"\n"
"QPushButton {\n"
"	border-radius: 10px;	\n"
"	background-color: #27AE61;\n"
"	color:white;\n"
"}\n"
"QPushButton:hover {\n"
"background-color: rgb(30, 138, 75);\n"
"	border: 2px solid rgb(85, 170, 255);\n"
"\n"
"}\n"
"")

        self.horizontalLayout_9.addWidget(self.btnRun)

        self.horizontalLayout_9.setStretch(0, 1)

        self.verticalLayout_12.addWidget(self.frame_8)


        self.horizontalLayout_8.addWidget(self.AccountBanCheckerGroupBox)


        self.verticalLayout_11.addWidget(self.frame_5)

        self.frame_6 = QFrame(self.AccountBanCheckerPage)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setEnabled(False)
        self.frame_6.setFrameShape(QFrame.StyledPanel)
        self.frame_6.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_10 = QHBoxLayout(self.frame_6)
        self.horizontalLayout_10.setSpacing(0)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(200, 31, 200, 66)
        self.txtEditConsole2 = QTextEdit(self.frame_6)
        self.txtEditConsole2.setObjectName(u"txtEditConsole2")
        self.txtEditConsole2.setEnabled(False)
        self.txtEditConsole2.setStyleSheet(u"QTextEdit{\n"
"                border: 1px solid white;\n"
"                border-radius: 10px;\n"
"				background-color: #2c2c2c;\n"
"            color: white;\n"
"            font-family: Consolas, monospace;\n"
"            font-size: 14px;\n"
"padding:10px\n"
"\n"
"}\n"
"")

        self.horizontalLayout_10.addWidget(self.txtEditConsole2)


        self.verticalLayout_11.addWidget(self.frame_6)

        self.stackedWidget.addWidget(self.AccountBanCheckerPage)
        self.FAQPage = QWidget()
        self.FAQPage.setObjectName(u"FAQPage")
        self.FAQPage.setStyleSheet(u"QGroupBox {\n"
"                color: #ffffff;\n"
"                font-size: 16px;\n"
"                font-weight: bold;\n"
"                border: 1px solid #ffffff;\n"
"                border-radius: 10px;\n"
"                margin-top: 10px;\n"
"            }\n"
"            QGroupBox::title {\n"
"                subcontrol-origin: margin;\n"
"                subcontrol-position: top left;\n"
"                padding: 0 3px;\n"
"            }")
        self.verticalLayout_14 = QVBoxLayout(self.FAQPage)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.FAQGroupBox = QGroupBox(self.FAQPage)
        self.FAQGroupBox.setObjectName(u"FAQGroupBox")
        self.verticalLayout_15 = QVBoxLayout(self.FAQGroupBox)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.verticalLayout_15.setContentsMargins(20, 20, 20, 20)
        self.scrollArea = QScrollArea(self.FAQGroupBox)
        self.scrollArea.setObjectName(u"scrollArea")
        self.scrollArea.setStyleSheet(u"border:none")
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.scrollAreaWidgetContents.setObjectName(u"scrollAreaWidgetContents")
        self.scrollAreaWidgetContents.setGeometry(QRect(0, 0, 885, 465))
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.verticalLayout_15.addWidget(self.scrollArea)


        self.verticalLayout_14.addWidget(self.FAQGroupBox)

        self.stackedWidget.addWidget(self.FAQPage)

        self.verticalLayout_5.addWidget(self.stackedWidget)


        self.verticalLayout_6.addWidget(self.content)

        self.bottomBar = QFrame(self.contentBottom)
        self.bottomBar.setObjectName(u"bottomBar")
        self.bottomBar.setMinimumSize(QSize(0, 22))
        self.bottomBar.setMaximumSize(QSize(16777215, 22))
        self.bottomBar.setStyleSheet(u"\n"
"/* Bottom Bar */\n"
"#bottomBar {background-color: #2c2c2c; }\n"
"#bottomBar QLabel { font-size: 11px; color: rgb(113, 126, 149); padding-left: 10px; padding-right: 10px; padding-bottom: 2px; }\n"
"\n"
"")
        self.bottomBar.setFrameShape(QFrame.NoFrame)
        self.bottomBar.setFrameShadow(QFrame.Raised)
        self.horizontalLayout_5 = QHBoxLayout(self.bottomBar)
        self.horizontalLayout_5.setSpacing(0)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.horizontalLayout_5.setContentsMargins(0, 0, 0, 0)

        font3 = QFont()
        font3.setFamilies([u"Segoe UI"])
        font3.setBold(False)
        font3.setItalic(False)

        self.verticalLayout_6.addWidget(self.bottomBar)
        self.verticalLayout_2.addWidget(self.contentBottom)
        self.appLayout.addWidget(self.contentBox)
        self.appMargins.addWidget(self.bgApp)
        MainWindow.setCentralWidget(self.styleSheet)
        self.retranslateUi(MainWindow)
        self.stackedWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(MainWindow)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:20pt; font-weight:600; color:#4673c6;\">B</span></p></body></html>", None))
        self.label_19.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:16pt; font-weight:600; color:#ffffff;\">BNET GEN</span></p></body></html>", None))
        self.toggleButton.setToolTip("")
        self.toggleButton.setText(QCoreApplication.translate("MainWindow", u"Hide", None))
        self.btnAccountGenerator.setText(QCoreApplication.translate("MainWindow", u"Account Generator", None))
        self.btnAccountBlock.setText(QCoreApplication.translate("MainWindow", u"Account Ban Checker", None))
        self.btnFaq.setText(QCoreApplication.translate("MainWindow", u"FAQ", None))
        self.titleRightInfo.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p><span style=\" font-size:12pt; font-weight:600; color:#4673c6;\">Battle net</span><span style=\" color:#ffffff;\"> - </span><span style=\" font-weight:600; color:#ffffff;\">Account Generator</span></p></body></html>", None))
        self.minimizeAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Minimize", None))
        self.minimizeAppBtn.setText("")
        self.maximizeRestoreAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Maximize", None))
        self.maximizeRestoreAppBtn.setText("")
        self.closeAppBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Close", None))
        self.closeAppBtn.setText("")
        self.AccountSettingGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Acccount Settings", None))
        self.chkBoxUseProxies.setText(QCoreApplication.translate("MainWindow", u"Use Proxies", None))
        self.chkBoxUseEmailstxt.setText(QCoreApplication.translate("MainWindow", u"Use Emails.txt", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Accounts to Create:", None))
        self.txtAccountToCreate.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Number", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Threads to Run:", None))
        self.txtThreadsToRun.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Number", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Account Username:", None))
        self.txtAccountUsername.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter username", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Kopeechka API Key:", None))
        self.txtKopeechkaApiKey.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Kopeechka API Key", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"BNET Custom Country", None))
        self.txtKopeechkEmailPref.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter preference", None))
        self.SMSSettingGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"SMS / Captcha", None))
        self.chkBoxUseSMSApi.setText(QCoreApplication.translate("MainWindow", u"Use SMS API", None))
        self.chkUseSMSPVA.setText(QCoreApplication.translate("MainWindow", u"Use SMSPVA", None))
        self.chkBoxSMSHUB.setText(QCoreApplication.translate("MainWindow", u"Use SMSHUB", None))
        self.chkBox5Sim.setText(QCoreApplication.translate("MainWindow", u"Use 5SIM", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"API Key:", None))
        self.txtApiKey.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter API Key", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"SMS Country:", None))
        self.txtSMSCountry.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter SMS API Key", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Wait Code Sec:", None))
        self.txtWaitCodeSec.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Wait Code Sec", None))
        self.InfoBox1GroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Balances", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"Kopeechka balance: ", None))
        self.lblKopeechkaBalance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Captcha Balance: ", None))
        self.lblCapsolverBalance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"SMSPVA Balance: ", None))
        self.lblSMSPVABalance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"SMSHUB Balance: ", None))
        self.lblSMSHUBBalance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_18.setText(QCoreApplication.translate("MainWindow", u"5Sim Balance: ", None))
        self.lbl5SimBalance.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.InfoBox2GroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Stats", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Failed Accounds: ", None))
        self.lblFailedAccounts.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Made Accounts: ", None))
        self.lblMadeAccounts.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Total Attempted: ", None))
        self.lblTotalAttempted.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.btnStart.setText(QCoreApplication.translate("MainWindow", u"Start", None))
        self.btnStop.setText(QCoreApplication.translate("MainWindow", u"Stop", None))
        self.AccountGeneratorConsole.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n""<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n""p, li { white-space: pre-wrap; }\n""</style></head><body style=\" font-family:'Consolas,monospace'; font-size:14px; font-weight:400; font-style:normal;\">\n""<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.AccountGeneratorConsole.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Console Output", None))
        self.SecondConsole.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Made Accounts Ouput", None))

        self.frame_9.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.label_92.setText(QCoreApplication.translate("MainWindow", u"<html><head/><body><p align=\"center\"><span style=\" font-size:18pt; font-weight:600; color:#ffffff;\">Coming Soon....</span></p></body></html>", None))
        self.frame_5.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.AccountBanCheckerGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"Ban Check", None))
        self.txtThreads.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.txtThreads.setText("")
        self.txtThreads.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter Number", None))
        self.label_11.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Threads:", None))
        self.frame_8.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.btnRun.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.btnRun.setText(QCoreApplication.translate("MainWindow", u"Run", None))
        self.frame_6.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.txtEditConsole2.setToolTip(QCoreApplication.translate("MainWindow", u"Coming Soon....", None))
        self.txtEditConsole2.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Console Output", None))
        self.FAQGroupBox.setTitle(QCoreApplication.translate("MainWindow", u"FAQs", None))

class ConsoleUpdater(QObject):
    update_signal = Signal(str, str)
    second_update_signal = Signal(str, str)


    def __init__(self):
        super().__init__()
        self.thread_statuses = {}

    def update_status(self, thread_index, message):
        self.thread_statuses[thread_index] = message
        self.emit_status(thread_index, message)

    def emit_status(self, thread_index, message):
        self.update_signal.emit(thread_index, message)

    def update_second_console(self, username, password):
        self.second_update_signal.emit(username, password)





class MainWindow(QMainWindow, Ui_MainWindow):
    CONFIG_FILE = 'settings.ini'
    updateFailedAccounts = Signal(int)
    updateMadeAccounts = Signal(int)
    updateTotalAttempted = Signal(int)
    def __init__(self,api):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_window)
        self.api = api
        self.security_monitor = SecurityMonitor()
        self.key_checker = ContinuousKeyChecker(self.api)
        self.load_settings()
        self.go_to_page(0)
        self.balance_fetcher = BalanceFetcher(self)
        self.balance_fetcher.fetch_all_balances()
        self.console_updater = ConsoleUpdater()
        self.console_updater.update_signal.connect(self.update_console, type=QtCore.Qt.QueuedConnection)
        self.console_updater.second_update_signal.connect(self.update_second_console, type=QtCore.Qt.QueuedConnection)
        self.useBestCapsovler.toggled.connect(self.updateCaptchaSelection)
        self.useTwoCaptcha.toggled.connect(self.updateCaptchaSelection)
        self.thread_messages = {}
        self.chkUseSMSPVA.clicked.connect(self.on_checkbox_clicked)
        self.chkBoxSMSHUB.clicked.connect(self.on_checkbox_clicked)
        self.chkBox5Sim.clicked.connect(self.on_checkbox_clicked)
        self.minimizeAppBtn.clicked.connect(self.showMinimized)
        self.toggleButton.clicked.connect(lambda: self.toggleMenu(True))
        self.closeAppBtn.clicked.connect(self.close)
        self.btnAccountGenerator.clicked.connect(lambda:self.go_to_page(0))
        self.btnAccountBlock.clicked.connect(lambda:self.go_to_page(1))
        self.btnFaq.clicked.connect(lambda:self.go_to_page(2))
        self.btnStart.clicked.connect(self.handleStartButtonClick)
        self.btnStop.clicked.connect(self.stop_everything)
        self.failed_accounts = 0
        self.made_accounts = 0
        self.total_attempts = 0

        self.faqs = [
            ("Q1: What captcha service is supported", "Answer: Best Captcha Solver"),
            ("Q2: What is required to run it?", "You need residential proxies, captcha balance, sms balance, and kopeechka balance or use own emails (outlook or gmx)."),
            ("Q3: Where can I find my API keys?", "Answer: There is a designated spot for each one labeled"),
            ("Q4: Where do the accounts save to?", "Answer: The accounts after successfully made save to Accounts.txt"),
            ("Q5: What is wait code sec?", "Answer: That is how many seconds to wait for sms for example 30,45,60."),
            ("Q6: What do I put for country code?", "Answer: When filling SMS Country info needs to be as follows, country ID for smshub like 22 for Vietnam, 5SIM lowercase russia for Russia, SMSPVA like FR for France."),
            ("Q7: What proxy format is supported?", "hostname:port:username:password, username:password@hostname:port, and ip:port"),
            ("Q8: What if I don't have my own emails?", "Answer: If you don't have your own emails the default will be Kopeechka and that will work but those only last so long to get emails. It is best to use own emails."),
        ]

    def updateCaptchaSelection(self):
        sender = self.sender()
        print(f"Sender: {sender.objectName()}, Checked: {sender.isChecked()}")

        if sender == self.useBestCapsovler and self.useBestCapsovler.isChecked():
            self.useTwoCaptcha.setChecked(False)
            print("Best Capsolver selected, 2Captcha deselected")
        elif sender == self.useTwoCaptcha and self.useTwoCaptcha.isChecked():
            self.useBestCapsovler.setChecked(False)
            print("2Captcha selected, Best Capsolver deselected")

    def setFailedAccounts(self):
        self.failed_accounts += 1
        self.lblFailedAccounts.setText(str(self.failed_accounts))

    def _async_raise(self,tid, exctype):
        """Raises an exception in threads with ID tid"""
        if not isinstance(exctype, type):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("Invalid thread ID")
        elif res != 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_everything(self):
        """Attempts to stop all threads except for the current thread."""
        current_thread = threading.current_thread().ident
        for thread in threading.enumerate():
            if thread.ident != current_thread:
                self._async_raise(thread.ident, SystemExit)
        self.clear_console()
        self.update_console("Pause",
                            "All threads stopped!")

    def update_second_console(self, username, password):
        current_text = self.SecondConsole.toPlainText()
        new_message = f"Account made: {username} | {password}"
        new_text = f"{current_text}\n{new_message}" if current_text else new_message
        self.SecondConsole.setPlainText(new_text)
        QCoreApplication.processEvents()


    def get_thread_id(self,thread):
        """Retrieves a given thread's ID"""
        if hasattr(thread, 'ident'):
            return thread.ident
        raise ValueError("Could not retrieve the thread's ID")
    def setMadeAccounts(self):
        self.made_accounts += 1
        self.lblMadeAccounts.setText(str(self.made_accounts))

    def setTotalAttempted(self):
        self.total_attempts += 1
        self.lblTotalAttempted.setText(str(self.total_attempts))

    def update_console(self, thread_index, message):
        self.thread_messages[thread_index] = message
        display_text = "\n".join(f"Thread {idx}: {msg}" for idx, msg in sorted(self.thread_messages.items()))
        self.AccountGeneratorConsole.setPlainText(display_text)
        QCoreApplication.processEvents()

    def on_checkbox_clicked(self):
        clicked_checkbox = self.sender()

        self.chkUseSMSPVA.setChecked(False)
        self.chkBoxSMSHUB.setChecked(False)
        self.chkBox5Sim.setChecked(False)

        clicked_checkbox.setChecked(True)


    def showFAQPage(self):
        scroll_area = self.scrollArea
        scroll_area.setWidgetResizable(True)
        faq_page = FAQPage(self.faqs)
        scroll_area.setWidget(faq_page)
    def go_to_page(self,index):
        if(index == 2):
            self.showFAQPage()
        self.stackedWidget.setCurrentIndex(index)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self.dragPos)
            event.accept()

    def maximize_window(self):

        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def toggleMenu(self, enable):
        if enable:
            width = self.leftMenuBg.width()
            maxExtend = 240
            standard = 60
            if width == 60:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            self.animation = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
            self.animation.setDuration(500)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    def clear_console(self):
        """Clear the console area of the UI."""
        self.thread_messages = {}
        self.AccountGeneratorConsole.clear()
        QCoreApplication.processEvents()

    def check_email_file(self):
        try:
            with open("emails.txt", "r") as file:
                lines = file.readlines()

            if not lines:
                return "Emails.txt is empty."

            valid_patterns = [
                re.compile(r"^[^@]+@[^@]+\.[^:]+:[^\s]+$"),  # email:password
                re.compile(r"^[^@]+@[^@]+\.[^|]+\|[^\s]+$"),  # email|password
                re.compile(r"^[^@]+@[^@]+\.[^|]+\|[^\|]+\|.+$"),  # email|password|extra_fields
            ]

            for index, line in enumerate(lines, start=1):
                line = line.strip()  # Remove whitespace and newline characters
                if not any(pattern.match(line) for pattern in valid_patterns):
                    return f"Line {index} is incorrect format: {line}"

            return None

        except FileNotFoundError:
            return f"Error: The file 'emails.txt' does not exist."
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

    def handleStartButtonClick(self):
        self.save_settings()
        if not self.useTwoCaptcha.isChecked() and not self.useBestCapsovler.isChecked():
            self.update_console("Error",
                            "Please select a captcha to use before starting.")
            return
        if (self.useBestCapsovler.isChecked() or self.useTwoCaptcha.isChecked()):
            if not self.txtCaptchaApiKey.text().strip():
                self.update_console("Error",
                                    "Please enter captcha API key")
                return
        if self.chkBoxUseSMSApi.isChecked():
            if self.chkUseSMSPVA.isChecked() or self.chkBoxSMSHUB.isChecked() or self.chkBox5Sim.isChecked():
                if not self.txtSMSCountry.text().strip() or not self.txtWaitCodeSec.text().strip() or not self.txtApiKey.text().strip():
                    self.update_console("Error",
                                        "Please enter all required SMS settings: SMS Country, Wait Code Sec, and API Key")
                    return

        if self.chkBoxUseSMSApi.isChecked():

            if not self.chkUseSMSPVA.isChecked() and not self.chkBoxSMSHUB.isChecked() and not self.chkBox5Sim.isChecked():
                self.update_console("Error",
                                    "If using sms api you must select either 5sim, smspva, or smshub")
                return

        if not self.txtAccountToCreate.text() or not self.txtThreadsToRun.text() or not self.txtKopeechkEmailPref.text():
            self.update_console("Error",
                                "Please fill in all required fields: Accounts to Create, Threads to Run, Captcha API Key, and BNET custom country")
            return
        if self.chkBoxUseEmailstxt.isChecked():
            result = self.check_email_file()
            if result:
                self.update_console("Error", result)
                return

        try:
            accounts_to_create = int(self.txtAccountToCreate.text())
            threads_to_run = int(self.txtThreadsToRun.text())
            wait_code_sec = int(self.txtWaitCodeSec.text())
        except ValueError:
            self.update_console("Error",
                                "Please ensure 'Accounts to Create', 'Threads to Run', and 'Wait Code Sec' are integers.")
            return
        if not self.chkBoxUseEmailstxt.isChecked() and not self.txtKopeechkaApiKey.text():
            self.update_console("Error", "If not using emails.txt, a Kopeechka API Key is required.")
            return
        self.clear_console()
        self.balance_fetcher.fetch_all_balances()
        one_time_key_checker = OneTimeKeyChecker(self.api)
        data = self.fetch_ui_data()
        config = Config(data)
        signup_manager = SignUpThreads(config, self.console_updater,self)
        signup_manager.start_processes()

    def fetch_ui_data(self):
        return {
            'use_proxies': self.chkBoxUseProxies.isChecked(),
            'use_emails': self.chkBoxUseEmailstxt.isChecked(),
            'accounts_to_create': int(self.txtAccountToCreate.text()),
            'threads_to_run': int(self.txtThreadsToRun.text()),
            'account_username': self.txtAccountUsername.text(),
            'kopeechka_api_key': self.txtKopeechkaApiKey.text(),
            'kopeechka_email_pref': self.txtKopeechkEmailPref.text(),
            'use_sms_api': self.chkBoxUseSMSApi.isChecked(),
            'use_smspva': self.chkUseSMSPVA.isChecked(),
            'use_smshub': self.chkBoxSMSHUB.isChecked(),
            'use_5sim': self.chkBox5Sim.isChecked(),
            'api_key': self.txtApiKey.text(),
            'sms_country': self.txtSMSCountry.text(),
            'wait_code_sec': int(self.txtWaitCodeSec.text()),
            'use_best_capsolver': self.useBestCapsovler.isChecked(),
            'use_two_captcha': self.useTwoCaptcha.isChecked(),
            'captcha_api_key': self.txtCaptchaApiKey.text()
        }

    def get_settings(self):
        """Collect settings from the GUI elements"""
        settings = configparser.ConfigParser()
        settings['AccountSettings'] = {
            'use_proxies': str(self.chkBoxUseProxies.isChecked()),
            'use_emails': str(self.chkBoxUseEmailstxt.isChecked()),
            'accounts_to_create': self.txtAccountToCreate.text(),
            'threads_to_run': self.txtThreadsToRun.text(),
            'account_username': self.txtAccountUsername.text(),
            'kopeechka_api_key': self.txtKopeechkaApiKey.text(),
            'kopeechka_email_pref': self.txtKopeechkEmailPref.text(),
            'use_sms_api': str(self.chkBoxUseSMSApi.isChecked()),
            'use_smspva': str(self.chkUseSMSPVA.isChecked()),
            'use_smshub': str(self.chkBoxSMSHUB.isChecked()),
            'use_5sim': str(self.chkBox5Sim.isChecked()),
            'sms_api_key': self.txtApiKey.text(),
            'sms_country': self.txtSMSCountry.text(),
            'wait_code_sec': self.txtWaitCodeSec.text(),
            'use_best_capsolver': str(self.useBestCapsovler.isChecked()),
            'use_two_captcha': str(self.useTwoCaptcha.isChecked()),
            'captcha_api_key': self.txtCaptchaApiKey.text()
        }
        return settings

    def save_settings(self):
        """Save the encrypted settings as a single line in an INI file"""
        settings = self.get_settings()

        settings_str = '\n'.join(
            f'{section}.{key}={value}' for section, options in settings.items() for key, value in options.items())

        encrypted_settings = encrypt(settings_str)

        with open(self.CONFIG_FILE, 'w') as config_file:
            config_file.write(encrypted_settings)

    def load_settings(self):
        """Load and decrypt settings from a single line in an INI file"""
        if os.path.exists(self.CONFIG_FILE):
            with open(self.CONFIG_FILE, 'r') as config_file:
                encrypted_settings = config_file.read()

            decrypted_settings = decrypt(encrypted_settings)

            settings_dict = dict(line.split('=') for line in decrypted_settings.split('\n') if '=' in line)

            self.set_settings(settings_dict)
        else:
            print("No configuration file found. Using default settings.")

    def set_settings(self, settings_dict):
        """Populate GUI elements from the decrypted settings"""
        for key, value in settings_dict.items():
            section, option = key.split('.')
            if section == 'AccountSettings':
                if option == 'use_proxies':
                    self.chkBoxUseProxies.setChecked(value == 'True')
                elif option == 'use_emails':
                    self.chkBoxUseEmailstxt.setChecked(value == 'True')
                elif option == 'accounts_to_create':
                    self.txtAccountToCreate.setText(value)
                elif option == 'threads_to_run':
                    self.txtThreadsToRun.setText(value)
                elif option == 'account_username':
                    self.txtAccountUsername.setText(value)
                elif option == 'kopeechka_api_key':
                    self.txtKopeechkaApiKey.setText(value)
                elif option == 'kopeechka_email_pref':
                    self.txtKopeechkEmailPref.setText(value)
                elif option == 'use_sms_api':
                    self.chkBoxUseSMSApi.setChecked(value == 'True')
                elif option == 'use_smspva':
                    self.chkUseSMSPVA.setChecked(value == 'True')
                elif option == 'use_smshub':
                    self.chkBoxSMSHUB.setChecked(value == 'True')
                elif option == 'use_5sim':
                    self.chkBox5Sim.setChecked(value == 'True')
                elif option == 'sms_api_key':
                    self.txtApiKey.setText(value)
                elif option == 'sms_country':
                    self.txtSMSCountry.setText(value)
                elif option == 'wait_code_sec':
                    self.txtWaitCodeSec.setText(value)
                elif option == 'use_best_capsolver':
                    self.useBestCapsovler.setChecked(value == 'True')
                elif option == 'use_two_captcha':
                    self.useTwoCaptcha.setChecked(value == 'True')
                elif option == 'captcha_api_key':
                    self.txtCaptchaApiKey.setText(value)


