import { io } from "socket.io-client";
import { useGameStore } from "./store";

const socket = io(import.meta.env.VITE_API_URL || "", {
  withCredentials: true,
  autoConnect: true,
});

const store = useGameStore.getState();

socket.on("round:start", () => {
  store.reset();
  store.setPhase("betting");
});

socket.on("round:fly", () => store.setPhase("flying"));

socket.on("round:tick", (m: number) => store.setMultiplier(m));

socket.on("round:crash", (m: number) => {
  store.setPhase("crashed");
  store.setMultiplier(m);
  store.addRound(m);
});

export default socket;
