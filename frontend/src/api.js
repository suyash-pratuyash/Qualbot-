export const API_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function requestApi(path, options = {}) {
  const response = await fetch(`${API_URL}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });

  if (!response.ok) {
    const detail = await response.text();
    const error = new Error(detail || `Request failed (${response.status})`);
    error.status = response.status;
    throw error;
  }

  return response.json();
}
