import { createContext, useContext, useEffect, useMemo, useState } from "react";

import api, { setAuthToken } from "@/lib/api";

const AuthContext = createContext(null);
const STORAGE_KEY = "arquicontrol-session-token";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem(STORAGE_KEY) || "");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function bootstrap() {
      if (!token) {
        setAuthToken(null);
        setIsLoading(false);
        return;
      }

      try {
        setAuthToken(token);
        const response = await api.get("/auth/me");
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem(STORAGE_KEY);
        setAuthToken(null);
        setToken("");
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    bootstrap();
  }, [token]);

  const value = useMemo(
    () => ({
      user,
      token,
      isLoading,
      isAuthenticated: Boolean(user),
      async login(credentials) {
        const response = await api.post("/auth/login", credentials);
        localStorage.setItem(STORAGE_KEY, response.data.token);
        setAuthToken(response.data.token);
        setToken(response.data.token);
        setUser(response.data.user);
        return response.data.user;
      },
      logout() {
        localStorage.removeItem(STORAGE_KEY);
        setAuthToken(null);
        setToken("");
        setUser(null);
      },
    }),
    [isLoading, token, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider");
  }
  return context;
}