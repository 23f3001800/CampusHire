<template>
  <form @submit.prevent="submit" novalidate>

    <div class="mb-3">
      <label class="form-label fw-semibold small">Email Address</label>
      <div class="input-wrap">
        <i class="bi bi-envelope input-icon"></i>
        <input v-model="email" type="email" class="form-control panel-input"
          placeholder="you@study.com" required />
      </div>
    </div>

    <div class="mb-3">
      <div class="d-flex justify-content-between align-items-center">
        <label class="form-label fw-semibold small mb-0">Password</label>
        <a href="#" class="small text-primary text-decoration-none">Forgot password?</a>
      </div>
      <div class="input-wrap mt-1">
        <i class="bi bi-lock input-icon"></i>
        <input v-model="password" :type="showPass ? 'text' : 'password'"
          class="form-control panel-input" placeholder="••••••••" required />
        <button type="button" class="input-eye" @click="showPass = !showPass">
          <i :class="`bi bi-eye${showPass ? '-slash' : ''}`"></i>
        </button>
      </div>
    </div>

    <div v-if="error" class="alert alert-danger py-2 small mb-3">
      <i class="bi bi-exclamation-circle me-1"></i>{{ error }}
    </div>

    <button type="submit" class="btn btn-primary w-100 fw-bold submit-btn" :disabled="loading">
      <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
      {{ loading ? 'Signing in…' : 'Sign In' }}
    </button>

    <p class="text-center text-muted small mt-3 mb-0">
      Don't have an account?
      <router-link to="/signup" class="text-primary fw-bold text-decoration-none">
        Sign up here
      </router-link>
    </p>

  </form>
</template>

<script>
import { useUserStore } from '@/stores/userStore'

export default {
  name: 'LoginPage',
  setup() { return { store: useUserStore() } },
  data: () => ({ email: '', password: '', loading: false, error: '', showPass: false }),
  created() {
    if (this.store.isAuthenticated) this._redirect()
  },
  methods: {
    async submit() {
      this.error = ''
      this.loading = true
      try {
        await this.store.loginWithCredentials('/auth/login', {
          email: this.email, password: this.password,
        })
        this._redirect()
      } catch (e) {
        this.error = e.message || 'Login failed'
      } finally {
        this.loading = false
      }
    },
    _redirect() {
      const dest = this.$route.query.redirect || `/${this.store.role}/${this.store.id}`
      this.$router.push(dest)
    },
  },
}
</script>

<style scoped>
.input-wrap    { position: relative; }
.input-icon    { position: absolute; left: .75rem; top: 50%; transform: translateY(-50%); color: #adb5bd; pointer-events: none; }
.input-eye     { position: absolute; right: .75rem; top: 50%; transform: translateY(-50%); background: none; border: none; color: #adb5bd; cursor: pointer; padding: 0; }
.panel-input   { padding-left: 2.25rem; border-radius: 8px; border: 1.5px solid #dee2e6; font-size: .9rem; }
.panel-input:focus { border-color: #0d6efd; box-shadow: 0 0 0 3px rgba(13,110,253,.12); }
.submit-btn    { border-radius: 8px; padding: .6rem; font-size: .95rem; }
.submit-btn:hover:not(:disabled) { box-shadow: 0 4px 14px rgba(13,110,253,.35); }
</style>
