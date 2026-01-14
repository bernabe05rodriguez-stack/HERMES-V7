import customtkinter as ctk
import requests
import subprocess
import sys
import os
import time
import threading
import json
from tkinter import messagebox

# Configuration
API_URL = "https://elhermes.site"  # PROD URL

# Intentar cargar la configuración desde config.json (Opcional, para override)
if os.path.exists("config.json"):
    try:
        with open("config.json", "r") as f:
            config = json.load(f)
            API_URL = config.get("api_url", API_URL)
    except Exception as e:
        print(f"Error loading config.json: {e}")

CURRENT_VERSION = "1.0.0"

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Import Hermes at top level for PyInstaller to detect dependencies
try:
    import Hermes
except ImportError:
    Hermes = None

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hermes Launcher")
        self.geometry("400x500")
        self.resizable(False, False)

        self.hwid = self.get_hwid()
        self.license_file = "license.json"

        # Determine current executable name
        self.app_exe = os.path.basename(sys.executable) if getattr(sys, 'frozen', False) else "launcher.py"

        self.setup_ui()
        # Schedule update check on main thread
        self.after(100, self.start_update_check)

    def get_hwid(self):
        try:
            # Simple HWID generation based on machine GUID (Windows)
            cmd = "wmic csproduct get uuid"
            uuid = subprocess.check_output(cmd).decode().split('\n')[1].strip()
            return uuid
        except:
            return "UNKNOWN_HWID_FALLBACK"

    def setup_ui(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.label_title = ctk.CTkLabel(self.main_frame, text="HΞЯMΞS V7", font=("Arial", 30, "bold"))
        self.label_title.pack(pady=40)

        self.status_label = ctk.CTkLabel(self.main_frame, text="Initializing...", font=("Arial", 12))
        self.status_label.pack(pady=10)

        self.login_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")

        self.license_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Enter License Code")
        self.license_entry.pack(pady=10)

        self.login_btn = ctk.CTkButton(self.login_frame, text="Verify & Launch", command=self.do_verify)
        self.login_btn.pack(pady=20)

    def start_update_check(self):
        self.status_label.configure(text="Checking for updates...")
        threading.Thread(target=self._check_update_thread, daemon=True).start()

    def _check_update_thread(self):
        try:
            response = requests.get(f"{API_URL}/check_update", timeout=5)
            if response.status_code == 200:
                data = response.json()
                server_version = data.get("version", "0.0.0")

                if self.is_newer(server_version, CURRENT_VERSION):
                    self.after(0, lambda: self.status_label.configure(text=f"Update found: {server_version}"))
                    self.after(0, lambda: self.perform_update(data["download_url"], data["filename"]))
                else:
                    self.after(0, lambda: self.status_label.configure(text="Ready to launch"))
                    self.after(0, self.check_license_and_launch)
            else:
                self.after(0, lambda: self.status_label.configure(text="Server error. Offline mode?"))
                self.after(0, self.check_license_and_launch)
        except Exception as e:
            print(f"Update check failed: {e}")
            self.after(0, lambda: self.status_label.configure(text="Update check failed"))
            self.after(0, self.check_license_and_launch)

    def is_newer(self, v1, v2):
        # v1 is server, v2 is current
        return v1 > v2

    def perform_update(self, url, filename):
        # This runs on main thread due to previous `after` call, but downloading should be threaded
        threading.Thread(target=self._download_update_thread, args=(url, filename), daemon=True).start()

    def _download_update_thread(self, url, filename):
        try:
            self.after(0, lambda: self.status_label.configure(text="Downloading update..."))
            # Ensure URL is absolute
            if not url.startswith("http"):
                url = f"{API_URL}{url}"

            r = requests.get(url, stream=True)
            # Use a temporary name for the new file
            new_exe_name = f"new_{self.app_exe}"

            with open(new_exe_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

            self.after(0, lambda: self.status_label.configure(text="Installing..."))

            # Create update batch script using the actual current executable name
            bat_script = f"""
            @echo off
            timeout /t 2 /nobreak > NUL
            del "{self.app_exe}"
            move "{new_exe_name}" "{self.app_exe}"
            start "" "{self.app_exe}"
            del "%~f0"
            """

            with open("update.bat", "w") as f:
                f.write(bat_script)

            self.after(0, lambda: subprocess.Popen("update.bat", shell=True))
            self.after(0, lambda: [self.quit(), sys.exit()])

        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text=f"Update error: {e}"))
            self.after(0, self.show_login)

    def check_license_and_launch(self):
        # Check for saved license
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, "r") as f:
                    data = json.load(f)
                    code = data.get("code")
                    if code:
                        self.status_label.configure(text="Verifying license...")
                        threading.Thread(target=self._verify_thread, args=(code,), daemon=True).start()
                        return
            except Exception:
                pass

        self.show_login()

    def show_login(self):
        self.login_frame.pack(fill="x", pady=10)
        self.status_label.configure(text="Please enter license code")

    def do_verify(self):
        code = self.license_entry.get().strip()
        if not code:
            messagebox.showerror("Error", "Please enter a license code")
            return

        self.status_label.configure(text="Verifying...")
        threading.Thread(target=self._verify_thread, args=(code,), daemon=True).start()

    def _verify_thread(self, code):
        try:
            payload = {"code": code, "hwid": self.hwid}
            response = requests.post(f"{API_URL}/verify_license", json=payload, timeout=5)

            if response.status_code == 200:
                data = response.json()
                # Save license if successful
                with open(self.license_file, "w") as f:
                    json.dump({"code": code}, f)

                self.after(0, lambda: self.status_label.configure(text=f"License valid. Expires: {data.get('expires_at', '?')}"))
                self.after(1000, self.launch_app)
            else:
                msg = response.json().get("detail", "Verification failed")
                self.after(0, lambda: messagebox.showerror("License Error", msg))
                self.after(0, lambda: self.status_label.configure(text="Verification failed"))
                self.after(0, self.show_login)
        except Exception as e:
             self.after(0, lambda: messagebox.showerror("Connection Error", f"Could not connect to server: {e}"))
             self.after(0, lambda: self.status_label.configure(text="Connection error"))
             self.after(0, self.show_login)

    def launch_app(self):
        self.status_label.configure(text="Launching Hermes...")
        self.login_frame.pack_forget()

        # Destroy launcher UI and start Hermes
        try:
            # Add current directory to sys.path
            if os.path.abspath(".") not in sys.path:
                sys.path.append(os.path.abspath("."))

            if Hermes:
                self.destroy()
                Hermes.main()
            else:
                 import Hermes as HermesLate
                 self.destroy()
                 HermesLate.main()

        except ImportError as e:
             messagebox.showerror("Error", f"Could not load Hermes module: {e}")
        except Exception as e:
             messagebox.showerror("Error", f"Error launching Hermes: {e}")

if __name__ == "__main__":
    app = Launcher()
    app.mainloop()
