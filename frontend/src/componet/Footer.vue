<template>
  <footer class="bg-dark text-light mt-5 footer-custom">
    <div class="container py-5">
      <div class="row g-4">

        <!-- Company Info -->
        <div class="col-lg-3 col-md-6">
          <h5 class="fw-bold mb-3">
            <i class="bi bi-briefcase-fill me-2"></i>CampusHire
          </h5>
          <p class="small text-secondary">
            Connecting talented students with leading companies.
          </p>
        </div>

        <!-- Quick Links -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">Quick Links</h6>
          <ul class="list-unstyled footer-links">
            <li><router-link to="/">Home</router-link></li>
            <li><router-link to="/jobs">Browse Jobs</router-link></li>
            <li><router-link to="/about">About</router-link></li>
            <li><router-link to="/contact">Contact</router-link></li>
          </ul>
        </div>

        <!-- Students -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">For Students</h6>
          <ul class="list-unstyled footer-links">
            <li><a href="#">Create Profile</a></li>
            <li><a href="#">Career Resources</a></li>
            <li><a href="#">Interview Tips</a></li>
          </ul>
        </div>

        <!-- Contact + Subscribe -->
        <div class="col-lg-3 col-md-6">
          <h6 class="fw-bold mb-3">Stay Updated</h6>

          <div class="input-group input-group-sm mb-3">
            <input
              type="email"
              class="form-control bg-secondary border-0 text-light"
              placeholder="Your email"
            />
            <button class="btn btn-primary">
              <i class="bi bi-send"></i>
            </button>
          </div>

        </div>

      </div>

      <hr class="footer-hr" />

      <!-- Bottom Footer -->
      <div class="row align-items-center">
        <div class="col-md-6 small text-secondary">
          © {{ year }} CampusHire — Built with ❤️
        </div>

        <div class="col-md-6 text-md-end footer-bottom-links">
          <router-link to="/privacy">Privacy</router-link>
          <router-link to="/terms">Terms</router-link>
          <a href="#">Sitemap</a>
        </div>
      </div>

    </div>
  </footer>
</template>



<script>
export default {
  name: "Footer",
  computed: {
    year() {
      return new Date().getFullYear();
    }
  }
};
</script>


<style scoped>
.footer-custom {
  background: #121212;
}

.footer-links a,
.footer-bottom-links a {
  color: #cfcfcf;
  text-decoration: none;
  margin-right: 12px;
  transition: 0.25s;
}

.footer-links a:hover,
.footer-bottom-links a:hover {
  color: white;
}

.footer-hr {
  border-color: #2a2a2a;
  opacity: 1;
}

@media (max-width: 768px) {
  .footer-bottom-links {
    margin-top: 10px;
    text-align: left !important;
  }
}
</style>
