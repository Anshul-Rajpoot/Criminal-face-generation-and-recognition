const DEFAULT_API_BASE_URL = "http://localhost:8000";

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
