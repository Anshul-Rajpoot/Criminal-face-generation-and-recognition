# Criminal Face Generation & Recognition

<p align="center">
  <img src="Frontend/public/assets/logo.png" alt="Project logo" width="240" />
</p>

<p align="center">
  A full‑stack web app that generates a composite face (by layering facial assets), then performs face matching against enrolled profiles stored in MongoDB.
</p>

## ✨ What this project does

- **Face generation (frontend editor)**: build a face by combining hair/eyes/nose/etc. assets on a canvas.
- **Face search**: upload an image (or a generated face) and find the closest matches in the database.
- **Criminal profile enrollment (admin-only)**: add a profile + image, generate face embeddings, store everything in MongoDB.
- **Member search**: search enrolled profiles by name (and optional sex filter).
- **Role-based access control**: only `ADMIN` users can upload/enroll into the database.

## 🧱 Tech stack

- **Frontend**: React + Vite
- **Backend**: Flask
- **Database**: MongoDB (local or Atlas)
- **Face embeddings / matching**: DeepFace (embeddings) + cosine similarity
- **Image hosting**: Cloudinary

## 📁 Repository layout

```text
Backend/
  app.py
  db_inspect.py
  templates/
    index.html
Frontend/
  src/
  public/
  package.json
```

## ✅ Prerequisites

- Node.js (for the React frontend)
- Python 3.x (for the Flask backend)
- MongoDB (local or Atlas)
- Cloudinary account (for image uploads)

## 🚀 Quick start (recommended order)

### 1) Backend (Flask)

Install dependencies (example):

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install flask python-dotenv pymongo pillow cloudinary deepface numpy itsdangerous werkzeug
```

Create environment file: `Backend/.env`

```env
FLASK_SECRET_KEY=your-secret
MONGO_CONNECTION_STRING=mongodb://...

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Required for ADMIN signup + admin-only enroll
ADMIN_SECRET_KEY=...
```

Run the server:

```bash
cd Backend
python app.py
```

Backend runs at `http://localhost:8000`.

### 2) Frontend (React + Vite)

```bash
cd Frontend
npm install
npm run dev
```

Frontend runs at `http://localhost:5173`.

Important: the frontend currently calls the backend at **`http://localhost:8000`** (hard-coded in the UI pages).

## 🔐 Access control (Admin-only uploads)

Uploading/enrolling new profiles into the database is restricted to **ADMIN** users.

How to create an admin user:

1) Set `ADMIN_SECRET_KEY` in `Backend/.env`
2) Open the Signup page in the frontend
3) Choose role `ADMIN` and enter the same Admin Secret Key
4) Login as that admin — the `/upload` page becomes accessible

The legacy Flask HTML form (served at `/`) also requires the Admin Secret Key when enrolling.

## 🔌 Backend API (used by the Frontend)

- `POST /api/auth/signup` — `{ name, email, password, role, adminSecret? }`
- `POST /api/auth/login` — `{ email, password }` → `{ token, user }`
- `POST /api/enroll` — multipart form (**ADMIN only**, requires `Authorization: Bearer <token>`)
- `POST /api/upload` — multipart form (requires `Authorization: Bearer <token>`)
- `GET /api/members?name=...&sex=...` (requires `Authorization: Bearer <token>`)
- `GET /api/latest-criminals?limit=10&status=...`

## 🧰 Utilities

Inspect MongoDB records:

```bash
cd Backend
python db_inspect.py
```

## 🩺 Troubleshooting

- **Login shows “Server error”**: ensure the backend is running on `http://localhost:8000`.
- **CORS errors**: backend allows Vite localhost ports `5173–5180`.
- **Embedding extraction fails**: try a clear, front‑facing image; ML models may take 1–2 minutes to warm up after server start.
