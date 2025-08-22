import axios, { AxiosError } from "axios";

const raw = (import.meta.env.VITE_API_URL || "https://gaming-fastapi.onrender.com").replace(/\/$/, "");
const baseURL = raw.startsWith("http://") && !raw.includes("localhost") ? raw.replace("http://", "https://") : raw;

const api = axios.create({
  baseURL,
  withCredentials: true,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err: AxiosError) => {
    if (err.response?.status === 401 && typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
