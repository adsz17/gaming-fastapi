const API_BASE = "http://127.0.0.1:8000";

function setToken(t){ localStorage.setItem("token", t); }
function getToken(){ return localStorage.getItem("token"); }
function clearToken(){ localStorage.removeItem("token"); }
function isAuthed(){ return !!getToken(); }
