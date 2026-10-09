import streamlit as st
from database import (
    init_db, create_user, check_login, create_request,
    get_student_requests, get_all_requests, update_request_status,
    get_counts
)

st.set_page_config(page_title="CleanIT | Campus Cleaning", page_icon="🧹", layout="wide")
init_db()

st.title("🧹 CleanIT")
st.caption("A centralized room-cleaning request system for campus hostels")

if "user" not in st.session_state:
    st.session_state.user = None

def logout():
    st.session_state.user = None
    st.rerun()

def login_screen():
    st.subheader("Welcome")
    login_tab, register_tab = st.tabs(["Log in", "Student registration"])

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email").strip().lower()
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", use_container_width=True)
        if submitted:
            user = check_login(email, password)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Login failed. Check your email and password.")

        with st.expander("Demo worker account"):
            st.write("Email: `worker@campus.local`")
            st.write("Password: `Clean123!`")
            st.caption("For this local prototype only. Change this before any real deployment.")

    with register_tab:
        st.write("Create a student account to submit and track cleaning requests.")
        with st.form("register_form"):
            name = st.text_input("Full name")
            email = st.text_input("Student email",type="password").strip().lower()
            password = st.text_input("Create password", type="password")
            confirm = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)
        if submitted:
            if not name.strip() or not email or not password:
                st.error("Please fill in every field.")
            elif password != confirm:
                st.error("The passwords do not match.")
            elif len(password) < 8:
                st.error("Use a password with at least 8 characters.")
            else:
                ok, message = create_user(name.strip(), email, password, "student")
                if ok:
                    st.success(message + " You can now log in.")
                else:
                    st.error(message)

def student_dashboard(user):
    st.subheader(f"Hello, {user['name']} 👋")
    st.write("Submit a request below, then use **My requests** to follow its progress.")
    new_tab, history_tab = st.tabs(["New cleaning request", "My requests"])

    with new_tab:
        with st.form("request_form"):
            block = st.selectbox("Hostel block", ["Block Q", "Block P", "Block N", "Block T", "Other"])
            room = st.text_input("Room number")
            issue = st.selectbox("Cleaning needed", [
                "Room cleaning", "Bathroom cleaning", "Floor cleaning",
                "Dustbin removal", "Other"
            ])
            details = st.text_area("Additional details (optional)", max_chars=500)
            submitted = st.form_submit_button("Submit request", use_container_width=True)
        if submitted:
            if not room.strip():
                st.error("Please enter your room number.")
            else:
                create_request(user["id"], block, room.strip(), issue, details.strip())
                st.success("Request submitted successfully.")
                st.rerun()

    with history_tab:
        requests = get_student_requests(user["id"])
        if not requests:
            st.info("You have not submitted any requests yet.")
        else:
            for req in requests:
                with st.container(border=True):
                    left, right = st.columns([3, 1])
                    left.markdown(f"**{req['issue']} — {req['block']}, Room {req['room']}**")
                    left.caption(f"Submitted: {req['created_at']}")
                    if req["details"]:
                        left.write(req["details"])
                    right.metric("Status", req["status"])

def worker_dashboard(user):
    st.subheader("Worker dashboard")
    st.write("Review incoming requests and update their progress.")
    total, pending, progress, completed = get_counts()
    a, b, c, d = st.columns(4)
    a.metric("Total", total)
    b.metric("Pending", pending)
    c.metric("In progress", progress)
    d.metric("Completed", completed)

    status_filter = st.selectbox(
        "Filter requests",
        ["All", "Pending", "Accepted", "In Progress", "Completed"]
    )
    requests = get_all_requests(status_filter)
    if not requests:
        st.info("No requests match this filter.")
        return

    for req in requests:
        with st.container(border=True):
            st.markdown(f"**Request #{req['id']} · {req['issue']}**")
            st.write(f"**Location:** {req['block']}, Room {req['room']}")
            st.write(f"**Student:** {req['student_name']} ({req['student_email']})")
            st.write(f"**Submitted:** {req['created_at']}")
            if req["details"]:
                st.write(f"**Details:** {req['details']}")
            current = req["status"]
            options = ["Pending", "Accepted", "In Progress", "Completed"]
            selected = st.selectbox(
                "Update status",
                options,
                index=options.index(current),
                key=f"status_{req['id']}"
            )
            if st.button("Save status", key=f"save_{req['id']}"):
                update_request_status(req["id"], selected)
                st.success(f"Request #{req['id']} updated.")
                st.rerun()

user = st.session_state.user
if user is None:
    login_screen()
else:
    with st.sidebar:
        st.write(f"**{user['name']}**")
        st.write(f"Role: {user['role'].title()}")
        st.divider()
        if st.button("Log out", use_container_width=True):
            logout()
    if user["role"] == "student":
        student_dashboard(user)
    else:
        worker_dashboard(user)

st.divider()
st.caption("RoomCare prototype · Data is stored in a local SQLite database.")
