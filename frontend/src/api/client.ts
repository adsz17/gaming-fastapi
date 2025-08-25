import axios from "axios";

let errorHandler: (msg: string) => void = () => {};
export const setClientErrorHandler = (fn: (msg: string) => void) => {
  errorHandler = fn;
};

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
});

client.interceptors.response.use(
  (res) => res,
  (err) => {
    const msg = err.response?.data?.error || err.message;
    errorHandler(msg);
    return Promise.reject(err);
  }
);

export default client;
