<template>
  <div class="signup-page">
    <div class="container py-5" style="max-width:700px">
      <div class="card shadow-lg border-0">

        <div class="card-header text-white text-center py-4 border-0">
          <h2 class="mb-0"><i class="bi bi-briefcase-fill me-2"></i>Create Your Account</h2>
          <p class="text-white-50 mb-0 mt-1">Join CampusHire Today</p>
        </div>

        <div class="card-body p-4">
          <!-- Role selector -->
          <div class="mb-4 text-center">
            <div class="btn-group" role="group">
              <button type="button" class="btn"
                :class="role === 'student' ? 'btn-primary' : 'btn-outline-primary'"
                @click="role = 'student'">
                <i class="bi bi-mortarboard me-1"></i>Student
              </button>
              <button type="button" class="btn"
                :class="role === 'company' ? 'btn-primary' : 'btn-outline-primary'"
                @click="role = 'company'">
                <i class="bi bi-briefcase me-1"></i>Recruiter
              </button>
            </div>
          </div>

          <form @submit.prevent="submit" novalidate>
            <div class="row g-3">

              <!-- Common fields -->
              <div class="col-md-6">
                <label class="form-label fw-bold">Full Name</label>
                <input v-model="form.name" type="text" class="form-control" placeholder="Jane Doe" required />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold">Email Address</label>
                <input v-model="form.email" type="email" class="form-control" placeholder="you@example.com" required />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold">Password</label>
                <input v-model="form.password" type="password" class="form-control" placeholder="Min 6 characters" required />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-bold">Confirm Password</label>
                <input v-model="form.confirmPassword" type="password" class="form-control" placeholder="Repeat password" required />
              </div>

              <!-- Student fields -->
              <template v-if="role === 'student'">
                <div class="col-12">
                  <label class="form-label fw-bold">Roll Number</label>
                  <input v-model="student.rollNumber" type="text" class="form-control" placeholder="e.g. CS20001" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Branch / Department</label>
                  <select v-model="student.branch" class="form-select">
                    <option value="">Select branch</option>
                    <option value="CSE">Computer Science & Engineering</option>
                    <option value="ECE">Electronics & Communication</option>
                    <option value="ME">Mechanical Engineering</option>
                    <option value="Civil">Civil Engineering</option>
                    <option value="EE">Electrical Engineering</option>
                    <option value="IT">Information Technology</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Graduation Year</label>
                  <input v-model="student.graduation" type="number" class="form-control"
                    placeholder="2025" :min="new Date().getFullYear()" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold">Phone Number</label>
                  <input v-model="student.phone" type="tel" class="form-control" placeholder="+91 98765 43210" />
                </div>
              </template>

              <!-- Recruiter fields -->
              <template v-if="role === 'company'">
                <div class="col-12">
                  <label class="form-label fw-bold">Company Name</label>
                  <input v-model="recruiter.companyName" type="text" class="form-control" placeholder="Tech Solutions Inc." required />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Department</label>
                  <input v-model="recruiter.department" type="text" class="form-control" placeholder="Human Resources" />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold">Designation</label>
                  <input v-model="recruiter.designation" type="text" class="form-control" placeholder="HR Manager" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold">Phone Number</label>
                  <input v-model="recruiter.phone" type="tel" class="form-control" placeholder="+91 98765 43210" required />
                </div>
              </template>

              <!-- Error -->
              <div v-if="error" class="col-12">
                <div class="alert alert-danger mb-0">
                  <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
                </div>
              </div>

              <div class="col-12">
                <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold" :disabled="loading">
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  {{ loading ? 'Creating account…' : 'Sign Up' }}
                </button>
              </div>

              <div class="col-12 text-center">
                <small class="text-muted">
                  Already have an account?
                  <router-link to="/login" class="text-primary fw-bold text-decoration-none">Login here</router-link>
                </small>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/utils/api'

export default {
  name: 'SignupPage',
  data: () => ({
    role: 'student',
    form:      { name: '', email: '', password: '', confirmPassword: '' },
    student:   { rollNumber: '', branch: '', graduation: '', phone: '' },
    recruiter: { companyName: '', department: '', designation: '', phone: '' },
    loading: false,
    error:   '',
  }),
  methods: {
    async submit() {
      this.error = ''
      if (this.form.password !== this.form.confirmPassword) {
        this.error = 'Passwords do not match'; return
      }
      if (this.form.password.length < 6) {
        this.error = 'Password must be at least 6 characters'; return
      }

      this.loading = true
      try {
        await api.post('/auth/register', {
          name:     this.form.name,
          email:    this.form.email,
          password: this.form.password,
          role:     this.role,
          ...(this.role === 'student'  ? { student:   this.student }   : {}),
          ...(this.role === 'company'  ? { recruiter: this.recruiter } : {}),
        })
        alert('Registration successful! Please login.')
        this.$router.push('/login')
      } catch (e) {
        this.error = e.message || 'Registration failed'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.signup-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}
.card        { border-radius: 12px; overflow: hidden; }
.card-header { background: linear-gradient(45deg, #0d6efd, #0dcaf0) !important; }
.form-control:focus, .form-select:focus {
  border-color: #0d6efd;
  box-shadow: 0 0 0 .2rem rgba(13,110,253,.25);
}
</style>