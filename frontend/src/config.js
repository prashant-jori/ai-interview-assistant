const defaultBackend =
  typeof window !== "undefined" && window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000"
    : "https://ai-interview-assistant-1-hwco.onrender.com";

export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || defaultBackend;