from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from database import users_collection, qr_collection
from pydantic import BaseModel
from datetime import datetime
import qrcode
import io
import base64
from PIL import Image
import pyzbar.pyzbar as pyzbar

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class SignupUser(BaseModel):
    name: str
    email: str
    password: str

class LoginUser(BaseModel):
    email: str
    password: str

class URLInput(BaseModel):
    email: str
    url: str 

class ScanURL(BaseModel):
    url: str


# Signup
@app.post("/signup")
def signup(user: SignupUser):
    existing = users_collection.find_one({"email": user.email})
    if existing:
        return {"success": False, "message": "Email already exists"}

    users_collection.insert_one({
        "name": user.name,
        "email": user.email,
        "password": user.password,
        "created_at": datetime.utcnow()
    })

    return {"success": True, "message": "Signup successful"}


# Login
@app.post("/login")
def login(user: LoginUser):
    existing = users_collection.find_one({
        "email": user.email,
        "password": user.password
    })

    if existing:
        return {"success": True, "message": "Login successful"}

    return {"success": False, "message": "Invalid email/password"}


# Generate QR
@app.post("/generate-qr")
def generate_qr(data: URLInput):
    qr_img = qrcode.make(data.url)
    buf = io.BytesIO()
    qr_img.save(buf, format="PNG")
    img_bytes = buf.getvalue()
    img_base64 = base64.b64encode(img_bytes).decode("utf-8")

    # Save to DB
    qr_collection.insert_one({
        "email": data.email,
        "url": data.url,
        "created_at": datetime.utcnow()
    })

    return {"success": True, "qr_base64": img_base64}

# Scan QR (from image upload)
@app.post("/scan-qr")
def scan_qr(file: UploadFile = File(...)):
    img = Image.open(file.file)
    decoded = pyzbar.decode(img)
    if not decoded:
        return {"success": False, "message": "No QR found"}
    url = decoded[0].data.decode("utf-8")
    found = qr_collection.find_one({"url": url})
    if found:
        return {"success": True, "url": url, "registered": True}
    else:
        return {"success": True, "url": url, "registered": False}


@app.post("/scan-qr-url")
def scan_qr_url(data: ScanURL):
    found = qr_collection.find_one({"url": data.url})
    if found:
        return {
            "success": True,
            "url": data.url,
            "registered": True
        }
    else:
        return {
            "success": True,
            "url": data.url,
            "registered": False
        }