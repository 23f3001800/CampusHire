<template>
  <div class="login-page">
    <div class="container py-5" style="max-width:450px">
      <div class="card shadow-lg border-0">

        <div class="card-header text-white text-center py-4 border-0">
          <h2 class="mb-0"><i class="bi bi-briefcase-fill me-2"></i>CampusHire</h2>
          <p class="text-white-50 mb-0 mt-1">Launch Your Career Today</p>
        </div>

        <div class="card-body p-4">
          <form @submit.prevent="submit" novalidate>

            <div class="mb-3">
              <label class="form-label fw-bold">Email Address</label>
              <input v-model="email" type="email" class="form-control form-control-lg"
                placeholder="you@study.com" required />
            </div>

            <div class="mb-3">
              <label class="form-label fw-bold">Password</label>
              <input v-model="password" type="password" class="form-control form-control-lg"
                placeholder="••••••••" required />
            </div>

            <div v-if="error" class="alert alert-danger">
              <i class="bi bi-exclamation-circle me-2"></i>{{ error }}
            </div>

            <button type="submit" class="btn btn-primary btn-lg w-100 fw-bold" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              {{ loading ? 'Signing in…' : 'Sign In' }}
            </button>
          </form>

          <hr class="my-4 opacity-25" />

          <p class="text-center text-muted mb-0">
            Don't have an account?
            <router-link to="/signup" class="text-primary fw-bold text-decoration-none">Sign up here</router-link>
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useUserStore } from '@/stores/userStore'

export default {
  name: 'LoginPage',
  setup() {
    return { store: useUserStore() }
  },
  data:    () => ({ email: '', password: '', loading: false, error: '' }),
  created() {
    if (this.store.isAuthenticated) this._redirect()
  },
  methods: {
    async submit() {
      this.error   = ''
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
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
}
.card          { border-radius: 12px; overflow: hidden; }
.card-header   { background: linear-gradient(45deg, #0d6efd, #0dcaf0) !important; }
.form-control-lg:focus { border-color: #0d6efd; box-shadow: 0 0 0 .2rem rgba(13,110,253,.25); }
</style>