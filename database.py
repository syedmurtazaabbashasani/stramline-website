import sqlite3
import hashlib
import hmac
import os
from datetime import datetime

DB_NAME = "roomcare.db"

def connect():
    """Open a database connection."""
    connection = sqlite3.connect(DB_NAME)
    connection.row_factory = sqlite3.Row
    return connection

def hash_password(password):
    """Hash a password with a random salt using Python's standard library."""
    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
    return salt.hex() + "$" + hashed.hex()

def verify_password(password, saved_hash):
    """Compare a password with the saved password hash."""
    try:
        salt_hex, hash_hex = saved_hash.split("$")
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 200_000)
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def init_db():
    """Create tables and a demo worker account if they do not exist."""
    with connect() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'worker'))
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                block TEXT NOT NULL,
                room TEXT NOT NULL,
                issue TEXT NOT NULL,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'Pending',
                created_at TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES users(id)
            )
        """)
        worker = db.execute(
            "SELECT id FROM users WHERE email = ?", ("worker@campus.local",)
        ).fetchone()
        if worker is None:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                ("Demo Cleaning Worker", "worker@campus.local",
                 hash_password("Clean123!"), "worker")
            )

def create_user(name, email, password, role="student"):
    """Add a new user. Public registration only creates student accounts."""
    try:
        with connect() as db:
            db.execute(
                "INSERT INTO users (name, email, password_hash, role) VALUES (?, ?, ?, ?)",
                (name, email, hash_password(password), role)
            )
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "That email is already registered."

def check_login(email, password):
    """Return user details if the login is correct; otherwise return None."""
    with connect() as db:
        row = db.execute(
            "SELECT id, name, email, password_hash, role FROM users WHERE email = ?",
            (email,)
        ).fetchone()
    if row and verify_password(password, row["password_hash"]):
        return {"id": row["id"], "name": row["name"],
                "email": row["email"], "role": row["role"]}
    return None

def create_request(student_id, block, room, issue, details):
    """Save a student's cleaning request."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    with connect() as db:
        db.execute(
            """INSERT INTO requests
               (student_id, block, room, issue, details, status, created_at)
               VALUES (?, ?, ?, ?, ?, 'Pending', ?)""",
            (student_id, block, room, issue, details, now)
        )

def get_student_requests(student_id):
    """Get only the requests belonging to the logged-in student."""
    with connect() as db:
        rows = db.execute(
            """SELECT * FROM requests WHERE student_id = ?
               ORDER BY id DESC""", (student_id,)
        ).fetchall()
    return [dict(row) for row in rows]

def get_all_requests(status="All"):
    """Get requests for the worker dashboard."""
    query = """
        SELECT requests.*, users.name AS student_name, users.email AS student_email
        FROM requests JOIN users ON requests.student_id = users.id
    """
    values = ()
    if status != "All":
        query += " WHERE requests.status = ?"
        values = (status,)
    query += " ORDER BY requests.id DESC"
    with connect() as db:
        rows = db.execute(query, values).fetchall()
    return [dict(row) for row in rows]

def update_request_status(request_id, status):
    """Save a new status for a request."""
    with connect() as db:
        db.execute(
            "UPDATE requests SET status = ? WHERE id = ?",
            (status, request_id)
        )

def get_counts():
    """Return total, pending, in-progress and completed counts."""
    with connect() as db:
        total = db.execute("SELECT COUNT(*) FROM requests").fetchone()[0]
        pending = db.execute(
            "SELECT COUNT(*) FROM requests WHERE status = 'Pending'"
        ).fetchone()[0]
        progress = db.execute(
            "SELECT COUNT(*) FROM requests WHERE status = 'In Progress'"
        ).fetchone()[0]
        completed = db.execute(
            "SELECT COUNT(*) FROM requests WHERE status = 'Completed'"
        ).fetchone()[0]
    return total, pending, progress, completed
