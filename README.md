PPRA Tender Alerts

PPRA Tender Alerts is a web application that allows users to track and get notifications for tenders published by the Public Procurement Regulatory Authority (PPRA). This project leverages a modern tech stack including React, Django REST API, and PostgreSQL, providing a real-time, easy-to-use interface to manage and monitor tender data.

Quick Start

This section will help you get started quickly by setting up the development environment and running the test API script.

Prerequisites

- Python 3.12 or higher
- Git

Step 1: Clone the Repository

Clone the repository to your local machine:

```bash
git clone https://github.com/your-username/ppra-tender-alerts.git
cd ppra-tender-alerts
```

Step 2: Set Up Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

- On Linux/Mac:
  ```bash
  source venv/bin/activate
  ```

- On Windows:
  ```bash
  venv\Scripts\activate
  ```

You should see `(venv)` at the beginning of your command prompt when the virtual environment is active.

Step 3: Install Dependencies

Install the required Python packages from the requirements file:

```bash
pip install -r backend/requirements.txt
```

This will install the following dependencies:
- `requests` - HTTP library for API requests
- `selenium` - Web scraping and browser automation
- `python-dotenv` - Environment variable management
- `pytest` - Testing framework

Step 4: Run the Test API Script

Test the connectivity to the PPRA API by running the test script:

```bash
python tests/test_api.py
```

Or if you need to use `python3`:

```bash
python3 tests/test_api.py
```

This script will:
- Test connectivity to the PPRA API endpoint
- Display the response status and details
- Handle errors gracefully (including 405 Method Not Allowed responses)

Optional: Environment Variables

If you need to customize the API endpoint URL or configure WhatsApp notifications, create a `.env` file in the root directory:

```bash
PPRA_API_URL=https://ppra.gov.pk/api/tenders
```

If no `.env` file is provided, the script will use the default URL.

For WhatsApp notifications setup, see the [Twilio WhatsApp Configuration](#twilio-whatsapp-configuration) section below.

Table of Contents

Quick Start

Features

Tech Stack

Installation

Configuration

Usage

Project Structure

API Documentation

Contributing

License

Acknowledgements

Features

Fetch real-time tender data from the PPRA API

Filter tenders by category, region, or deadline

Search functionality for tenders by keywords

User authentication and account management

Personalized notifications for new tenders via email/SMS

Admin dashboard to manage users and tender alerts

Responsive UI for desktop and mobile

Tech Stack

Frontend:

React 19

Vite

Tailwind CSS v4

React Router (BrowserRouter)

Backend:

Django 4.x

Django REST Framework

PostgreSQL (with optional PostGIS for location-based filtering)

Celery + Redis (for background notifications)

Other Tools:

Docker & Docker Compose (for containerization)

Twilio API (for SMS alerts)

Git & GitHub (version control)

Installation
Prerequisites

Node.js v20+

Python 3.12+

PostgreSQL 15+

Docker & Docker Compose (optional but recommended)

Clone the repository
git clone https://github.com/your-username/ppra-tender-alerts.git
cd ppra-tender-alerts

Backend Setup
cd backend
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt

Database Setup
# Create PostgreSQL database and user
psql -U postgres
CREATE DATABASE ppra_tender_db;
CREATE USER ppra_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ppra_tender_db TO ppra_user;


Apply migrations:

python manage.py migrate

Frontend Setup
cd ../frontend
npm install
npm run dev

Running with Docker
docker-compose up --build

Configuration

Create a .env file in the backend folder and add the following environment variables:

# Django Settings
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=ppra_tender_db
DB_USER=ppra_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# PPRA API
PPRA_API_KEY=your_api_key

# Twilio WhatsApp Sandbox (optional)
# Get these from https://console.twilio.com/
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# Gmail SMTP Email (optional)
# Generate App Password from https://myaccount.google.com/apppasswords
GMAIL_SMTP_USER=yourname@gmail.com
GMAIL_SMTP_PASSWORD=your_16_character_app_password
GMAIL_SMTP_FROM=yourname@gmail.com  # Optional, defaults to GMAIL_SMTP_USER
GMAIL_SMTP_TO=recipient@gmail.com  # Optional, for testing

Usage
Backend

Start Django development server:

cd backend
python manage.py runserver


API endpoints will be available at http://localhost:8000/api/

Frontend

Start React development server:

cd frontend
npm run dev


Access the application at http://localhost:5173 (Vite default port).

Twilio WhatsApp Configuration

This project supports WhatsApp notifications via Twilio's WhatsApp sandbox. Follow these steps to set it up:

Step 1: Create a Twilio Account

1. Sign up for a free Twilio account at https://www.twilio.com/try-twilio
2. Verify your email and phone number
3. Navigate to the Twilio Console: https://console.twilio.com/

Step 2: Get Your Twilio Credentials

1. In the Twilio Console, find your Account SID and Auth Token on the dashboard
2. Copy these values - you'll need them for your `.env` file

Step 3: Set Up WhatsApp Sandbox

1. In the Twilio Console, navigate to "Messaging" > "Try it out" > "Send a WhatsApp message"
2. You'll see the sandbox number (default: `+14155238886`) and a join code
3. The join code is a word like "join <word>" that recipients need to send to the sandbox number

Step 4: Join the Sandbox (for testing)

1. Open WhatsApp on your phone
2. Send the join code (e.g., "join example-word") to the Twilio sandbox number: `+1 415 523 8886`
3. You should receive a confirmation message that you've joined the sandbox

Step 5: Configure Environment Variables

1. Copy `.env.example` to `.env` in the project root:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Twilio credentials:
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid_here
   TWILIO_AUTH_TOKEN=your_auth_token_here
   TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
   TWILIO_WHATSAPP_TO=whatsapp:+1234567890  # Replace with your WhatsApp number
   ```

   **Important:** 
   - Use the `whatsapp:` prefix for both FROM and TO numbers
   - Replace `+1234567890` with your actual WhatsApp number in E.164 format (country code + number)
   - The recipient number must have joined the sandbox before receiving messages

Step 6: Test WhatsApp Notifications

Run the test script to verify the integration:

```bash
python tests/test_whatsapp_notification.py
```

Or if you need to use `python3`:

```bash
python3 tests/test_whatsapp_notification.py
```

The script will:
- Check that all required environment variables are set
- Initialize the WhatsApp notifier
- Send a test message to your configured WhatsApp number
- Display success/error messages

If successful, you should receive a test message on WhatsApp. If you encounter errors, check:
- Your Twilio credentials are correct
- The recipient has joined the sandbox
- Phone numbers are in the correct format with `whatsapp:` prefix
- Your Twilio account has sufficient credits

Gmail SMTP Email Configuration

This project supports email notifications via Gmail SMTP with App Password authentication. Follow these steps to set it up:

Step 1: Enable 2-Step Verification

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to "Security" section
3. Under "Signing in to Google", enable "2-Step Verification" if not already enabled
4. Follow the prompts to complete the setup (you'll need a phone number)

Step 2: Generate Gmail App Password

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to "Security" section
3. Under "Signing in to Google", find "2-Step Verification" and click on it
4. Scroll down to find "App passwords" (you may need to search for it)
5. Click on "App passwords"
6. Select "Mail" as the app and "Other (Custom name)" as the device
7. Enter a name like "PPRA Tender Alerts" and click "Generate"
8. Google will display a 16-character password (e.g., `abcd efgh ijkl mnop`)
9. **Copy this password immediately** - you won't be able to see it again
10. Remove spaces from the password when adding it to your `.env` file

**Important:** 
- You cannot use your regular Gmail password for SMTP
- App Passwords are required when 2-Step Verification is enabled
- Each App Password is 16 characters (without spaces)

Step 3: Configure Environment Variables

1. Edit your `.env` file in the project root and add your Gmail SMTP credentials:
   ```bash
   GMAIL_SMTP_USER=yourname@gmail.com
   GMAIL_SMTP_PASSWORD=abcdefghijklmnop  # Your 16-character App Password (no spaces)
   GMAIL_SMTP_FROM=yourname@gmail.com  # Optional, defaults to GMAIL_SMTP_USER
   GMAIL_SMTP_TO=recipient@gmail.com  # Optional, for testing purposes
   ```

   **Important:**
   - Use your full Gmail address for `GMAIL_SMTP_USER`
   - Use the 16-character App Password (without spaces) for `GMAIL_SMTP_PASSWORD`
   - `GMAIL_SMTP_FROM` is optional and defaults to `GMAIL_SMTP_USER`
   - `GMAIL_SMTP_TO` is optional and only needed for testing

Step 4: Test Email Notifications

Run the test script to verify the integration:

```bash
python tests/test_email_notification.py
```

Or if you need to use `python3`:

```bash
python3 tests/test_email_notification.py
```

The script will:
- Check that all required environment variables are set
- Initialize the email notifier
- Send a test email to your configured email address
- Display success/error messages

If successful, you should receive a test email. If you encounter errors, check:
- Your Gmail App Password is correct (16 characters, no spaces)
- 2-Step Verification is enabled on your Google account
- The recipient email address is correct
- Check your spam/junk folder
- Your internet connection is working
- You're using an App Password, not your regular Gmail password

Project Structure
ppra-tender-alerts/
├─ scripts/           # Python scripts (fetch_tenders.py, etc.)
├─ data/              # JSON or DB storage
├─ tests/             # Test scripts
│  ├─ test_whatsapp_notification.py  # WhatsApp notification test
│  ├─ test_email_notification.py    # Email notification test
├─ backend/
│  ├─ scraper/
│  │  ├─ notifications.py    # WhatsApp and Email notifications
│  │  ├─ ppra_scraper.py
│  │  └─ tender_storage.py
│  ├─ ppra_tender_alerts/
│  ├─ tenders/
│  ├─ users/
│  ├─ manage.py
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ components/
│  │  ├─ pages/
│  │  ├─ hooks/
│  │  ├─ App.jsx
│  │  └─ main.jsx
│  ├─ index.html
│  └─ package.json
├─ .env               # Environment variables (create from .env.example)
├─ .env.example       # Environment variables template
├─ .gitignore
├─ docker-compose.yml
└─ README.md

API Documentation
Sample Endpoints

GET /api/tenders/ – Fetch all tenders

GET /api/tenders/?category=IT – Filter tenders by category

POST /api/users/register/ – Register a new user

POST /api/users/login/ – User login

POST /api/alerts/ – Create a new tender alert

Note: API responses are in JSON format.

Contributing

Fork the repository

Create a new branch: git checkout -b feature/YourFeature

Commit your changes: git commit -m 'Add new feature'

Push to the branch: git push origin feature/YourFeature

Open a Pull Request

License

This project is licensed under the MIT License. See the LICENSE
 file for details.

Acknowledgements

PPRA Official API

Django REST Framework

Tailwind CSS

Vite

Twilio
