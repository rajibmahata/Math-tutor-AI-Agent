import { create } from "zustand";
import type { User, AuthState } from "@/types";

interface AuthStore extends AuthState {
  login: (user: User, accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: true,

  login: (user, accessToken, refreshToken) => {
    localStorage.setItem("access_token", accessToken);
    localStorage.setItem("refresh_token", refreshToken);
    set({
      user,
      accessToken,
      refreshToken,
      isAuthenticated: true,
      isLoading: false,
    });
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  },

  setLoading: (loading) => set({ isLoading: loading }),
}));

// Language store
interface LanguageStore {
  language: "en" | "hi" | "bn";
  setLanguage: (lang: "en" | "hi" | "bn") => void;
}

export const useLanguageStore = create<LanguageStore>((set) => ({
  language: "en",
  setLanguage: (language) => {
    localStorage.setItem("preferred_language", language);
    set({ language });
  },
}));
