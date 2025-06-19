# 📁 File: frontend/app.py (Streamlit Frontend)
import streamlit as st
import requests
from datetime import datetime, date as dt_date, time as dt_time

API_URL = "http://backend:8000"
st.set_page_config(page_title="Secure Collaboration", layout="wide")

st.title("🔐 Secure Virtual Collaboration Platform")

if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# Signup Section
with st.expander("👤 Create New Account"):
    signup_username = st.text_input("New Username", key="signup_username")
    signup_email = st.text_input("Email", key="signup_email")
    signup_password = st.text_input("Password", type="password", key="signup_password")
    signup_role = st.selectbox("Role", ["admin", "member", "guest"], key="signup_role")
    if st.button("Signup"):
        payload = {
            "username": signup_username,
            "email": signup_email,
            "password": signup_password,
            "role": signup_role
        }
        res = requests.post(f"{API_URL}/signup", json=payload)
        if res.status_code == 200:
            st.success("User registered successfully!")
        else:
            st.error("Failed to register user.")

# Login Section
st.subheader("🔑 Login")
username = st.text_input("Username", key="login_username")
if st.button("Login"):
    try:
        role_res = requests.get(f"{API_URL}/user-role/{username}")
        if role_res.status_code == 200:
            st.session_state.username = username
            st.session_state.role = role_res.json().get("role", "")
            st.success(f"Logged in as {username} ({st.session_state.role})")
        else:
            st.warning("User not found in database.")
    except:
        st.warning("Could not connect to API.")

username = st.session_state.username
role = st.session_state.role

if role == "admin":
    st.subheader("📢 Post a New Announcement")
    with st.form("announcement_form"):
        title = st.text_input("Title")
        content = st.text_area("Content")
        if st.form_submit_button("Post Announcement"):
            payload = {"title": title, "content": content, "created_by": username}
            res = requests.post(f"{API_URL}/announcements/", json=payload)
            if res.status_code == 200:
                st.success("✅ Announcement posted successfully!")
            else:
                st.error("❌ Failed to post announcement.")

    st.markdown("---")
    st.subheader("📋 Activity Logs")
    logs = requests.get(f"{API_URL}/logs/").json()
    st.dataframe(logs, use_container_width=True)

    st.markdown("---")
    st.subheader("👥 User Management")
    users = requests.get(f"{API_URL}/users").json()
    if users:
        st.dataframe(users)
        selected_email = st.selectbox("Select user to update", [u['email'] for u in users])
        new_username = st.text_input("New Username")
        new_role = st.selectbox("New Role", ["admin", "member", "guest"])
        if st.button("Update User"):
            payload = {"username": new_username, "role": new_role}
            res = requests.put(f"{API_URL}/users/{selected_email}", json=payload)
            if res.status_code == 200:
                st.success("User updated successfully!")
            else:
                st.error("Failed to update user.")
        if st.button("Delete User"):
            res = requests.delete(f"{API_URL}/users/{selected_email}")
            if res.status_code == 200:
                st.success("User deleted successfully!")
            else:
                st.error("Failed to delete user.")

if role in ["admin", "member"]:
    st.markdown("---")
    st.subheader("📅 Create Meeting")
    meeting_title = st.text_input("Meeting Title")
    meeting_date = st.date_input("Start Date")
    meeting_time_only = st.time_input("Start Time")
    if st.button("Create Meeting"):
        start_time = datetime.combine(meeting_date, meeting_time_only).isoformat()
        payload = {"title": meeting_title, "start_time": start_time}
        res = requests.post(f"{API_URL}/meetings", json=payload)
        if res.status_code == 200:
            st.success("Meeting created successfully!")
        else:
            st.error("Failed to create meeting.")

if role in ["admin", "member", "guest"]:
    st.markdown("---")
    st.subheader("📰 Latest Announcements")
    res = requests.get(f"{API_URL}/announcements/")
    if res.status_code == 200:
        for ann in res.json():
            st.markdown(f"### 📌 {ann['title']}")
            st.write(ann['content'])
            st.caption(f"Posted by {ann['created_by']} on {ann['created_at']}")

    st.markdown("---")
    st.subheader("💬 Send Message")
    chatroom_id = st.number_input("Chatroom ID", min_value=1, step=1)
    message = st.text_input("Your Message")
    if st.button("Send Message"):
        payload = {"chatroom_id": chatroom_id, "content": message}
        res = requests.post(f"{API_URL}/messages", json=payload)
        if res.status_code == 200:
            st.success("Message sent successfully!")
        else:
            st.error("Failed to send message.")

    st.markdown("---")
    st.subheader("📂 Upload File")
    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file and st.button("Upload File"):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        res = requests.post(f"{API_URL}/upload", files=files)
        if res.status_code == 200:
            st.success("File uploaded successfully!")
        else:
            st.error("File upload failed!")
