import { useGameStore } from "./store";
import { WS_URL } from "./env";

let socket: WebSocket | null = null;
const store = useGameStore.getState();

function connect() {
  const url = `${WS_URL}/crash/stream`;
  if (socket && socket.url === url) {
    return;
  }
  if (socket) {
    socket.close();
  }
  socket = new WebSocket(url);
  socket.onmessage = (ev) => {
    try {
      const msg = JSON.parse(ev.data);
      switch (msg.event) {
        case "round:start":
          store.reset();
          store.setPhase("betting");
          break;
        case "round:fly":
          store.setPhase("flying");
          break;
        case "round:tick":
          store.setMultiplier(msg.data);
          break;
        case "round:crash":
          store.setPhase("crashed");
          store.setMultiplier(msg.data);
          store.addRound(msg.data);
          break;
      }
    } catch (err) {
      console.error("ws message error", err);
    }
  };
  socket.onclose = () => {
    setTimeout(connect, 1000);
  };
}

connect();

export default socket;
