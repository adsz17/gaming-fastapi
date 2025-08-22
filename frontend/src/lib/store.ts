import { create } from "zustand";

export type Phase = "idle" | "betting" | "flying" | "crashed";

interface GameState {
  phase: Phase;
  multiplier: number;
  bet: number;
  autoCashout: number;
  balance: number;
  lastRounds: number[];
  setPhase: (phase: Phase) => void;
  setMultiplier: (m: number) => void;
  setBet: (b: number) => void;
  setAutoCashout: (a: number) => void;
  setBalance: (b: number) => void;
  addRound: (m: number) => void;
  reset: () => void;
}

export const useGameStore = create<GameState>((set) => ({
  phase: "idle",
  multiplier: 1,
  bet: 0,
  autoCashout: 0,
  balance: 0,
  lastRounds: [],
  setPhase: (phase) => set({ phase }),
  setMultiplier: (multiplier) => set({ multiplier }),
  setBet: (bet) => set({ bet }),
  setAutoCashout: (autoCashout) => set({ autoCashout }),
  setBalance: (balance) => set({ balance }),
  addRound: (m) => set((s) => ({ lastRounds: [m, ...s.lastRounds].slice(0, 10) })),
  reset: () => set({ phase: "idle", multiplier: 1, bet: 0 }),
}));
