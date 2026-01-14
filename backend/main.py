from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from datetime import datetime, timedelta
from database import get_db_connection
from models import LicenseVerification, UpdateInfo

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/verify_license")
def verify_license(license_data: LicenseVerification):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM licenses WHERE code = ?", (license_data.code,))
    row = c.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=401, detail="Invalid license code")

    if not row["is_active"]:
        conn.close()
        raise HTTPException(status_code=403, detail="License is disabled")

    # Check activation
    if row["activated_at"]:
        # Already activated
        if row["hwid"] != license_data.hwid:
            conn.close()
            raise HTTPException(status_code=403, detail="License code used on another device")

        # Check expiration
        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.now() > expires_at:
            conn.close()
            raise HTTPException(status_code=403, detail="License expired")

        conn.close()
        return {
            "message": "License valid",
            "expires_at": row["expires_at"]
        }
    else:
        # First activation
        now = datetime.now()
        expires_at = now + timedelta(days=row["duration_days"])

        c.execute("""
            UPDATE licenses
            SET hwid = ?, activated_at = ?, expires_at = ?
            WHERE id = ?
        """, (license_data.hwid, now.isoformat(), expires_at.isoformat(), row["id"]))
        conn.commit()
        conn.close()

        return {
            "message": "License activated successfully",
            "expires_at": expires_at.isoformat()
        }

@app.get("/check_update")
def check_update():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM updates ORDER BY id DESC LIMIT 1")
    row = c.fetchone()
    conn.close()

    if row:
        return {
            "version": row["version"],
            "download_url": f"/download/{row['filename']}",
            "filename": row["filename"]
        }
    return {"version": "0.0.0", "download_url": "", "filename": ""}

@app.get("/download/{filename}")
def download_file(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename)
    raise HTTPException(status_code=404, detail="File not found")
