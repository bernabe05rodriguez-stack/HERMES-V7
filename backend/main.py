from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import shutil
import os
from database import get_db_connection
from models import UserLogin, UpdateInfo
from auth import verify_password

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/login")
def login(user: UserLogin):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (user.username,))
    row = c.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not verify_password(user.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not row["active"]:
        raise HTTPException(status_code=403, detail="Account is disabled")

    # HWID Check
    if row["hwid"]:
        if row["hwid"] != user.hwid:
            raise HTTPException(status_code=403, detail="HWID mismatch. Contact admin.")
    else:
        # First login, bind HWID
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE users SET hwid = ? WHERE id = ?", (user.hwid, row["id"]))
        conn.commit()
        conn.close()

    return {"message": "Login successful", "token": "dummy-token-for-now"}

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
