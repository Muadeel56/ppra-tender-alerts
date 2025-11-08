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
python test/test_api.py
```

Or if you need to use `python3`:

```bash
python3 test/test_api.py
```

This script will:
- Test connectivity to the PPRA API endpoint
- Display the response status and details
- Handle errors gracefully (including 405 Method Not Allowed responses)

Optional: Environment Variables

If you need to customize the API endpoint URL, create a `.env` file in the root directory:

```bash
PPRA_API_URL=https://ppra.gov.pk/api/tenders
```

If no `.env` file is provided, the script will use the default URL.

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

# Twilio (optional)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_number

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

Project Structure
ppra-tender-alerts/
├─ backend/
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
├─ test/
│  └─ test_api.py
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
