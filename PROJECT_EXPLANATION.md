# RoomCare — explanation for project review

## Problem statement
Room-cleaning requests are currently sent through separate WhatsApp groups for each hostel block. Messages can be disorganized, group membership may be limited, and students may find it hard to track a request's progress.

## Proposed solution
RoomCare is a centralized web application. Students log in and submit structured cleaning requests. Workers log in separately, view requests in one dashboard, and update their status. Students can then check progress without searching through group messages.

## Modules
1. **Authentication module** — registration, login, password hashing, and role-based screens.
2. **Student request module** — captures block, room number, cleaning type, and optional details.
3. **Worker module** — displays all requests and lets workers change status.
4. **Database module** — saves user and request records using SQLite.
5. **Tracking/dashboard module** — displays request history, filters, and summary counts.

## How the files connect
- `app.py` imports functions from `database.py`.
- Streamlit draws the interface and handles button clicks/forms.
- `database.py` runs SQL commands through Python's built-in `sqlite3` module.
- SQLite stores records in `roomcare.db`.
- When a student submits a form, `app.py` calls `create_request()`.
- When a worker updates a request, `app.py` calls `update_request_status()`.

## Concepts used
- Functions: reusable tasks such as `check_login()` and `create_request()`.
- Lists: dropdown options such as hostel blocks and request statuses.
- Dictionaries: the logged-in user and individual request records.
- Conditions: different screens for students and workers.
- SQL: insert, select, update, and table creation.
- Authentication: verifies a password before opening the dashboard.
- Hashing: stores a derived password hash instead of the original password.
- Session state: remembers the logged-in user while navigating the Streamlit app.

## Database tables
### users
- `id`: unique user identifier
- `name`: user's display name
- `email`: unique login email
- `password_hash`: salted password hash
- `role`: `student` or `worker`

### requests
- `id`: unique request identifier
- `student_id`: identifies the student who submitted it
- `block`, `room`: request location
- `issue`, `details`: cleaning request information
- `status`: Pending, Accepted, In Progress, or Completed
- `created_at`: date/time the request was submitted

## Suggested demonstration
1. Register a student account and log in.
2. Submit a cleaning request for a sample block and room.
3. Log out.
4. Log in using the demo worker account.
5. Find the request and change it to Accepted, then In Progress, then Completed.
6. Log back in as the student and show the updated status.

## Future improvements
- Admin panel to create and approve worker accounts.
- Notifications when status changes.
- Request priority and preferred cleaning time.
- Assignment to a particular cleaning worker.
- Monthly reports and response-time analytics.
- Cloud database and deployment after institution approval.

## Honest scope note
The prototype provides working local authentication, a persistent SQLite database, and separate student/worker workflows. It does not yet provide institution-wide access, automated notifications, verified VIT identity, or real worker assignment. Those are future enhancements.
