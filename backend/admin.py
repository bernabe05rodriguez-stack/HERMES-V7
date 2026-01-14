import streamlit as st
import sqlite3
import os
import shutil
import random
import string
import datetime

DB_NAME = "users.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def generate_code(length=12):
    """Generates a random license code like XXXX-XXXX-XXXX"""
    chars = string.ascii_uppercase + string.digits
    part1 = ''.join(random.choices(chars, k=4))
    part2 = ''.join(random.choices(chars, k=4))
    part3 = ''.join(random.choices(chars, k=4))
    return f"{part1}-{part2}-{part3}"

st.set_page_config(page_title="Hermes V7 Admin", layout="wide")
st.title("Hermes V7 - Admin Panel")

# Simple Admin Auth
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    col1, col2, col3 = st.columns([1,1,1])
    with col2:
        user = st.text_input("Admin Username")
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            # Replace these with ENV vars in production
            if user == "Bernabe" and pwd == "Selena":
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("Invalid admin credentials")
else:
    st.sidebar.button("Logout", on_click=lambda: st.session_state.update({"admin_logged_in": False}))

    tab1, tab2 = st.tabs(["License Management", "Software Updates"])

    with tab1:
        st.header("License Management")

        # Generate License
        with st.expander("Generate New License", expanded=True):
            col_gen1, col_gen2, col_gen3 = st.columns(3)
            with col_gen1:
                duration = st.number_input("Duration (Days)", min_value=1, value=30)
            with col_gen2:
                num_licenses = st.number_input("Quantity", min_value=1, value=1)

            if st.button("Generate Code(s)"):
                conn = get_db_connection()
                generated = []
                for _ in range(num_licenses):
                    code = generate_code()
                    try:
                        conn.execute(
                            "INSERT INTO licenses (code, duration_days) VALUES (?, ?)",
                            (code, duration)
                        )
                        generated.append(code)
                    except sqlite3.IntegrityError:
                        pass # Retrying logic could go here but unlikely collision
                conn.commit()
                conn.close()
                st.success(f"Generated {len(generated)} license(s)!")
                for g in generated:
                    st.code(g, language=None)

        # List Licenses
        st.subheader("Existing Licenses")

        # Filter options
        filter_status = st.selectbox("Filter by Status", ["All", "Active", "Expired", "Unused"])

        conn = get_db_connection()
        query = "SELECT * FROM licenses"
        params = []

        # We handle filtering in python for simplicity or basic SQL
        # For simplicity, let's fetch all and filter in python if list isn't huge
        # or do basic SQL tweaks.

        licenses = conn.execute(query).fetchall()
        conn.close()

        # Display table
        data = []
        for lic in licenses:
            status = "Unused"
            if lic["activated_at"]:
                expires = datetime.datetime.fromisoformat(lic["expires_at"])
                if datetime.datetime.now() > expires:
                    status = "Expired"
                else:
                    status = "Active"

            if not lic["is_active"]:
                status = "Disabled"

            if filter_status != "All" and status != filter_status:
                continue

            data.append({
                "ID": lic["id"],
                "Code": lic["code"],
                "Duration": f"{lic['duration_days']} Days",
                "Status": status,
                "HWID": lic["hwid"] if lic["hwid"] else "-",
                "Expires": lic["expires_at"] if lic["expires_at"] else "-",
                "is_active_db": lic["is_active"]
            })

        if data:
            # We construct a custom grid for actions
            for row in data:
                c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 2, 1, 1, 2, 2, 1])
                c1.write(row["ID"])
                c2.code(row["Code"])
                c3.write(row["Duration"])
                c4.write(row["Status"])
                c5.write(row["HWID"])
                c6.write(row["Expires"])

                # Delete Button
                if c7.button("🗑️", key=f"del_{row['ID']}"):
                     conn = get_db_connection()
                     conn.execute("DELETE FROM licenses WHERE id = ?", (row["ID"],))
                     conn.commit()
                     conn.close()
                     st.rerun()
        else:
            st.info("No licenses found.")

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
