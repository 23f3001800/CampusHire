<template>
  <div>

    <!-- Role selector -->
    <div class="role-selector mb-4">
      <button type="button" class="role-btn" :class="{ active: role === 'student' }"
        @click="role = 'student'">
        <i class="bi bi-mortarboard d-block mb-1 fs-5"></i>
        <span class="small">Student</span>
      </button>
      <button type="button" class="role-btn" :class="{ active: role === 'company' }"
        @click="role = 'company'">
        <i class="bi bi-briefcase d-block mb-1 fs-5"></i>
        <span class="small">Recruiter</span>
      </button>
    </div>

    <form @submit.prevent="submit" novalidate>
      <div class="row g-3">

        <!-- Common fields -->
        <div class="col-12">
          <label class="form-label fw-semibold small">Full Name</label>
          <input v-model="form.name" type="text" class="form-control panel-input"
            placeholder="Jane Doe" required />
        </div>
        <div class="col-12">
          <label class="form-label fw-semibold small">Email Address</label>
          <input v-model="form.email" type="email" class="form-control panel-input"
            placeholder="you@example.com" required />
        </div>
        <div class="col-6">
          <label class="form-label fw-semibold small">Password</label>
          <input v-model="form.password" type="password" class="form-control panel-input"
            placeholder="Min 8 chars" required />
        </div>
        <div class="col-6">
          <label class="form-label fw-semibold small">Confirm</label>
          <input v-model="form.confirmPassword" type="password" class="form-control panel-input"
            placeholder="Repeat" required />
        </div>

        <!-- Student fields -->
        <template v-if="role === 'student'">
          <div class="col-12">
            <label class="form-label fw-semibold small">Roll Number</label>
            <input v-model="student.rollNumber" type="text" class="form-control panel-input"
              placeholder="e.g. CS20001" />
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Branch</label>
            <select v-model="student.branch" class="form-select panel-input">
              <option value="">Select</option>
              <option value="CSE">Computer Science</option>
              <option value="DS">Data Science</option>
              <option value="ECE">Electronics and Communication</option>
              <option value="ME">Mechanical</option>
              <option value="Civil">Civil Engineering</option>
              <option value="EE">Electrical Engineering</option>
              <option value="IT">Information Technology</option>
            </select>
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Grad Year</label>
            <input v-model="student.graduation" type="number" class="form-control panel-input"
              placeholder="2026" :min="new Date().getFullYear()" />
          </div>
          <div class="col-12">
            <label class="form-label fw-semibold small">Phone</label>
            <input v-model="student.phone" type="tel" class="form-control panel-input"
              placeholder="+91 98765 43210" />
          </div>
        </template>

        <!-- Recruiter fields -->
        <template v-if="role === 'company'">
          <div class="col-12">
            <label class="form-label fw-semibold small">Company Name</label>
            <input v-model="recruiter.companyName" type="text" class="form-control panel-input"
              placeholder="Tech Solutions Inc." required />
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Department</label>
            <input v-model="recruiter.department" type="text" class="form-control panel-input"
              placeholder="HR" />
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">web URL</label>
            <input v-model="recruiter.webUrl" type="text" class="form-control panel-input"
              placeholder="https://www.techsolutions.com" />
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Designation</label>
            <input v-model="recruiter.designation" type="text" class="form-control panel-input"
              placeholder="HR Manager" />
          </div>
          <div class="col-6">
            <label class="form-label fw-semibold small">Location</label>
            <input v-model="recruiter.location" type="text" class="form-control panel-input"
              placeholder="Hyderabad, India" />
          </div>
          <div class="col-12">
            <label class="form-label fw-semibold small">Phone</label>
            <input v-model="recruiter.phone" type="tel" class="form-control panel-input"
              placeholder="+91 98765 43210" required />
          </div>
        </template>

        <!-- Error -->
        <div v-if="error" class="col-12">
          <div class="alert alert-danger py-2 small mb-0">
            <i class="bi bi-exclamation-circle me-1"></i>{{ error }}
          </div>
        </div>

        <div class="col-12">
          <button type="submit" class="btn btn-primary w-100 fw-bold submit-btn" :disabled="loading">
            <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
            {{ loading ? 'Creating account…' : 'Create Account' }}
          </button>
        </div>

        <div class="col-12 text-center">
          <p class="text-muted small mb-0">
            Already have an account?
            <router-link to="/login" class="text-primary fw-bold text-decoration-none">
              Sign in here
            </router-link>
          </p>
        </div>

      </div>
    </form>
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
    recruiter: { companyName: '', department: '', designation: '', phone: '' , webUrl: '', location: '' },
    loading: false,
    error:   '',
  }),
  methods: {
    async submit() {
      this.error = ''
      if (this.form.password !== this.form.confirmPassword) {
        this.error = 'Passwords do not match'; return
      }
      if (this.form.password.length < 8) {
        this.error = 'Password must be at least 8 characters'; return
      }
      this.loading = true
      try {
        await api.post('/auth/register', {
          name:     this.form.name,
          email:    this.form.email,
          password: this.form.password,
          role:     this.role,
          ...(this.role === 'student' ? { student:   this.student }   : {}),
          ...(this.role === 'company' ? { recruiter: this.recruiter } : {}),
        })
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
.role-selector { display: flex; gap: 8px; }
.role-btn {
  flex: 1; background: #f8f9fa; border: 1.5px solid #dee2e6;
  border-radius: 10px; padding: .6rem .5rem; cursor: pointer;
  text-align: center; font-weight: 600; color: #495057;
  transition: all .2s;
}
.role-btn.active  { background: #e8f0fe; border-color: #0d6efd; color: #0d6efd; }
.role-btn:hover:not(.active) { background: #f1f3f5; }

.panel-input  { border-radius: 8px; border: 1.5px solid #dee2e6; font-size: .88rem; }
.panel-input:focus { border-color: #0d6efd; box-shadow: 0 0 0 3px rgba(13,110,253,.12); }

.submit-btn   { border-radius: 8px; padding: .6rem; font-size: .95rem; }
.submit-btn:hover:not(:disabled) { box-shadow: 0 4px 14px rgba(13,110,253,.35); }
</style>
