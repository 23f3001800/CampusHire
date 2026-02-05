<template>
  <div>
    <!-- Hero Section -->
    <div class="bg-primary bg-gradient text-white py-5">
      <div class="container">
        <div class="row align-items-center">
          <div class="col-lg-6">
            <h1 class="display-4 fw-bold mb-3">
              About CampusHire
            </h1>
            <p class="lead mb-4">
              CampusHire is your gateway to connecting students with top companies for internships and job placements. We bridge the gap between academic excellence and professional success.
            </p>
            <router-link to="/signup" class="btn btn-light btn-lg">
              Join Now
            </router-link>
          </div>
          <div class="col-lg-6 d-none d-lg-block text-center">
            <i
              class="bi bi-building-fill display-1 mb-3"
              style="font-size: 200px"
            ></i>
          </div>
        </div>
      </div>
    </div>

    <!-- Mission Section -->
    <div class="container py-5">
      <div class="row">
        <div class="col-lg-8 mx-auto text-center">
          <h2 class="mb-4">Our Mission</h2>
          <p class="lead">
            To empower students by providing seamless access to career opportunities and enable companies to discover talented individuals ready to contribute to their teams. We strive to create a transparent, efficient, and inclusive platform that supports the entire placement process.
          </p>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div class="bg-light py-5">
      <div class="container">
        <h2 class="text-center mb-5">What We Offer</h2>
        <div class="row g-4">
          <div class="col-md-4">
            <div class="card h-100 border-0 shadow-sm">
              <div class="card-body text-center p-4">
                <div class="display-5 mb-3 text-primary">
                  <i class="bi bi-mortarboard-fill"></i>
                </div>
                <h5 class="card-title">For Students</h5>
                <p class="card-text text-muted">
                  Explore job opportunities, apply to drives, track applications, and build your career profile with ease.
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
                <h5 class="card-title">For Companies</h5>
                <p class="card-text text-muted">
                  Post job drives, review applications, manage placements, and connect with talented students from top institutions.
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
                <h5 class="card-title">For Admins</h5>
                <p class="card-text text-muted">
                  Oversee the platform, manage users, monitor activities, and ensure a smooth placement process for all.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="container py-5">
      <h2 class="text-center mb-5">How It Works</h2>
      <div class="row g-4">
        <div class="col-md-4">
          <div class="text-center">
            <div class="display-4 mb-3 text-primary">1</div>
            <h5>Register & Profile</h5>
            <p class="text-muted">
              Students and companies create profiles, admins manage the system.
            </p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="text-center">
            <div class="display-4 mb-3 text-primary">2</div>
            <h5>Connect & Apply</h5>
            <p class="text-muted">
              Companies post drives, students apply, and admins oversee the process.
            </p>
          </div>
        </div>
        <div class="col-md-4">
          <div class="text-center">
            <div class="display-4 mb-3 text-primary">3</div>
            <h5>Get Placed</h5>
            <p class="text-muted">
              Successful matches lead to internships and job offers.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Contact Section -->
    <div class="bg-primary bg-gradient text-white py-5">
      <div class="container text-center">
        <h2 class="mb-4">Get In Touch</h2>
        <p class="lead mb-4">
          Have questions? We're here to help.
        </p>
        <p>
          Email: support@campushire.com<br>
          Phone: +1 (123) 456-7890
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "AboutPage",
};
</script>

<style scoped>
.bg-primary {
  background: linear-gradient(45deg, #0d6efd, #0dcaf0) !important;
}

.card {
  transition: transform 0.2s ease;
}

.card:hover {
  transform: translateY(-5px);
}

.display-4 {
  font-size: 3rem;
  font-weight: bold;
}
</style>
