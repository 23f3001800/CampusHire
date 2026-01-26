<template>
  <div>
    <!-- Hero Section -->
    <div class="bg-primary bg-gradient text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-3">
              Launch Your Career Today
            </h1>
            <p class="lead mb-4">
              Connect with top employers, explore exciting job opportunities,
              and take the next step in your professional journey.
            </p>
            <router-link to="/login" class="btn btn-light btn-lg">
              Regiter Today
            </router-link>
          </div>
          <div class="col-lg-6 d-none d-lg-block text-center">
            <i
              class="bi bi-briefcase-fill display-1 mb-3"
              style="font-size: 200px"
            ></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="container py-5">
      <div class="row g-4">
        <div class="col-md-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center p-4">
              <div class="display-5 mb-3 text-primary">
                <i class="bi bi-graph-up-arrow"></i>
              </div>
              <h5 class="card-title">Career Growth</h5>
              <p class="card-text text-muted">
                Access mentorship and training programs to accelerate your professional development
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center p-4">
              <div class="display-5 mb-3 text-primary">
                <i class="bi bi-building"></i>
              </div>
              <h5 class="card-title">Top Companies</h5>
              <p class="card-text text-muted">
                Connect with leading companies hiring talented professionals across industries
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card h-100 border-0 shadow-sm">
            <div class="card-body text-center p-4">
              <div class="display-5 mb-3 text-primary">
                <i class="bi bi-shield-check"></i>
              </div>
              <h5 class="card-title">Trusted Platform</h5>
              <p class="card-text text-muted">
                Secure and verified job listings from reputable employers
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Categories Section -->
    <div class="bg-light py-5">
      <div class="container">
        <h2 class="text-center mb-4">Job Categories</h2>
        <div class="row g-4">
          <div
            v-for="category in categories"
            :key="category.name"
            class="col-6 col-md-3"
          >
            <router-link
              :to="{ path: '/products', query: { category: category.name } }"
              class="text-decoration-none"
            >
              <div class="card h-100 border-0 shadow-sm hover-lift">
                <div class="card-body text-center p-4">
                  <i
                    :class="category.icon + ' display-6 mb-3 text-primary'"
                  ></i>
                  <h6 class="card-title text-dark">{{ category.name }}</h6>
                </div>
              </div>
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "HomePage",
  data() {
    return {
      categories: [
        { name: "IT & Software", icon: "bi bi-laptop" },
        { name: "Finance & Banking", icon: "bi bi-cash-coin" },
        { name: "Human Resources", icon: "bi bi-people-fill" },
        { name: "Marketing", icon: "bi bi-megaphone" },
        { name: "Engineering", icon: "bi bi-gear" },
        { name: "Sales", icon: "bi bi-graph-up" },
        { name: "Operations", icon: "bi bi-diagram-3" },
        { name: "Management", icon: "bi bi-suit-heart-fill" },
      ],
    };
  },
};
</script>

<style scoped>


.hover-lift {
  transition: transform 0.2s ease;
}
.hover-lift:hover {
  transform: translateY(-5px);
}
.bg-primary {
  background: linear-gradient(45deg, #0d6efd, #0dcaf0) !important;
}
.bi-briefcase-fill {
  opacity: 0.9;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.1);
}
</style>