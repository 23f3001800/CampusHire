<template>
  <footer class="bg-dark text-light mt-5">
    <!-- Main Footer Content -->
    <div class="container py-5">
      <div class="row g-4">
        <!-- Company Info -->
        <div class="col-lg-3 col-md-6">
          <h5 class="fw-bold mb-3">
            <i class="bi bi-briefcase-fill me-2"></i>CampusHire
          </h5>
          <p class="text-muted small mb-3">
            Connecting talented students with leading companies for career opportunities.
          </p>
          <div class="d-flex gap-3">
            <a href="#" class="text-muted text-decoration-none hover-link">
              <i class="bi bi-facebook"></i>
            </a>
            <a href="#" class="text-muted text-decoration-none hover-link">
              <i class="bi bi-twitter"></i>
            </a>
            <a href="#" class="text-muted text-decoration-none hover-link">
              <i class="bi bi-linkedin"></i>
            </a>
            <a href="#" class="text-muted text-decoration-none hover-link">
              <i class="bi bi-instagram"></i>
            </a>
          </div>
        </div>

        <!-- Quick Links -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">Quick Links</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <router-link to="/" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Home
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/products" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Browse Jobs
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/about" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>About Us
              </router-link>
            </li>
            <li class="mb-2">
              <router-link to="/contact" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Contact
              </router-link>
            </li>
          </ul>
        </div>

        <!-- For Students -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">For Students</h6>
          <ul class="list-unstyled">
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Create Profile
              </a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Career Resources
              </a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Interview Tips
              </a>
            </li>
            <li class="mb-2">
              <a href="#" class="text-muted text-decoration-none hover-link small">
                <i class="bi bi-chevron-right me-1"></i>Internships
              </a>
            </li>
          </ul>
        </div>

        <!-- Newsletter -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">Stay Updated</h6>
          <p class="text-muted small mb-3">
            Subscribe to get the latest job opportunities and career tips.
          </p>
          <div class="input-group input-group-sm">
            <input
              type="email"
              class="form-control bg-secondary border-0 text-light"
              placeholder="Your email"
              aria-label="Email"
            />
            <button class="btn btn-primary" type="button">
              <i class="bi bi-send"></i>
            </button>
          </div>
        </div>
      </div>

      <hr class="bg-secondary my-4" />

      <!-- Bottom Footer -->
      <div class="row align-items-center">
        <div class="col-md-6">
          <p class="text-muted small mb-0">
            &copy; {{ year }} CampusHire — Built with <i class="bi bi-heart-fill text-danger"></i> by AppDev Team
          </p>
        </div>
        <div class="col-md-6 text-md-end">
          <div class="d-flex gap-3 justify-content-md-end flex-wrap">
            <router-link to="/privacy" class="text-muted small text-decoration-none hover-link">
              Privacy Policy
            </router-link>
            <span class="text-muted">•</span>
            <router-link to="/terms" class="text-muted small text-decoration-none hover-link">
              Terms of Service
            </router-link>
            <span class="text-muted">•</span>
            <a href="#" class="text-muted small text-decoration-none hover-link">
              Sitemap
            </a>
          </div>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
export default {
  name: "Footer",
  data() {
    return {
      year: 2025,
    };
  },
};
</script>

<style scoped>
footer {
  margin-top: auto;
}

.hover-link {
  transition: color 0.3s ease, transform 0.3s ease;
}

.hover-link:hover {
  color: #0d6efd !important;
  transform: translateX(5px);
}

.input-group-sm .form-control {
  font-size: 0.875rem;
}

.input-group-sm .form-control::placeholder {
  color: #adb5bd;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
  padding: 0.375rem 0.75rem;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0b5ed7;
}

hr {
  opacity: 0.1;
}

@media (max-width: 768px) {
  .col-md-6:last-child {
    margin-top: 1rem;
    text-align: left !important;
  }
}
</style>