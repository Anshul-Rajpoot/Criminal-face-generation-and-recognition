
# import io
# import os
# import re
# from concurrent.futures import ProcessPoolExecutor
# from datetime import datetime
# from functools import wraps

# import cloudinary
# import cloudinary.uploader
# import numpy as np
# from dotenv import load_dotenv
# from flask import Flask, g, jsonify, request
# from itsdangerous import URLSafeTimedSerializer
# from PIL import Image
# from pymongo import MongoClient
# from werkzeug.security import check_password_hash, generate_password_hash

# load_dotenv()

# app = Flask(__name__)
# app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev")

# _token_serializer = URLSafeTimedSerializer(app.secret_key, salt="auth")
# TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7

# MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
# if not MONGO_CONNECTION_STRING:
#     raise RuntimeError("Missing required env var MONGO_CONNECTION_STRING")

# client = MongoClient(MONGO_CONNECTION_STRING)
# db = client["face_recognition_db"]
# collection = db["criminals"]
# users_collection = db["users"]

# cloudinary.config(
#     cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
#     api_key=os.getenv("CLOUDINARY_API_KEY"),
#     api_secret=os.getenv("CLOUDINARY_API_SECRET"),
# )

# THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.3"))
# MODEL = os.getenv("FACE_MODEL", "Facenet512")
# TIMEOUT = int(os.getenv("EMBEDDING_TIMEOUT_SECONDS", "180"))


# @app.after_request
# def add_cors_headers(resp):
#     resp.headers["Access-Control-Allow-Origin"] = "*"
#     resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
#     resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
#     return resp


# @app.get("/")
# def home():
#     return jsonify({"message": "API running"})


# @app.get("/api/health")
# def api_health():
#     return jsonify({"status": "ok"}), 200


# def _issue_token(email, role):
#     return _token_serializer.dumps({"email": email, "role": role})


# def _verify_token(token):
#     return _token_serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)


# def require_auth(required_role=None):
#     def decorator(fn):
#         @wraps(fn)
#         def wrapper(*args, **kwargs):
#             if request.method == "OPTIONS":
#                 return ("", 204)

#             auth = request.headers.get("Authorization", "")
#             if not auth.startswith("Bearer "):
#                 return jsonify({"message": "Missing token"}), 401

#             token = auth.split(" ", 1)[1].strip()
#             try:
#                 payload = _verify_token(token)
#             except Exception:
#                 return jsonify({"message": "Invalid/Expired token"}), 401

#             if required_role and payload.get("role") != required_role:
#                 return jsonify({"message": "Forbidden"}), 403

#             g.user = payload
#             return fn(*args, **kwargs)

#         return wrapper

#     return decorator


# def file_to_numpy(file_bytes: bytes):
#     img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
#     return np.array(img)


# def compute_embedding_worker(file_bytes: bytes):
#     try:
#         from deepface import DeepFace

#         img = file_to_numpy(file_bytes)
#         reps = DeepFace.represent(
#             img_path=img,
#             model_name=MODEL,
#             enforce_detection=False,
#         )
#         emb = np.array(reps[0]["embedding"], dtype=np.float32)
#         norm = float(np.linalg.norm(emb))
#         if norm == 0:
#             return None
#         return (emb / norm).tolist()
#     except Exception:
#         return None


# _executor = None


# def get_embedding(file_bytes: bytes):
#     global _executor
#     if _executor is None:
#         _executor = ProcessPoolExecutor(max_workers=1)
#     try:
#         fut = _executor.submit(compute_embedding_worker, file_bytes)
#         return fut.result(timeout=TIMEOUT)
#     except Exception:
#         return None


# def upload_image(file_bytes: bytes):
#     return cloudinary.uploader.upload(io.BytesIO(file_bytes))["secure_url"]


# def cosine_score(a, b) -> float:
#     a = np.asarray(a, dtype=np.float32)
#     b = np.asarray(b, dtype=np.float32)
#     denom = float(np.linalg.norm(a) * np.linalg.norm(b))
#     if denom == 0:
#         return 0.0
#     return float(np.dot(a, b) / denom)


# @app.route("/api/auth/signup", methods=["POST", "OPTIONS"])
# def signup():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     data = request.get_json(silent=True) or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password") or ""
#     role = (data.get("role") or "NORMAL").strip().upper()

#     if not email or not password:
#         return jsonify({"message": "Missing email/password"}), 400

#     if users_collection.find_one({"email": email}):
#         return jsonify({"message": "User exists"}), 409

#     users_collection.insert_one(
#         {
#             "email": email,
#             "passwordHash": generate_password_hash(password),
#             "role": role,
#             "createdAt": datetime.utcnow(),
#         }
#     )

#     return jsonify({"message": "Signup success"}), 201


# @app.route("/api/auth/login", methods=["POST", "OPTIONS"])
# def login():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     data = request.get_json(silent=True) or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password") or ""

#     if not email or not password:
#         return jsonify({"message": "Missing email/password"}), 400

#     user = users_collection.find_one({"email": email})
#     if not user or not check_password_hash(user.get("passwordHash", ""), password):
#         return jsonify({"message": "Invalid credentials"}), 401

#     role = user.get("role", "NORMAL")
#     token = _issue_token(email, role)
#     return jsonify({"token": token, "user": {"role": role}}), 200


# @app.route("/api/enroll", methods=["POST", "OPTIONS"])
# @require_auth("ADMIN")
# def enroll():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     file = request.files.get("image")
#     if not file:
#         return jsonify({"message": "Upload image"}), 400

#     file_bytes = file.read()
#     emb = get_embedding(file_bytes)
#     if emb is None:
#         return jsonify({"error": "Face not detected"}), 400

#     url = upload_image(file_bytes)

#     doc = {
#         "name": request.form.get("name"),
#         "age": int(request.form.get("age") or 0),
#         "sex": request.form.get("sex"),
#         "crime": request.form.get("crime"),
#         "status": request.form.get("status"),
#         "imageURL": url,
#         "embedding": emb,
#         "createdAt": datetime.utcnow(),
#     }

#     collection.insert_one(doc)
#     return jsonify({"message": "Added"}), 201


# @app.route("/api/members", methods=["GET", "OPTIONS"])
# @require_auth()
# def members_search():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     name = (request.args.get("name") or "").strip()
#     sex = (request.args.get("sex") or "").strip()

#     if not name:
#         return jsonify({"message": "Missing name"}), 400

#     mongo_query = {"name": {"$regex": re.escape(name), "$options": "i"}}
#     if sex and sex != "Any":
#         mongo_query["sex"] = sex

#     members = []
#     for doc in collection.find(mongo_query).sort("createdAt", -1).limit(25):
#         members.append(
#             {
#                 "name": doc.get("name"),
#                 "age": doc.get("age"),
#                 "sex": doc.get("sex"),
#                 "crime": doc.get("crime"),
#                 "status": doc.get("status"),
#                 "imageURL": doc.get("imageURL"),
#             }
#         )

#     return jsonify({"members": members}), 200


# @app.route("/api/upload", methods=["POST", "OPTIONS"])
# @require_auth()
# def upload_match():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     file = request.files.get("image")
#     if not file:
#         return jsonify({"message": "Upload image"}), 400

#     file_bytes = file.read()
#     emb = get_embedding(file_bytes)
#     if emb is None:
#         return jsonify({"matches": []}), 200

#     results = []
#     for doc in collection.find():
#         if "embedding" not in doc:
#             continue
#         try:
#             score = cosine_score(emb, doc["embedding"])
#         except Exception:
#             continue
#         if score >= THRESHOLD:
#             results.append(
#                 {
#                     "name": doc.get("name"),
#                     "score": float(score),
#                     "imageURL": doc.get("imageURL"),
#                 }
#             )

#     results.sort(key=lambda x: x["score"], reverse=True)
#     return jsonify({"matches": results}), 200


# @app.route("/api/latest-criminals", methods=["GET", "OPTIONS"])
# def latest():
#     if request.method == "OPTIONS":
#         return ("", 204)

#     data = []
#     for doc in collection.find().limit(10):
#         data.append(
#             {
#                 "name": doc.get("name"),
#                 "crime": doc.get("crime"),
#                 "status": doc.get("status"),
#                 "imageURL": doc.get("imageURL"),
#             }
#         )
#     return jsonify(data), 200


# if __name__ == "__main__":
#     port = int(os.getenv("PORT", "8000"))
#     app.run(host="0.0.0.0", port=port)




import io
import os
import numpy as np
from datetime import datetime
import multiprocessing
import re
from functools import wraps
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from concurrent.futures.process import BrokenProcessPool

from dotenv import load_dotenv
from flask import Flask, request, jsonify, g
from werkzeug.exceptions import HTTPException
from PIL import Image
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
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
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
client = MongoClient(MONGO_CONNECTION_STRING)
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
THRESHOLD = float(os.getenv("MATCH_THRESHOLD", "0.5"))
MODEL = os.getenv("FACE_MODEL", "Facenet512")
DETECTOR = os.getenv("FACE_DETECTOR", "retinaface")
ENFORCE = os.getenv("ENFORCE_DETECTION", "true").lower() in {"1", "true", "yes"}
TIMEOUT = int(os.getenv("EMBEDDING_TIMEOUT_SECONDS", "180"))

# ==============================
# CORS (simple)
# ==============================
@app.after_request
def add_cors_headers(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return resp


@app.errorhandler(Exception)
def handle_unexpected_error(err):
    # Keep HTTP errors (like 404/405) as-is.
    if isinstance(err, HTTPException):
        return err

    # Always return JSON for unexpected errors so the frontend can display them.
    return jsonify({"message": "Server error"}), 500

# ==============================
# HEALTH
# ==============================
@app.get("/")
def home():
    return jsonify({"message": "API running"})

@app.get("/api/health")
def api_health():
    return jsonify({"status": "ok"}), 200

# ==============================
# AUTH HELPERS
# ==============================
def _issue_token(email, role):
    return _token_serializer.dumps({"email": email, "role": role})

def _verify_token(token):
    return _token_serializer.loads(token, max_age=TOKEN_MAX_AGE_SECONDS)

def require_auth(required_role=None):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if request.method == "OPTIONS":
                return ("", 204)

            auth = request.headers.get("Authorization", "")
            if not auth.startswith("Bearer "):
                return jsonify({"message": "Missing token"}), 401

            token = auth.split(" ", 1)[1]
            try:
                payload = _verify_token(token)
            except:
                return jsonify({"message": "Invalid/Expired token"}), 401

            if required_role and payload.get("role") != required_role:
                return jsonify({"message": "Forbidden"}), 403

            g.user = payload
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# ==============================
# IMAGE + EMBEDDING
# ==============================
def file_to_numpy(file_bytes):
    img = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return np.array(img)

def compute_embedding_worker(file_bytes):
    try:
        from deepface import DeepFace
        img = file_to_numpy(file_bytes)
        reps = DeepFace.represent(img_path=img, model_name=MODEL, enforce_detection=False)
        emb = np.array(reps[0]["embedding"])
        return (emb / np.linalg.norm(emb)).tolist()
    except:
        return None

_executor = None

def get_embedding(file_bytes):
    global _executor
    if _executor is None:
        _executor = ProcessPoolExecutor(max_workers=1)

    try:
        return _executor.submit(compute_embedding_worker, file_bytes).result(timeout=TIMEOUT)
    except:
        return None

def upload_image(file_bytes):
    return cloudinary.uploader.upload(io.BytesIO(file_bytes))["secure_url"]

def cosine_score(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# ==============================
# AUTH ROUTES
# ==============================
@app.route("/api/auth/signup", methods=["POST"])
def signup():
    data = request.json
    email = data["email"]

    if users_collection.find_one({"email": email}):
        return jsonify({"message": "User exists"}), 409

    users_collection.insert_one({
        "email": email,
        "passwordHash": generate_password_hash(data["password"]),
        "role": data.get("role", "NORMAL")
    })

    return jsonify({"message": "Signup success"})

@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.json
    user = users_collection.find_one({"email": data["email"]})

    if not user or not check_password_hash(user["passwordHash"], data["password"]):
        return jsonify({"message": "Invalid credentials"}), 401

    token = _issue_token(user["email"], user.get("role", "NORMAL"))
    return jsonify({"token": token, "user": {"role": user.get("role")}})

# ==============================
# ENROLL
# ==============================
@app.route("/api/enroll", methods=["POST"])
@require_auth("ADMIN")
def enroll():
    file = request.files.get("image")
    if not file:
        return jsonify({"message": "Missing image"}), 400

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
@app.route("/api/upload", methods=["POST"])
@require_auth()
def upload_match():
    file = request.files.get("image")
    if not file:
        return jsonify({"message": "Missing image"}), 400

    file_bytes = file.read()
    emb = get_embedding(file_bytes)

    if emb is None:
        return jsonify({"error": "Face not detected"}), 400

    results = []
    for doc in collection.find():
        if "embedding" not in doc:
            continue

        score = cosine_score(emb, doc["embedding"])
        if score >= THRESHOLD:
            results.append({
                "name": doc["name"],
                "score": score,
                "imageURL": doc["imageURL"]
            })

    return jsonify({"matches": sorted(results, key=lambda x: x["score"], reverse=True)})

# ==============================
# LATEST
# ==============================
@app.route("/api/latest-criminals")
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



