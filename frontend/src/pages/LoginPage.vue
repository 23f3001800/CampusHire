<template>
  <div class="login-container">
    <div class="container py-5" style="max-width: 450px">
      <div class="card shadow-lg border-0">
        <!-- Header -->
        <div class="card-header bg-primary text-white text-center py-4 border-0">
          <h2 class="mb-0">
            <i class="bi bi-briefcase-fill me-2"></i>CampusHire
          </h2>
          <p class="text-white-50 mb-0 mt-2">Launch Your Career Today</p>
        </div>

        <div class="card-body p-4">
          <!-- Login Form -->
          <form @submit.prevent="submitLogin" novalidate>
            <div class="mb-3">
              <label class="form-label fw-bold" for="email">Email Address</label>
              <input
                id="email"
                v-model="email"
                type="email"
                class="form-control form-control-lg"
                placeholder="you@study.com"
                required
              />
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold" for="password">Password</label>
              <input
                id="password"
                v-model="password"
                type="password"
                class="form-control form-control-lg"
                placeholder="••••••••"
                required
              />
            </div>

            <!-- Remember & Forgot Password -->
            <div class="d-flex justify-content-between align-items-center mb-4">
              <div class="form-check">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="remember"
                  v-model="rememberMe"
                />
                <label class="form-check-label small" for="remember">
                  Remember me
                </label>
              </div>
              <a href="#" class="text-primary text-decoration-none small fw-bold">
                Forgot password?
              </a>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="alert alert-danger mb-3" role="alert">
              <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
            </div>

            <!-- Submit Button -->
            <button
              type="submit"
              class="btn btn-primary btn-lg w-100 fw-bold"
              :disabled="loading"
            >
              <span
                v-if="loading"
                class="spinner-border spinner-border-sm me-2"
                role="status"
                aria-hidden="true"
              ></span>
              {{ loading ? "Signing in…" : "Sign In" }}
            </button>
          </form>

          <!-- Divider -->
          <div class="my-4 position-relative">
            <hr />
            <span class="position-absolute top-50 start-50 translate-middle bg-white px-2 text-muted small">
              or
            </span>
          </div>

          <!-- Sign Up Link -->
          <p class="text-center text-muted mb-0">
            Don't have an account?
            <router-link to="/signup" class="text-primary fw-bold text-decoration-none">
              Sign up here
            </router-link>
          </p>
        </div>
      </div>

      <!-- Footer Text -->
      <p class="text-center text-muted small mt-4">
        By signing in, you agree to our
        <a href="#" class="text-primary text-decoration-none">Terms of Service</a>
        and
        <a href="#" class="text-primary text-decoration-none">Privacy Policy</a>
      </p>
    </div>
  </div>
</template>

<script>
import { useUserStore } from "@/stores/user";

export default {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
      rememberMe: false,
      loading: false,
      error: "",
      userStore: null,
      role: "",
      id: null,
    };
  },
  setup() {
    const userStore = useUserStore();
    return {
      userStore,
    };
  },
  created() {
      if (this.userStore.isAuthenticated) {
      if (this.userStore.role === "admin") {
        this.$router.push(`/admin/${this.userStore.id}`);
      } else if (this.userStore.role === "company") {
        this.$router.push(`/company/${this.userStore.id}`);
      } else if (this.userStore.role === "student") {
        this.$router.push(`/student/${this.userStore.id}`);
      }
    }
  },
  methods: {
    async submitLogin() {
      this.error = "";
      this.loading = true;
      try {
        // call with endpoint then credentials (store expects (endpoint, credentials))
        await this.userStore.loginWithCredentials("/auth/login", {
          email: this.email,
          password: this.password,
        });
        //this.$router.push("/${this.userStore.role}/${this.userStore.id}");
        if (this.userStore.role === "admin") {
          this.$router.push(`/admin/${this.userStore.id}`);
        } else if (this.userStore.role === "company") {
          this.$router.push(`/company/${this.userStore.id}`);
        } else if (this.userStore.role === "student") {
          this.$router.push(`/student/${this.userStore.id}`);
        } else {
          this.error = "Unknown user role";
        }
      } catch (e) {
        this.error = e.message || "Login failed";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.card {
  border-radius: 12px;
  overflow: hidden;
}

.card-header {
  background: linear-gradient(45deg, #0d6efd, #0dcaf0) !important;
}

.form-control-lg {
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.form-control-lg:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 0.2rem rgba(13, 110, 253, 0.25);
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover:not(:disabled) {
  background-color: #0b5ed7;
  border-color: #0b5ed7;
}

.btn-primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

hr {
  opacity: 0.2;
}
</style>