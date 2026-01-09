import streamlit as st
import sqlite3
import os
import shutil
from auth import get_password_hash

DB_NAME = "users.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

st.title("Hermes V7 - Admin Panel")

# Simple Admin Auth
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    user = st.text_input("Admin Username")
    pwd = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        # Replace these with ENV vars in production
        if user == "admin" and pwd == "admin123":
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid admin credentials")
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_logged_in": False}))

    tab1, tab2 = st.tabs(["Users", "Updates"])

    with tab1:
        st.header("User Management")

        # Add User
        with st.expander("Add New User"):
            new_user = st.text_input("Username")
            new_pass = st.text_input("Password", type="password")
            if st.button("Create User"):
                if new_user and new_pass:
                    hashed = get_password_hash(new_pass)
                    try:
                        conn = get_db_connection()
                        c = conn.cursor()
                        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (new_user, hashed))
                        conn.commit()
                        conn.close()
                        st.success(f"User {new_user} created!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        # List Users
        conn = get_db_connection()
        users = conn.execute("SELECT * FROM users").fetchall()
        conn.close()

        for user in users:
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.write(user["username"])
            col2.write(f"HWID: {user['hwid'] if user['hwid'] else 'None'}")
            col3.write(f"Active: {bool(user['active'])}")

            if col4.button("Toggle Active", key=f"act_{user['id']}"):
                conn = get_db_connection()
                conn.execute("UPDATE users SET active = NOT active WHERE id = ?", (user["id"],))
                conn.commit()
                conn.close()
                st.rerun()

            if col5.button("Reset HWID", key=f"rst_{user['id']}"):
                conn = get_db_connection()
                conn.execute("UPDATE users SET hwid = NULL WHERE id = ?", (user["id"],))
                conn.commit()
                conn.close()
                st.rerun()

    with tab2:
        st.header("Software Updates")

        uploaded_file = st.file_uploader("Upload new HermesV7.exe", type=["exe", "zip"])
        version_input = st.text_input("Version (e.g., 1.0.5)")

        if st.button("Publish Update"):
            if uploaded_file and version_input:
                file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                conn = get_db_connection()
                try:
                    conn.execute("INSERT INTO updates (version, filename) VALUES (?, ?)", (version_input, uploaded_file.name))
                    conn.commit()
                    st.success(f"Version {version_input} published!")
                except sqlite3.IntegrityError:
                    st.error("Version already exists.")
                finally:
                    conn.close()
            else:
                st.error("Please provide file and version.")

        # List updates
        conn = get_db_connection()
        updates = conn.execute("SELECT * FROM updates ORDER BY id DESC").fetchall()
        conn.close()

        if updates:
            st.write("Recent Updates:")
            st.table([{"Version": u["version"], "File": u["filename"], "Date": u["release_date"]} for u in updates])
