<template>
  <div class="signup-container">
    <div class="container py-5" style="max-width: 720px">
      <div class="card shadow-lg border-0">
        <!-- Header -->
        <div class="card-header bg-primary text-white text-center py-4 border-0">
          <h2 class="mb-0">
            <i class="bi bi-briefcase-fill me-2"></i>Create Your Account
          </h2>
          <p class="text-white-50 mb-0 mt-2">Join CampusHire Today</p>
        </div>

        <div class="card-body p-4">
          <!-- Role Selection -->
          <div class="mb-4">
            <label class="form-label fw-bold">Register As</label>
            <ul class="nav nav-pills gap-2 justify-content-center" role="tablist">
              <li class="nav-item" role="presentation">
                <button
                  class="nav-link"
                  :class="{ active: role === 'student' }"
                  @click="role = 'student'"
                  type="button"
                >
                  <i class="bi bi-mortarboard me-1"></i>Student
                </button>
              </li>
              <li class="nav-item" role="presentation">
                <button
                  class="nav-link"
                  :class="{ active: role === 'recruiter' }"
                  @click="role = 'recruiter'"
                  type="button"
                >
                  <i class="bi bi-briefcase me-1"></i>Recruiter
                </button>
              </li>
            </ul>
          </div>

          <form @submit.prevent="submitSignup" novalidate>
            <div class="row g-3">
              <!-- Common Fields -->
              <div class="col-12 col-md-6">
                <label class="form-label fw-bold" for="name">Full Name</label>
                <input
                  id="name"
                  v-model="name"
                  type="text"
                  class="form-control form-control-lg"
                  placeholder="Jane Doe"
                  required
                />
              </div>

              <div class="col-12 col-md-6">
                <label class="form-label fw-bold" for="email">Email Address</label>
                <input
                  id="email"
                  v-model="email"
                  type="email"
                  class="form-control form-control-lg"
                  placeholder="you@example.com"
                  required
                />
              </div>

              <div class="col-12 col-md-6">
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

              <div class="col-12 col-md-6">
                <label class="form-label fw-bold" for="confirmPassword">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  v-model="confirmPassword"
                  type="password"
                  class="form-control form-control-lg"
                  placeholder="••••••••"
                  required
                />
              </div>

              <!-- Student specific fields -->
              <template v-if="role === 'student'">
                <div class="col-12">
                  <label class="form-label fw-bold" for="rollNumber">Roll Number</label>
                  <input
                    id="rollNumber"
                    v-model="rollNumber"
                    type="text"
                    class="form-control form-control-lg"
                    placeholder="e.g. CS20001"
                    required
                  />
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label fw-bold" for="branch">Branch/Department</label>
                  <select
                    id="branch"
                    v-model="branch"
                    class="form-select form-select-lg"
                    required
                  >
                    <option value="">Select your branch</option>
                    <option value="cse">Computer Science & Engineering</option>
                    <option value="ece">Electronics & Communication</option>
                    <option value="me">Mechanical Engineering</option>
                    <option value="civil">Civil Engineering</option>
                    <option value="ee">Electrical Engineering</option>
                  </select>
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label fw-bold" for="graduation">
                    Expected Graduation Year
                  </label>
                  <input
                    id="graduation"
                    v-model="graduation"
                    type="number"
                    class="form-control form-control-lg"
                    placeholder="2024"
                    min="2024"
                    required
                  />
                </div>

                <div class="col-12">
                  <label class="form-label fw-bold" for="phone">Phone Number</label>
                  <input
                    id="phone"
                    v-model="phone"
                    type="tel"
                    class="form-control form-control-lg"
                    placeholder="+91 98765 43210"
                  />
                </div>
              </template>

              <!-- Recruiter specific fields -->
              <template v-if="role === 'recruiter'">
                <div class="col-12">
                  <label class="form-label fw-bold" for="companyName">Company Name</label>
                  <input
                    id="companyName"
                    v-model="companyName"
                    type="text"
                    class="form-control form-control-lg"
                    placeholder="e.g. Tech Solutions Inc."
                    required
                  />
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label fw-bold" for="department">Department/Division</label>
                  <input
                    id="department"
                    v-model="department"
                    type="text"
                    class="form-control form-control-lg"
                    placeholder="e.g. Human Resources"
                    required
                  />
                </div>

                <div class="col-12 col-md-6">
                  <label class="form-label fw-bold" for="designation">Designation</label>
                  <input
                    id="designation"
                    v-model="designation"
                    type="text"
                    class="form-control form-control-lg"
                    placeholder="e.g. HR Manager"
                    required
                  />
                </div>

                <div class="col-12">
                  <label class="form-label fw-bold" for="phone">Phone Number</label>
                  <input
                    id="phone"
                    v-model="recruiterPhone"
                    type="tel"
                    class="form-control form-control-lg"
                    placeholder="+91 98765 43210"
                    required
                  />
                </div>
              </template>

              <!-- Error Message -->
              <div v-if="error" class="col-12">
                <div class="alert alert-danger mb-0" role="alert">
                  <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
                </div>
              </div>

              <!-- Submit Button -->
              <div class="col-12 d-grid">
                <button
                  class="btn btn-primary btn-lg fw-bold"
                  :disabled="loading"
                  type="submit"
                >
                  <span
                    v-if="loading"
                    class="spinner-border spinner-border-sm me-2"
                    role="status"
                    aria-hidden="true"
                  ></span>
                  {{ loading ? "Creating account…" : "Sign Up" }}
                </button>
              </div>

              <!-- Login Link -->
              <div class="col-12 text-center">
                <small class="text-muted">
                  Already have an account?
                  <router-link to="/login" class="text-primary fw-bold text-decoration-none">
                    Login here
                  </router-link>
                </small>
              </div>
            </div>
          </form>
        </div>
      </div>

      <!-- Terms Text -->
      <p class="text-center text-muted small mt-4">
        By signing up, you agree to our
        <a href="#" class="text-primary text-decoration-none">Terms of Service</a>
        and
        <a href="#" class="text-primary text-decoration-none">Privacy Policy</a>
      </p>
    </div>
  </div>
</template>

<script>
import api from "@/utils/api";
import { useUserStore } from "@/stores/user";

export default {
  name: "SignupPage",
  data() {
    return {
      role: "student",
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      // Student fields
      rollNumber: "",
      branch: "",
      graduation: "",
      phone: "",
      // Recruiter fields
      companyName: "",
      department: "",
      designation: "",
      recruiterPhone: "",
      loading: false,
      error: "",
      userStore: null,
    };
  },
  created() {
    this.userStore = useUserStore();
  },
  methods: {
    async submitSignup() {
      this.error = "";
      if (this.password !== this.confirmPassword) {
        this.error = "Passwords do not match";
        return;
      }

      this.loading = true;
      try {
        const payload = {
          name: this.name,
          email: this.email,
          password: this.password,
          role: this.role,
        };

        if (this.role === "student") {
          payload.student = {
            rollNumber: this.rollNumber,
            branch: this.branch,
            graduation: Number(this.graduation),
            phone: this.phone,
          };
        } else if (this.role === "recruiter") {
          payload.recruiter = {
            companyName: this.companyName,
            department: this.department,
            designation: this.designation,
            phone: this.recruiterPhone,
          };
        }

        // Call signup endpoint (adjust path if your backend uses different URL)
        const res = await api.post("/auth/register", payload);
        // Redirect to login
        alert("Signup successful! Please login.");
        this.$router.push("/login");
      } catch (err) {
        this.error =
          (err && err.message) || "Signup failed. Please try again.";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.signup-container {
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

.nav-pills .nav-link {
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  color: #0d6efd;
  border: 1px solid #0d6efd;
}

.nav-pills .nav-link.active {
  background: linear-gradient(45deg, #0d6efd, #0dcaf0);
  color: #fff;
  border-color: transparent;
}

.form-control-lg,
.form-select-lg {
  border-radius: 8px;
  border: 1px solid #dee2e6;
}

.form-control-lg:focus,
.form-select-lg:focus {
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
</style>