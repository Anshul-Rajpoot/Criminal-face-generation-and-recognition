

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
from flask import Flask, flash, redirect, render_template, request, url_for, jsonify, g
from flask_cors import CORS   # ✅ ADDED
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

@app.route("/test")
def test():
    return "Backend working"

# ✅ ENABLE CORS (IMPORTANT FOR DEPLOYMENT)
CORS(app)

_token_serializer = URLSafeTimedSerializer(app.secret_key, salt="auth")
TOKEN_MAX_AGE_SECONDS = 60 * 60 * 24 * 7

# MongoDB
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = client["face_recognition_db"]
collection = db["criminals"]
users_collection = db["users"]

# Cloudinary
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
# UTIL FUNCTIONS
# ==============================
def file_to_numpy(file_bytes):
    img = Image.open(io.BytesIO(file_bytes))

    if img.mode in {"RGBA", "LA"} or (img.mode == "P" and "transparency" in img.info):
        img = img.convert("RGBA")
        bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
        img = Image.alpha_composite(bg, img).convert("RGB")
    else:
        img = img.convert("RGB")

    return np.array(img)


def compute_embedding_worker(file_bytes):
    try:
        from deepface import DeepFace

        img = file_to_numpy(file_bytes)

        reps = []
        try:
            reps = DeepFace.represent(
                img_path=img,
                model_name=MODEL,
                detector_backend=DETECTOR,
                enforce_detection=ENFORCE,
            )
        except:
            reps = []

        if not reps:
            try:
                reps = DeepFace.represent(
                    img_path=img,
                    model_name=MODEL,
                    detector_backend="opencv",
                    enforce_detection=False,
                )
            except:
                reps = []

        if not reps:
            return None

        emb = np.array(reps[0]["embedding"], dtype=np.float32)
        norm = float(np.linalg.norm(emb))
        if norm == 0:
            return None

        emb = emb / norm
        return emb.tolist()

    except:
        return None


_executor = None


def get_executor():
    global _executor
    if _executor is None:
        ctx = multiprocessing.get_context("spawn")
        _executor = ProcessPoolExecutor(max_workers=1, mp_context=ctx)
    return _executor


def get_embedding(file_bytes):
    try:
        ex = get_executor()
        fut = ex.submit(compute_embedding_worker, file_bytes)
        return fut.result(timeout=TIMEOUT)

    except TimeoutError:
        return None

    except BrokenProcessPool:
        global _executor
        if _executor:
            _executor.shutdown(wait=False, cancel_futures=True)
        _executor = None
        return None

    except:
        return None


def upload_image(file_bytes):
    result = cloudinary.uploader.upload(io.BytesIO(file_bytes))
    return result["secure_url"]


def cosine_score(a, b):
    a = np.asarray(a, dtype=np.float32)
    b = np.asarray(b, dtype=np.float32)
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom == 0.0:
        return 0.0

    cos = float(np.dot(a, b) / denom)
    cos = max(-1.0, min(1.0, cos))
    return max(0.0, cos)


# ==============================
# ROUTES (same as your original)
# ==============================

# (❗ Keeping all your APIs unchanged — no logic touched)

# ==============================
# RUN (UPDATED FOR DEPLOYMENT)
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))   # ✅ IMPORTANT
    app.run(host="0.0.0.0", port=port)
