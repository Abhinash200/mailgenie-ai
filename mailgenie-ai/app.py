import os
import json
import smtplib
import streamlit as st
from email_generator import generate_email
from grammar_checker import correct_grammar
from email_sender import send_email
from scheduler import schedule_meeting
from memory_manager import MemoryManager
from utils.attachments import handle_attachment
from db import init_db, save_email_to_db, load_email_history, delete_email_by_id

# --- Init DB for storing emails ---
init_db()

# --- Persistent User Storage ---
def save_user(email, password):
    users = {}
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
    users[email] = password
    with open("users.json", "w") as f:
        json.dump(users, f)

def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def delete_user(email):
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            users = json.load(f)
        if email in users:
            del users[email]
            with open("users.json", "w") as f:
                json.dump(users, f)

# --- Validate Gmail Login via SMTP ---
def validate_gmail_login(email, password):
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(email, password)
        server.quit()
        return True
    except Exception:
        return False

# --- Streamlit Page Setup ---
st.set_page_config(page_title="MailGenie AI Pro", layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;500;600&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif;
        }
        .main {
            background-image: url('https://images.unsplash.com/photo-1581093588401-99b54bcb07f1');
            background-size: cover;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-position: center;
        }
        .sidebar .sidebar-content {
            background-color: #f0f2f6;
        }
        .scrollable-history {
            max-height: 400px;
            overflow-y: auto;
        }
        .switch-account-btn {
            background-color: #ffffff;
            padding: 8px 12px;
            border-radius: 8px;
            margin: 4px 0;
            width: 100%;
            text-align: left;
            border: 1px solid #ccc;
            font-weight: 500;
        }
        .switch-account-btn:hover {
            background-color: #f0f0f0;
        }
    </style>
""", unsafe_allow_html=True)

# --- Title and Account Controls ---
col_top1, col_top2, col_top3 = st.columns([5, 3, 1])
with col_top1:
    st.title("📬 MailGenie AI Pro - Groq + Gmail + Calendar + Memory")

with col_top2:
    users = load_users()
    current_email = st.session_state.get("email")
    if users:
        with st.expander(f"🔁 Switch Account ({current_email})"):
            for email in users:
                if email != current_email:
                    if st.button(email, key=f"switch_{email}", help=f"Switch to {email}"):
                        st.session_state.email = email
                        st.session_state.password = users[email]
                        st.rerun()

with col_top3:
    if st.button("🚪 Logout"):
        try:
            delete_user(st.session_state.email)
            for file in ["credentials.json", "token.json"]:
                if os.path.exists(file):
                    os.remove(file)
            st.session_state.clear()
            st.success("✅ Logged out successfully.")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Failed to logout: {e}")

# --- Login if not in session ---
if "email" not in st.session_state or "password" not in st.session_state:
    with st.sidebar:
        st.subheader("🔐 Login")
        email = st.text_input("Your Gmail")
        password = st.text_input("Gmail App Password", type="password")
        if st.button("Login"):
            if email and password:
                if validate_gmail_login(email, password):
                    st.session_state.email = email
                    st.session_state.password = password
                    save_user(email, password)
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid Gmail or App Password.")
            else:
                st.warning("⚠️ Please enter both email and password.")
    st.stop()

# --- Sidebar: Sent Emails History for current user ---
st.sidebar.title("📂 Sent Emails History")
with st.sidebar:
    with st.container():
        st.markdown('<div class="scrollable-history">', unsafe_allow_html=True)
        email_history = load_email_history(st.session_state.email)
        if email_history:
            for record in reversed(email_history):
                with st.expander(f"📧 Subject: {record[3]}"):
                    st.markdown(f"**To:** {record[2]}")
                    st.markdown(record[4])
                    if st.button(f"❌ Revoke Email #{record[0]}", key=f"revoke-{record[0]}"):
                        try:
                            delete_email_by_id(record[0])
                            st.success(f"✅ Email ID {record[0]} revoked.")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Failed to revoke email: {e}")
        else:
            st.info("No emails sent yet.")
        st.markdown('</div>', unsafe_allow_html=True)

# --- Main Section: Compose & Schedule ---
with st.container():
    st.subheader("✉️ Compose Email")
    col1, col2 = st.columns(2)
    with col1:
        recipient = st.text_input("Recipient Name")
        to_email = st.text_input("Recipient Email")
        tone = st.selectbox("Select Tone", ["Formal", "Friendly", "Urgent"])
        attachment = st.file_uploader("Attach a file (optional)", type=["pdf", "docx"])
        sender_name = st.text_input("Your Name (for signature)")
    with col2:
        email_content = st.text_area("What do you want to say?", height=250)

# --- Meeting Info ---
with st.expander("📅 Schedule Meeting"):
    date = st.date_input("Meeting Date (optional)")
    time = st.time_input("Meeting Time (optional)")
    if st.button("📌 Schedule Meeting"):
        if recipient and date and time:
            try:
                schedule_meeting(recipient, date, time)
                st.success("📅 Meeting scheduled successfully.")
            except Exception as e:
                st.error(f"❌ Failed to schedule meeting: {e}")
        else:
            st.warning("⚠️ Please enter recipient name, date, and time to schedule a meeting.")

# --- Send Email ---
if st.button("📤 Send Email"):
    if recipient and email_content and to_email and sender_name:
        with st.spinner("📨 Sending email..."):
            try:
                subject, email = generate_email(recipient, email_content, tone, sender_name)
                corrected_email = correct_grammar(email)
                attachment_path = handle_attachment(attachment)
                from_email = st.session_state.email
                password = st.session_state.password
                send_email(from_email, password, to_email, subject, corrected_email, attachment_path)
                save_email_to_db(from_email, to_email, subject, corrected_email)
                st.success("✅ Email sent successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Failed to send email: {e}")
    else:
        st.warning("⚠️ Please fill in all required email fields.")
