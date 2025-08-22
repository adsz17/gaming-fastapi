import { useState } from "react";
import { register } from "../api";
import styles from "./RegisterPage.module.css";

export default function RegisterPage() {
  const [status, setStatus] = useState<"idle" | "loading" | "error" | "success">("idle");
  const [message, setMessage] = useState("");

  async function onSubmit(e: React.FormEvent<HTMLFormElement>) {
    e.preventDefault();
    const form = e.currentTarget;
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    const fd = new FormData(form);
    const email = String(fd.get("email") || "");
    const username = String(fd.get("username") || "");
    const password = String(fd.get("password") || "");
    if (username.length < 3) {
      setStatus("error");
      setMessage("El usuario debe tener al menos 3 caracteres.");
      return;
    }
    if (password.length < 6) {
      setStatus("error");
      setMessage("La contraseña debe tener al menos 6 caracteres.");
      return;
    }
    setStatus("loading");
    setMessage("");
    try {
      const r: any = await register({ email, username, password });
      localStorage.setItem("token", r.access_token);
      setStatus("success");
      setMessage("Registro exitoso. Redirigiendo...");
      setTimeout(() => { window.location.href = "/"; }, 1500);
    } catch (err: any) {
      if (err?.status === 409 && err?.payload?.detail === "email_taken") {
        setMessage("Ese email ya está registrado.");
      } else if (err?.payload?.detail) {
        setMessage(String(err.payload.detail));
      } else if (err?.message?.includes("Failed to fetch")) {
        setMessage("No se pudo conectar. Reintentá más tarde.");
      } else {
        setMessage("Error registrando.");
      }
      setStatus("error");
    }
  }

  return (
    <div className={styles.container}>
      <div className={styles.card}>
        <h1>Crear cuenta</h1>
        <p>Registrate para empezar a jugar.</p>
        <form onSubmit={onSubmit} noValidate className={styles.form}>
          <div className={styles.field}>
            <label htmlFor="email">Email</label>
            <input id="email" name="email" type="email" autoComplete="email" required />
            <small className={styles.help}>Email inválido</small>
          </div>
          <div className={styles.field}>
            <label htmlFor="username">Usuario</label>
            <input id="username" name="username" minLength={3} autoComplete="username" required />
            <small className={styles.help}>Mínimo 3 caracteres</small>
          </div>
          <div className={styles.field}>
            <label htmlFor="password">Password</label>
            <input id="password" name="password" type="password" minLength={6} autoComplete="new-password" required />
            <small className={styles.help}>Mínimo 6 caracteres</small>
          </div>
          <div className={`${styles.message} ${status === "error" ? styles.error : status === "success" ? styles.success : ""}`} aria-live="polite">
            {message}
          </div>
          <button disabled={status === "loading"} type="submit">
            {status === "loading" && <span className={styles.spinner} aria-hidden="true"></span>}
            Registrarse
          </button>
        </form>
        <a href="/" className={styles.link}>Volver al inicio</a>
      </div>
    </div>
  );
}
