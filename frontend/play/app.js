import { getState, placeBet, getHistory } from './api.js';

const btnAuth = document.getElementById('btnAuth');
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const closeModal = document.getElementById('closeModal');

const lastMultiplier = document.getElementById('lastMultiplier');
const liveMultiplier = document.getElementById('liveMultiplier');
const startBtn = document.getElementById('startBtn');
const roundState = document.getElementById('roundState');

const betAmount = document.getElementById('betAmount');
const cashout = document.getElementById('cashout');
const betBtn = document.getElementById('betBtn');
const balanceEl = document.getElementById('balance');

const multipliers = document.getElementById('multipliers');
const betsTable = document.getElementById('betsTable');

const toastContainer = document.getElementById('toast');

const TOKEN_KEY = 'token';

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function setToken(t) {
  localStorage.setItem(TOKEN_KEY, t);
}

function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

function showToast(msg, type='info') {
  const div = document.createElement('div');
  div.className = `px-4 py-2 rounded shadow text-sm backdrop-blur ${type==='error' ? 'bg-red-500/80 text-white' : 'bg-gray-800/80 text-gray-200'}`;
  div.textContent = msg;
  toastContainer.appendChild(div);
  setTimeout(() => div.remove(), 3000);
}

function updateAuthUI(){
  btnAuth.textContent = getToken() ? 'Perfil' : 'Ingresar';
}

btnAuth.addEventListener('click', () => {
  if (getToken()) {
    // Placeholder for profile
    showToast('Perfil no implementado');
  } else {
    loginModal.classList.remove('hidden');
  }
});

closeModal.addEventListener('click', () => loginModal.classList.add('hidden'));

loginForm.addEventListener('submit', async (e) => {
  e.preventDefault();
  const email = loginForm.email.value.trim();
  const password = loginForm.password.value;
  try {
    const res = await fetch('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if(!res.ok) throw new Error(data.detail || 'Login error');
    setToken(data.token);
    updateAuthUI();
    loginModal.classList.add('hidden');
    showToast('Bienvenido '+ email);
    await refreshAll();
  } catch (err) {
    showToast(err.message, 'error');
  }
});

async function refreshState(){
  try {
    const s = await getState(getToken());
    if (s.last_multiplier !== undefined) {
      lastMultiplier.textContent = `x${Number(s.last_multiplier).toFixed(2)}`;
      lastMultiplier.classList.remove('animate-pulse');
    }
    if (s.multiplier !== undefined) {
      liveMultiplier.textContent = `x${Number(s.multiplier).toFixed(2)}`;
      liveMultiplier.classList.remove('animate-pulse');
    }
    if (s.balance !== undefined) {
      balanceEl.textContent = Number(s.balance).toFixed(2);
    }
    if (s.state) {
      roundState.textContent = s.state;
    }
  } catch (err) {
    console.error(err);
  }
}

async function refreshHistory(){
  try {
    const h = await getHistory(getToken());
    // chips of last multipliers
    multipliers.innerHTML = '';
    (h.multipliers || []).forEach((m) => {
      const chip = document.createElement('button');
      chip.className = 'px-2 py-1 rounded-full bg-gray-700 hover:bg-neon-pink hover:text-gray-900 transition';
      chip.textContent = `x${Number(m).toFixed(2)}`;
      chip.addEventListener('click', () => { cashout.value = m; });
      multipliers.appendChild(chip);
    });
    // table of bets
    betsTable.innerHTML = '';
    (h.bets || []).forEach((b) => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td class="px-2 py-1">${b.player}</td><td class="px-2 py-1">${b.amount}</td><td class="px-2 py-1">${b.cashout}</td><td class="px-2 py-1">${b.result}</td>`;
      betsTable.appendChild(tr);
    });
  } catch (err) {
    console.error(err);
  }
}

async function refreshAll(){
  await Promise.all([refreshState(), refreshHistory()]);
}

betBtn.addEventListener('click', async () => {
  const amount = parseFloat(betAmount.value);
  if(!(amount > 0)) {
    showToast('Monto inválido', 'error');
    return;
  }
  const auto = parseFloat(cashout.value);
  betBtn.disabled = true;
  betBtn.textContent = 'Apostando...';
  try {
    const r = await placeBet(amount, auto, getToken());
    showToast(`Apuesta aceptada x${auto}`);
    await refreshAll();
  } catch (err) {
    showToast(err.message || 'Error de apuesta', 'error');
  } finally {
    betBtn.disabled = false;
    betBtn.textContent = 'Apostar';
  }
});

startBtn.addEventListener('click', async () => {
  await refreshState();
});

setInterval(refreshState, 2000);
refreshAll();
updateAuthUI();
