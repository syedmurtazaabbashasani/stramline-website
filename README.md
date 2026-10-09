# RoomCare — Campus Cleaning Request System

A beginner-friendly Python project that replaces scattered hostel WhatsApp cleaning groups with one central request dashboard.

## Features
- Student registration and login
- Worker login
- Passwords stored as salted PBKDF2 hashes, not plain text
- Student submits a request with block, room, cleaning type, and notes
- Student sees their own request history and status
- Worker views and filters requests, then updates status
- SQLite database saves information between sessions

## Run the project

1. Install Python 3.10 or newer.
2. Open Terminal in this project folder.
3. (Recommended) Create and activate a virtual environment:
   - macOS/Linux: `python3 -m venv .venv` then `source .venv/bin/activate`
   - Windows: `py -m venv .venv` then `.venv\Scripts\activate`
4. Install packages: `pip install -r requirements.txt`
5. Start the app: `streamlit run app.py`
6. Open the local URL shown in Terminal (usually http://localhost:8501).

## Demo worker login
- Email: `worker@campus.local`
- Password: `Clean123!`

Student accounts can be created from the registration tab.

## Files
- `app.py`: user interface and page flow
- `database.py`: SQLite database, account authentication, and request functions
- `requirements.txt`: required Python package
- `roomcare.db`: created automatically when the app runs

## Important limitations
This is a local demonstration prototype, not an approved campus production system. The demo worker password is public by design and must not be used for real service. For production, add administrator-controlled worker accounts, stronger authorization, HTTPS, backups, audit logs, input validation, and institution-approved hosting. The current version stores requests locally on the machine running Streamlit.
