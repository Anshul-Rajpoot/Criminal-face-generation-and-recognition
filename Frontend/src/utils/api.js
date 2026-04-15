const DEFAULT_API_BASE_URL = https://criminal-face-generation-and-recognition.onrender.com ;

function normalizeBaseUrl(url) {
  return String(url || DEFAULT_API_BASE_URL).replace(/\/+$/, "");
}

export const API_BASE_URL = normalizeBaseUrl(import.meta.env.VITE_API_BASE_URL);

export function apiUrl(pathname) {
  const path = String(pathname || "");
  if (!path) return API_BASE_URL;
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  return `${API_BASE_URL}${path.startsWith("/") ? "" : "/"}${path}`;
}
