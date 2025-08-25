import { create } from "zustand";

interface User {
  id: string;
  email: string;
  username: string;
  is_admin: boolean;
}

interface AuthState {
  user?: User;
  balance: number;
  setUser: (u?: User) => void;
  setBalance: (b: number) => void;
  clear: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  user: undefined,
  balance: 0,
  setUser: (user) => set({ user }),
  setBalance: (balance) => set({ balance }),
  clear: () => set({ user: undefined, balance: 0 }),
}));
