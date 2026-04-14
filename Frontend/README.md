# 🕵️ Criminal Face Generation & Recognition System

<p align="center">
  <img src="Frontend/public/assets/logo.png" alt="Project logo" width="220"/>
</p>

<p align="center">
  Generate composite faces and perform intelligent face matching using Deep Learning.
</p>

---

## 🚀 Overview

This project is a **full-stack web application** that allows users to:

- 🎨 Generate a face by combining facial components (eyes, nose, hair, etc.)
- 🔍 Match faces against a criminal database using AI embeddings
- 🧾 Enroll criminal profiles (Admin only)
- 👥 Search and filter stored profiles
- 🔐 Secure system with role-based access control

---

## ✨ Features

### 🎭 Face Generation (Frontend Editor)
- Interactive UI to build faces using layered assets
- Canvas-based rendering

### 🔎 Face Matching
- Upload image or generated face
- Uses **DeepFace embeddings + cosine similarity**
- Returns closest matches

### 🧑‍💼 Criminal Profile Enrollment (Admin Only)
- Add profile details + image
- Generate and store embeddings in MongoDB

### 🔍 Member Search
- Search by name
- Optional filters (e.g., sex)

### 🔐 Authentication & Authorization
- JWT-based login system
- Role-based access (`ADMIN`, `NORMAL`)

---

## 🧱 Tech Stack

| Layer        | Technology |
|-------------|------------|
| Frontend     | React + Vite |
| Backend      | Flask |
| Database     | MongoDB |
| AI/ML        | DeepFace |
| Image Hosting| Cloudinary |

---

## 📁 Project Structure


Backend/
│── app.py
│── db_inspect.py
│── templates/
│ └── index.html

Frontend/
│── src/
│── public/
│── package.json


---

## ⚙️ Prerequisites

Make sure you have:

- Node.js
- Python 3.x
- MongoDB (Local / Atlas)
- Cloudinary account

---

## 🛠️ Setup Instructions
## ⚙️ Setup Instructions

### 1️⃣ Backend Setup (Flask)

```bash
python -m venv .venv

# Activate environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

pip install flask python-dotenv pymongo pillow cloudinary deepface numpy itsdangerous werkzeug
```

Create a `.env` file inside `Backend/`:

```env
FLASK_SECRET_KEY=your-secret-key
MONGO_CONNECTION_STRING=mongodb://...

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

ADMIN_SECRET_KEY=your-admin-secret
```

Run backend:

```bash
cd Backend
python app.py
```

📍 Backend runs on: `http://localhost:8000`

---

### 2️⃣ Frontend Setup (React + Vite)

```bash
cd Frontend
npm install
npm run dev
```

📍 Frontend runs on: `http://localhost:5173`

⚠️ **Note:** Backend URL is currently hardcoded to `http://localhost:8000`

---

## 🔐 Admin Access Setup

To create an admin user:

1. Add `ADMIN_SECRET_KEY` in `.env`
2. Go to Signup page
3. Select role `ADMIN`
4. Enter the secret key
5. Login → Access `/upload` page

---

## 🔌 API Endpoints

### Authentication

```http
POST /api/auth/signup
POST /api/auth/login
```

### Face Enrollment & Upload

```http
POST /api/enroll       (ADMIN only)
POST /api/upload
```

### Member Search

```http
GET /api/members?name=&sex=
GET /api/latest-criminals?limit=10&status=
```

---

## 🧠 How Face Matching Works

1. Image is uploaded
2. DeepFace generates embedding vector
3. Compare with database embeddings
4. Use cosine similarity to find closest match

---

## 🧰 Utilities

Inspect database records:

```bash
cd Backend
python db_inspect.py
```

---

## 🩺 Troubleshooting

### ❌ Login shows "Server Error"

* Ensure backend is running on port `8000`

### ❌ CORS Issues

* Backend allows ports `5173–5180`

### ❌ Face Matching Not Working

* Use clear, front-facing images
* Wait for model warm-up (1–2 minutes)

---

## 📌 Future Improvements

* 🔄 Real-time face detection (Webcam)
* 📊 Dashboard analytics for crime data
* ⚡ Faster embeddings using GPU
* 🧠 Switch to InsightFace for better accuracy

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Submit a Pull Request

---

## 📜 License

This project is licensed under the **MIT License**

---

## 👨‍💻 Author

**Anshul Rajpoot**
MANIT Bhopal | ECE
