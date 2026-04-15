```python
import io
import os
import numpy as np
from datetime import datetime
import multiprocessing

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
from pymongo import MongoClient
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
CORS(app)

# ==============================
# DATABASE
# ==============================
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = client["face_recognition_db"]
collection = db["criminals"]

# ==============================
# CLOUDINARY
# ==============================
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ==============================
# TEST ROUTE
# ==============================
@app.route("/test")
def test():
    return "Backend working"

# ==============================
# GET LATEST CRIMINALS
# ==============================
@app.route("/api/latest-criminals", methods=["GET"])
def get_latest_criminals():
    try:
        limit = int(request.args.get("limit", 10))
        status = request.args.get("status")

        query = {}
        if status:
            query["status"] = status

        criminals = list(collection.find(query).sort("_id", -1).limit(limit))

        for c in criminals:
            c["_id"] = str(c["_id"])

        return jsonify(criminals)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# ENROLL (ADMIN)
# ==============================
@app.route("/api/enroll", methods=["POST"])
def enroll():
    try:
        name = request.form.get("name")
        age = request.form.get("age")
        sex = request.form.get("sex")
        crime = request.form.get("crime")
        status = request.form.get("status")

        image = request.files.get("image")

        if not image:
            return jsonify({"error": "Image required"}), 400

        # Upload to cloudinary
        result = cloudinary.uploader.upload(image)
        image_url = result["secure_url"]

        data = {
            "name": name,
            "age": age,
            "sex": sex,
            "crime": crime,
            "status": status,
            "imageURL": image_url,
            "createdAt": datetime.utcnow()
        }

        collection.insert_one(data)

        return jsonify({"message": "Criminal added successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
```
