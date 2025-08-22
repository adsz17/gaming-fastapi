import { create } from "zustand";

export interface User {
  id: string;
  email: string;
  username: string;
  is_admin: boolean;
}

interface AuthState {
  user: User | null;
  setUser: (u: User | null) => void;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  setUser: (user) => set({ user }),
}));
