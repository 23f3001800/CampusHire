<template>
  <footer class="footer-custom text-light mt-auto">
    <div class="container py-4">
      <div class="row align-items-center g-3">

        <!-- Brand + tagline -->
        <div class="col-md-4">
          <div class="fw-bold fs-5 mb-1">
            <i class="bi bi-briefcase-fill me-2 text-primary"></i>CampusHire
          </div>
          <p class="text-secondary small mb-0">
            Connecting students with leading companies.
          </p>
        </div>

        <!-- Subscribe -->
        <div class="col-md-4">
          <div class="input-group input-group-sm">
            <input
              v-model="email"
              type="email"
              class="form-control bg-secondary border-0 text-light"
              placeholder="Stay updated — enter email"
            />
            <button @click="subscribe" class="btn btn-primary px-3">
              <i class="bi bi-send-fill"></i>
            </button>
          </div>
          <div v-if="subscribed" class="text-success small mt-1">
            <i class="bi bi-check-circle me-1"></i>You're subscribed!
          </div>
        </div>

        <!-- Social icons -->
        <div class="col-md-4 text-md-end">
          <a href="#" class="social-icon" aria-label="Twitter">
            <i class="bi bi-twitter-x"></i>
          </a>
          <a href="#" class="social-icon" aria-label="LinkedIn">
            <i class="bi bi-linkedin"></i>
          </a>
          <a href="#" class="social-icon" aria-label="GitHub">
            <i class="bi bi-github"></i>
          </a>
        </div>

      </div>

      <hr class="footer-hr my-3" />

      <div class="d-flex flex-wrap justify-content-between align-items-center gap-2">
        <span class="small text-secondary">
          © {{ year }} CampusHire — Built with ❤️
        </span>
        <div class="d-flex gap-3">
          <a href="#" class="footer-link">Privacy</a>
          <a href="#" class="footer-link">Terms</a>
          <a href="#" class="footer-link">Contact</a>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: 'Footer',
  data: () => ({ email: '', subscribed: false }),
  computed: {
    year() { return new Date().getFullYear() }
  },
  methods: {
    subscribe() {
      if (this.email) {
        this.subscribed = true
        this.email = ''
        setTimeout(() => (this.subscribed = false), 3000)
      }
    }
  }
}
</script>

<style scoped>
.footer-custom {
  background: #0f0f0f;
  border-top: 1px solid #1e1e1e;
}

.footer-hr { border-color: #2a2a2a; opacity: 1; }

.footer-link {
  color: #9a9a9a;
  text-decoration: none;
  font-size: .85rem;
  transition: color .2s;
}
.footer-link:hover { color: #fff; }

.social-icon {
  color: #9a9a9a;
  font-size: 1.1rem;
  margin-left: 16px;
  text-decoration: none;
  transition: color .2s, transform .2s;
  display: inline-block;
}
.social-icon:hover { color: #0d6efd; transform: translateY(-2px); }
</style>
