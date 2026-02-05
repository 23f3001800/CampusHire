// Use environment variable when available, fall back to localhost for development
const baseURL = import.meta.env.VITE_API_BASE_URL || "http://localhost:5000/api";

const api = {
  async request(endpoint, options = {}) {
    // ensure endpoint starts with a slash
    const path = endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
    const url = `${baseURL.replace(/\/$/, "")}${path}`;
    const token = localStorage.getItem("token");

    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    if (token) {
      headers["Authentication-Token"] = token;
    }

    const config = {
      ...options,
      headers,
    };

    try {
      const response = await fetch(url, config);

      if (response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
        throw new Error("Session expired. Please login again.");
      }

      if (response.status === 403) {
        throw new Error("You don't have permission to access this resource.");
      }

      if (!response.ok) {
        let bodyText = null;
        try {
          const json = await response.json();
          bodyText = json.message || json.error || JSON.stringify(json);
        } catch (e) {
          try {
            bodyText = await response.text();
          } catch (e2) {
            /* ignore */
          }
        }
        const message = bodyText
          ? `${response.status} - ${bodyText}`
          : `HTTP error! status: ${response.status}`;
        const err = new Error(message);
        err.status = response.status;
        throw err;
      }

      // 204 No Content or empty body
      if (response.status === 204) return null;
      const text = await response.text();
      if (!text) return null;
      try {
        return JSON.parse(text);
      } catch (e) {
        return text;
      }
    } catch (error) {
      return Promise.reject(error);
    }
  },

  get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "GET" });
  },

  post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "POST",
      body: JSON.stringify(data),
    });
  },

  put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PUT",
      body: JSON.stringify(data),
    });
  },

  patch(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: "PATCH",
      body: JSON.stringify(data),
    });
  },

  delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: "DELETE" });
  },
};

export default api;