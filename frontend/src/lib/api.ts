import axios, { AxiosError } from "axios";
import { API_URL } from "./env";

const raw = (API_URL || "https://gaming-fastapi.onrender.com").replace(/\/$/, "");
const baseURL = raw.startsWith("http://") && !raw.includes("localhost") ? raw.replace("http://", "https://") : raw;

const api = axios.create({
  baseURL,
  withCredentials: true,
  headers: { "Content-Type": "application/json" },
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
