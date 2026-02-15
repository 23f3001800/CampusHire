<template>
  <div>
    <!-- Hero -->
    <section class="hero d-flex align-items-center">
      <div class="container text-center text-white py-5">
        <h1 class="display-4 fw-bold mb-3">Find Your Dream Career</h1>
        <p class="lead mb-4 opacity-90">
          CampusHire connects talented students with top companies through seamless placement drives.
        </p>
        <div class="d-flex justify-content-center gap-3 flex-wrap">
          <router-link to="/signup" class="btn btn-light btn-lg px-5 fw-bold text-primary">
            Get Started Free
          </router-link>
          <router-link to="/login" class="btn btn-outline-light btn-lg px-5">
            Sign In
          </router-link>
        </div>
      </div>
    </section>

    <!-- Stats -->
    <section class="bg-white py-5 border-bottom">
      <div class="container">
        <div class="row text-center g-4">
          <div class="col-6 col-md-3" v-for="s in stats" :key="s.label">
            <div class="h2 fw-bold text-primary mb-1">{{ s.value }}</div>
            <div class="text-muted small">{{ s.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Features -->
    <section class="py-5 bg-light">
      <div class="container">
        <h2 class="text-center fw-bold mb-5">Everything You Need</h2>
        <div class="row g-4">
          <div class="col-md-4" v-for="f in features" :key="f.title">
            <div class="card h-100 border-0 shadow-sm text-center p-4">
              <div class="feature-icon mb-3" :class="f.bg">
                <i :class="`bi ${f.icon} fs-3 text-white`"></i>
              </div>
              <h5 class="fw-bold">{{ f.title }}</h5>
              <p class="text-muted mb-0">{{ f.desc }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA -->
    <section class="py-5 bg-primary text-white text-center">
      <div class="container">
        <h2 class="fw-bold mb-3">Ready to Launch Your Career?</h2>
        <p class="lead mb-4 opacity-90">Join thousands of students already placed through CampusHire.</p>
        <router-link to="/signup" class="btn btn-light btn-lg px-5 fw-bold text-primary">
          Create Free Account
        </router-link>
      </div>
    </section>
  </div>
</template>

<script>
export default {
  name: 'HomePage',
  data: () => ({
    stats: [
      { value: '10,000+', label: 'Students Placed' },
      { value: '500+',    label: 'Partner Companies' },
      { value: '2,000+',  label: 'Drives Conducted' },
      { value: '95%',     label: 'Placement Rate' },
    ],
    features: [
      { icon: 'bi-mortarboard', bg: 'bg-primary', title: 'For Students', desc: 'Browse eligible drives, track applications, and get placed at your dream company.' },
      { icon: 'bi-building',    bg: 'bg-success',  title: 'For Companies', desc: 'Post placement drives, manage applicants, and find the best campus talent.' },
      { icon: 'bi-shield-check', bg: 'bg-info',   title: 'Verified & Secure', desc: 'All companies are verified by our admin team before accessing student profiles.' },
    ],
  }),
}
</script>

<style scoped>
.hero {
  min-height: 75vh;
  background: linear-gradient(135deg, #0d6efd 0%, #0dcaf0 100%);
}
.feature-icon {
  width: 64px; height: 64px; border-radius: 16px;
  display: flex; align-items: center; justify-content: center; margin: 0 auto;
}
</style>