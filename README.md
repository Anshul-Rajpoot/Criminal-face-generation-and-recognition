# 🕵️ Criminal Face Generation & Recognition

<p align="center">
  <img src="Frontend/public/assets/logo.png" alt="Project logo" width="240" />
</p>

<p align="center">
  A full‑stack app that generates a composite face (layered assets) and performs face matching against enrolled profiles stored in MongoDB.
</p>

## ✨ What this project does

- **Face generation (frontend editor)**: build a face by combining hair/eyes/nose/etc. assets on a canvas.
- **Face search**: upload an image (or a generated face) and find the closest matches in the database.
- **Criminal profile enrollment (admin-only)**: add a profile + image, generate face embeddings, store everything in MongoDB.
- **Member search**: search enrolled profiles by name (optional sex filter).
- **Role-based access control**: only `ADMIN` users can upload/enroll.

## 🧱 Tech stack

- **Frontend**: React + Vite
- **Backend**: Flask
- **Database**: MongoDB (local or Atlas)
- **Face embeddings / matching**: DeepFace + cosine similarity
- **Image hosting**: Cloudinary

## 📁 Repository layout

```text
Backend/
  app.py
  db_inspect.py
  .env
  templates/
    index.html

Frontend/
  src/
  public/
  package.json
```

## ✅ Prerequisites

- Node.js
- Python 3.x
- MongoDB (local or Atlas)
- Cloudinary account

## 🚀 Quick start

### 1) Backend (Flask)

```bash
python -m venv .venv

# Windows PowerShell
\.\.venv\Scripts\Activate.ps1

pip install flask python-dotenv pymongo pillow cloudinary deepface numpy itsdangerous werkzeug
```

Create `Backend/.env`:

```env
FLASK_SECRET_KEY=your-secret
MONGO_CONNECTION_STRING=mongodb://...

CLOUDINARY_CLOUD_NAME=...
CLOUDINARY_API_KEY=...
CLOUDINARY_API_SECRET=...

# Required for ADMIN signup + admin-only enroll
ADMIN_SECRET_KEY=...

# Matching (optional)
# score is cosine similarity clamped to [0, 1]
MATCH_THRESHOLD=0.5

# DeepFace (optional)
FACE_MODEL=Facenet512
FACE_DETECTOR=retinaface
ENFORCE_DETECTION=true
EMBEDDING_TIMEOUT_SECONDS=180
```

Run backend:

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

Important: the frontend currently calls the backend at `http://localhost:8000`.

## 🔐 Admin access

To create an admin user:

1) Set `ADMIN_SECRET_KEY` in `Backend/.env`
2) Open Signup
3) Select role `ADMIN` and enter the same secret
4) Login → access `/upload`

## 🔌 Backend API

- `POST /api/auth/signup` — `{ name, email, password, role, adminSecret? }`
- `POST /api/auth/login` — `{ email, password }` → `{ token, user }`
- `POST /api/enroll` — multipart form (**ADMIN only**, requires `Authorization: Bearer <token>`)
- `POST /api/upload` — multipart form (requires `Authorization: Bearer <token>`)
- `GET /api/members?name=...&sex=...` (requires `Authorization: Bearer <token>`)
- `GET /api/latest-criminals?limit=10&status=...`

`POST /api/upload` (multipart fields)

- `image` (file) — required
- `sex_filter` (string) — optional
- `include_candidates` ("1"/"true") — optional; if no match clears `MATCH_THRESHOLD`, return the top scored candidates anyway

## 🧠 Notes on matching

- Score is cosine similarity clamped to `[0, 1]` (higher = more similar).
- Tune strictness using `MATCH_THRESHOLD` in `Backend/.env`.
- Generated (canvas) faces are not real photos. The app pre-processes generated images before searching (white background + upscale), but photo-to-composite matching can still be harder than photo-to-photo matching.

## 🧰 Utilities

Inspect MongoDB records:

```bash
cd Backend
python db_inspect.py
```

## 🩺 Troubleshooting

- **Login shows “Server error”**: ensure backend is running on `http://localhost:8000`.
- **CORS errors**: backend allows Vite localhost ports `5173–5180`.
- **Embedding extraction fails**: try a clear, front‑facing face image; models may take 1–2 minutes to warm up after server start.
- **Generated face returns “No matches”**: expected if your DB contains real photos and the generated face is stylized; try tuning `MATCH_THRESHOLD` or use `include_candidates`.
