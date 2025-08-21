import { registerUser } from "../api/client";

export function initRegisterPage() {
  const form = document.querySelector<HTMLFormElement>("#register-form");
  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const payload = {
        email: String(fd.get("email") || ""),
        username: String(fd.get("username") || ""),
        password: String(fd.get("password") || ""),
      };
      try {
        const res = await registerUser(payload);
        localStorage.setItem("token", res.access_token);
        alert("Registrado!");
      } catch (err: any) {
        alert("Error registrando: " + err.message);
      }
    });
  }
}
