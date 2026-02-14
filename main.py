from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from database import users_collection, qr_collection
from pydantic import BaseModel
from datetime import datetime
import qrcode
import io
import base64
from PIL import Image
import cv2
import numpy as np
from bson import ObjectId

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://qr-system-by-faruk.netlify.app",
        "http://localhost:3000",
        "https://qr-system-rho.vercel.app/"
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
        "qr_base64": img_base64,
        "created_at": datetime.utcnow()
    })

    return {"success": True, "qr_base64": img_base64}

# Scan QR (from image upload)
@app.post("/scan-qr")
def scan_qr(file: UploadFile = File(...)):
    image_bytes = file.file.read()

    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    detector = cv2.QRCodeDetector()
    data, bbox, _ = detector.detectAndDecode(img)

    if not data:
        return {"success": False, "message": "No QR code detected"}

    found = qr_collection.find_one({"url": data})

    return {
        "success": True,
        "url": data,
        "registered": bool(found)
    }


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
    


@app.get("/user-qrs")
def get_user_qrs(email: str):
    qrs = list(qr_collection.find({"email": email}).sort("created_at", -1))

    # MongoDB ObjectId ke string e convert korte hobe
    for qr in qrs:
        qr["_id"] = str(qr["_id"])

    return {
        "success": True,
        "count": len(qrs),
        "data": qrs
    }
