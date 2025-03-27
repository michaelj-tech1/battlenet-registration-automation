# Battle.net Account Registration Automation

[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-blue.svg)](https://github.com/michaelj-tech1/battlenet-registration-automation)

## Overview
**Battle.net Account Registration Automation** is a fully automated, multithreaded Python tool designed to register Battle.net accounts by interacting directly with the platform’s APIs. By reverse-engineering the sign-up process using Fiddler, this tool bypasses traditional browser-based workflows for a faster, more efficient account creation process.

## Features
- **Reverse-Engineered Sign-Up Process:**  
  Inspected request headers, cookies, and API behavior with Fiddler to accurately replicate the Battle.net registration flow.
- **Automated Account Registration:**  
  Utilizes a multithreaded Python backend to create accounts rapidly by interacting directly with the Battle.net APIs.
- **Graphical User Interface (GUI):**  
  Built with PySide6, the GUI allows for managing input data, monitoring registration progress in real-time, and handling concurrent account creation.
- **SMS Support:**  
  Integrated SMS verification to ensure secure and validated account creation.
- **Proxy Support:**  
  Built-in support for proxies to help manage IP restrictions and enhance anonymity.

## Prerequisites
- **Python 3.7** or later  
- **Internet Connection** for API, SMS, proxy, and email verification  
- **Email Support** (e.g., an email account with IMAP enabled for verification retrieval)  
- **SMS Support** (active SMS API credentials for phone verification)

## Installation

1. **Clone the Repository:**  
   ```bash
   git clone https://github.com/michaelj-tech1/battlenet-registration-automation.git
   cd battlenet-registration-automation
