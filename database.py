import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
client = MongoClient(MONGO_URL)

db = client["qr_system"]
users_collection = db["users"]
qr_collection = db["qr_codes"]
