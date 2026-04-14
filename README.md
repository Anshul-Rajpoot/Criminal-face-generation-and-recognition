# Criminal Face Generation & Recognition

Full‑stack college project for enrolling “criminal” profiles with face embeddings and matching a query face against stored profiles.

## Project Structure

- `Backend/` — Flask API + simple HTML page, MongoDB storage, Cloudinary image uploads
- `Frontend/` — React (Vite) UI that talks to the Flask API

## Prerequisites

- Node.js (for the React frontend)
- Python 3.x (for the Flask backend)
- MongoDB (local or Atlas)
- Cloudinary account (for image hosting)

## Backend Setup (Flask)

1) Create a Python environment and install dependencies.

	Example (venv):
	- `python -m venv .venv`
	- Windows PowerShell: `.\.venv\Scripts\Activate.ps1`
	- `pip install flask python-dotenv pymongo pillow cloudinary deepface numpy itsdangerous werkzeug`

	Notes:
	- `deepface` may take time to install the first time and can pull in additional ML dependencies.
	- If embeddings fail right after server start, try again after 1–2 minutes (model warm-up).

2) Create a `Backend/.env` file (or set these variables in your shell):

	- `FLASK_SECRET_KEY=your-secret`
	- `MONGO_CONNECTION_STRING=mongodb://...` (or Atlas connection string)
	- `CLOUDINARY_CLOUD_NAME=...`
	- `CLOUDINARY_API_KEY=...`
	- `CLOUDINARY_API_SECRET=...`

	Optional:
	- `ADMIN_SECRET_KEY=...` (required to sign up an ADMIN user)
	- `MATCH_THRESHOLD=0.6`
	- `FACE_MODEL=Facenet512`
	- `FACE_DETECTOR=retinaface`
	- `ENFORCE_DETECTION=true`
	- `EMBEDDING_TIMEOUT_SECONDS=180`

3) Run the backend:

	- `cd Backend`
	- `python app.py`

	Server runs on: `http://localhost:8000`

### Backend Endpoints (used by the Frontend)

- `POST /api/auth/signup` — `{ name, email, password, role, adminSecret? }`
- `POST /api/auth/login` — `{ email, password }` → `{ token, user }`
- `POST /api/enroll` — multipart form (**ADMIN only**, requires Bearer token)
- `POST /api/upload` — multipart form (requires Bearer token)
- `GET /api/members?name=...&sex=...` (requires Bearer token)
- `GET /api/latest-criminals?limit=10&status=...`

### Optional Utilities

- Inspect MongoDB records:
  - `cd Backend`
  - `python db_inspect.py`

## Frontend Setup (React + Vite)

1) Install dependencies:

- `cd Frontend`
- `npm install`

2) Run the dev server:

- `npm run dev`

Frontend runs on: `http://localhost:5173`

Important: the frontend is currently hard-coded to use `http://localhost:8000` as the backend base URL.

## Typical Dev Workflow

1) Start MongoDB and ensure `MONGO_CONNECTION_STRING` is set.
2) Start backend on port `8000`.
3) Start frontend on port `5173`.

## Access Control (Admin-only uploads)

- Uploading/enrolling new criminal data into the database is restricted to `ADMIN` users.
- To create an admin account, set `ADMIN_SECRET_KEY` in `Backend/.env` and choose role `ADMIN` on the Signup page.
- The legacy Flask HTML form at `/` also requires the same `ADMIN_SECRET_KEY` value to enroll records.

## Troubleshooting

- **“Backend not reachable”**: confirm Flask is running on `http://localhost:8000`.
- **CORS errors**: backend allows localhost Vite ports (5173–5180). Make sure you are using a localhost URL.
- **Embedding extraction fails**: use a clear, front-facing face image; try again after warm-up.
