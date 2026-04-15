
import io
import os
import numpy as np
from datetime import datetime
from functools import wraps
from concurrent.futures import ProcessPoolExecutor, TimeoutError

from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from PIL import Image
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
import cloudinary
import cloudinary.uploader

# ==============================
# LOAD ENV
# ==============================
load_dotenv()

# ==============================
# CONFIG
# ==============================
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

_token_serializer = URLSafeTimedSerializer(app.secret_key, salt="auth")
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7

# ==============================
# DATABASE
# ==============================
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = client["face_recognition_db"]
collection = db["criminals"]
users_collection = db["users"]

# ==============================
# CLOUDINARY
# ==============================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ==============================
# SETTINGS
# ==============================
THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.3"))
TIMEOUT = 180

# ==============================
# CORS
# ==============================
@app.after_request
def cors(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp

# ==============================
# HEALTH
# ==============================
@app.get("/")
def home():
    return jsonify({"message": "API running"})

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

# ==============================
# AUTH
# ==============================
def issue_token(email, role):
    return _token_serializer.dumps({"email": email, "role": role})

def verify_token(token):
    return _token_serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)

def require_auth(role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"message": "Missing token"}), 401

            token = auth.split(" ")[1]
            try:
                data = verify_token(token)
            except:
                return jsonify({"message": "Invalid token"}), 401

            if role and data.get("role") != role:
                return jsonify({"message": "Forbidden"}), 403

            g.user = data
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ==============================
# IMAGE UTILS
# ==============================
def file_to_numpy(bytes_data):
    img = Image.open(io.BytesIO(bytes_data)).convert("RGB")
    return np.array(img)

def compute_embedding(bytes_data):
    try:
        from deepface import DeepFace
        img = file_to_numpy(bytes_data)
        rep = DeepFace.represent(img_path=img, enforce_detection=False)
        emb = np.array(rep[0]["embedding"])
        return (emb / np.linalg.norm(emb)).tolist()
    except:
        return None

executor = ProcessPoolExecutor(max_workers=1)

def get_embedding(bytes_data):
    try:
        return executor.submit(compute_embedding, bytes_data).result(timeout=TIMEOUT)
    except:
        return None

def upload_image(bytes_data):
    return cloudinary.uploader.upload(io.BytesIO(bytes_data))["secure_url"]

def cosine(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ==============================
# AUTH ROUTES
# ==============================
@app.post("/api/auth/signup")
def signup():
    data = request.json
    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"message": "User exists"}), 409

    users_collection.insert_one({
        "email": data["email"],
        "passwordHash": generate_password_hash(data["password"]),
        "role": data.get("role", "NORMAL")
    })

    return jsonify({"message": "Signup success"})

@app.post("/api/auth/login")
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["passwordHash"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = issue_token(user["email"], user["role"])
    return jsonify({"token": token, "user": {"role": user["role"]}})

# ==============================
# ENROLL
# ==============================
@app.post("/api/enroll")
@require_auth("ADMIN")
def enroll():
    file = request.files["image"]
    file_bytes = file.read()

    emb = get_embedding(file_bytes)
    if emb is None:
        return jsonify({"error": "Face not detected"}), 400

    url = upload_image(file_bytes)

    doc = {
        "name": request.form["name"],
        "age": int(request.form["age"]),
        "sex": request.form["sex"],
        "crime": request.form["crime"],
        "status": request.form["status"],
        "imageURL": url,
        "embedding": emb,
        "createdAt": datetime.utcnow()
    }

    collection.insert_one(doc)
    return jsonify({"message": "Added"})

# ==============================
# MATCH
# ==============================
@app.post("/api/upload")
@require_auth()
def match():
    file = request.files["image"]
    file_bytes = file.read()

    emb = get_embedding(file_bytes)
    if emb is None:
        return jsonify({"matches": []})

    results = []

    for doc in collection.find():
        if "embedding" not in doc:
            continue

        score = cosine(emb, doc["embedding"])
        if score >= THRESHOLD:
            results.append({
                "name": doc["name"],
                "score": score,
                "imageURL": doc["imageURL"]
            })

    results = sorted(results, key=lambda x: x["score"], reverse=True)
    return jsonify({"matches": results})

# ==============================
# LATEST
# ==============================
@app.get("/api/latest-criminals")
def latest():
    data = []
    for doc in collection.find().limit(10):
        data.append({
            "name": doc.get("name"),
            "imageURL": doc.get("imageURL")
        })
    return jsonify(data)

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port)

