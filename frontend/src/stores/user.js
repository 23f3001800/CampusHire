import { defineStore } from "pinia";
import api from "@/utils/api";

export const useUserStore = defineStore("user", {
  state: () => ({
    token: localStorage.getItem("token") || null,
    user: (() => {
      try {
        const raw = localStorage.getItem("user");
        return raw ? JSON.parse(raw) : null;
      } catch (e) {
        console.warn("Failed to parse stored user", e);
        return null;
      }
    })(),
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    role: (state) => (state.user && state.user.role ? state.user.role : null),
    id: (state) => state.user?.id || null,
  },

  actions: {
    setToken(token) {
      this.token = token;
      if (token) {
        localStorage.setItem("token", token);
      } else {
        localStorage.removeItem("token");
      }
    },

    setUser(user) {
      this.user = user;
      if (user) {
        try {
          localStorage.setItem("user", JSON.stringify(user));
        } catch (e) {
          console.warn("Failed to serialize user for storage", e);
        }
      } else {
        localStorage.removeItem("user");
      }
    },

    logout() {
      this.setToken(null);
      this.setUser(null);
      this.$router.push("/login");
    },

    loginWithToken(token, user = null) {
      this.setToken(token);
      if (user) this.setUser(user);
    },

    async loginWithCredentials(endpoint = "/auth/login", credentials = {}) {
      const res = await api.post(endpoint, credentials);

      const token =
        res &&
        (res.access_token ||
          res.token ||
          (res.data && (res.data.access_token || res.data.token)));
      const user = res && (res.user || (res.data && res.data.user) || res);

      if (!token) {
        // If the API does not return a token, throw so caller can handle it
        throw new Error("Login response did not include a token");
      }

      this.setToken(token);
      // If `user` is a primitive (like token-only response), prefer null
      this.setUser(typeof user === "object" ? user : null);
      return { token, user };
    },
  },
});