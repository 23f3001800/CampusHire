<template>
  <div class="home-wrapper">

    <!-- ═══ HOME CONTENT — always fully visible, never dimmed ═══ -->
    <div class="home-content">

      <!-- Hero -->
      <div class="hero-section text-white">
        <div class="container py-5">
          <div class="row align-items-center">
            <div class="col-lg-6">
              <span class="hero-badge mb-3 d-inline-block">
                <i class="bi bi-patch-check-fill me-1"></i> Trusted by 10,000+ students
              </span>
              <h1 class="fw-bold mb-3 hero-heading">
                Launch Your Career Today
              </h1>
              <p class="mb-4 hero-sub">
                Connect with top employers, explore exciting opportunities,
                and take the next step in your professional journey.
              </p>
              <div class="d-flex gap-2 flex-wrap">
                <router-link to="/signup" class="btn btn-light fw-semibold px-4">
                  Register Today
                </router-link>
                <router-link to="/login" class="btn btn-outline-light px-4">
                  Sign In
                </router-link>
              </div>
            </div>
            <div class="col-lg-6 d-none d-lg-flex justify-content-center">
              <div class="hero-icon-wrap">
                <i class="bi bi-briefcase-fill hero-icon"></i>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Features -->
      <div class="container py-4">
        <div class="row g-3">
          <div class="col-md-4" v-for="f in features" :key="f.title">
            <div class="feature-card d-flex align-items-start gap-3 p-3">
              <div class="feature-icon-wrap" :class="f.bg">
                <i :class="`bi ${f.icon}`"></i>
              </div>
              <div>
                <h6 class="fw-bold mb-1">{{ f.title }}</h6>
                <p class="text-muted small mb-0">{{ f.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Categories -->
      <div class="bg-light py-4">
        <div class="container">
          <h6 class="fw-bold text-center text-muted text-uppercase mb-3 cat-label">
            Browse by Category
          </h6>
          <div class="row g-2">
            <div class="col-6 col-md-3" v-for="cat in categories" :key="cat.name">
              <router-link
                :to="{ path: '/products', query: { category: cat.name } }"
                class="text-decoration-none">
                <div class="cat-card d-flex align-items-center gap-2 p-2 px-3">
                  <i :class="`bi ${cat.icon} text-primary`"></i>
                  <span class="small fw-semibold text-dark">{{ cat.name }}</span>
                </div>
              </router-link>
            </div>
          </div>
        </div>
      </div>

    </div>
    <!-- ═══ END HOME CONTENT ═══ -->


    <!-- ═══ BACKDROP — very subtle so home stays visible ═══ -->
    <transition name="fade-backdrop">
      <div v-if="isPanelOpen" class="auth-backdrop" @click="close"></div>
    </transition>


    <!-- ═══ SIDE PANEL — half page wide ═══ -->
    <transition name="slide-panel">
      <div v-if="isPanelOpen" class="auth-panel">

        <!-- Panel inner scroll container -->
        <div class="panel-inner">

          <!-- Close -->
          <button class="panel-close" @click="close" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>

          <!-- Brand -->
          <div class="mb-4 pt-2">
            <div class="fw-bold fs-5">
              <i class="bi bi-briefcase-fill me-2 text-primary"></i>CampusHire
            </div>
            <p class="text-muted small mb-0 mt-1">
              {{ isLogin ? 'Welcome back! Sign in to continue.' : 'Create your free account today.' }}
            </p>
          </div>

          <!-- Tabs -->
          <div class="panel-tabs mb-4">
            <router-link to="/login"  class="panel-tab" active-class="active">
              <i class="bi bi-box-arrow-in-right me-1"></i>Sign In
            </router-link>
            <router-link to="/signup" class="panel-tab" active-class="active">
              <i class="bi bi-person-plus me-1"></i>Sign Up
            </router-link>
          </div>

          <!-- Login / Signup form renders here -->
          <transition name="form-switch" mode="out-in">
            <router-view />
          </transition>

        </div>
      </div>
    </transition>

  </div>
</template>

<script>
export default {
  name: 'HomeView',

  computed: {
    isPanelOpen() {
      return ['/login', '/signup'].includes(this.$route.path)
    },
    isLogin() {
      return this.$route.path === '/login'
    },
  },

  watch: {
    isPanelOpen(val) {
      // Only lock scroll on mobile (panel is overlay); on desktop home stays scrollable
      if (window.innerWidth < 768) {
        document.body.style.overflow = val ? 'hidden' : ''
      }
    },
  },

  beforeUnmount() {
    document.body.style.overflow = ''
  },

  methods: {
    close() {
      this.$router.push('/')
    },
  },

  data: () => ({
    features: [
      { icon: 'bi-graph-up-arrow', bg: 'bg-primary-soft', title: 'Career Growth',
        desc: 'Mentorship and training programs to accelerate your development.' },
      { icon: 'bi-building',       bg: 'bg-success-soft', title: 'Top Companies',
        desc: 'Leading companies hiring talented professionals across industries.' },
      { icon: 'bi-shield-check',   bg: 'bg-info-soft',    title: 'Trusted Platform',
        desc: 'Secure and verified listings from reputable employers.' },
    ],
    categories: [
      { name: 'IT & Software',     icon: 'bi-laptop' },
      { name: 'Finance & Banking', icon: 'bi-cash-coin' },
      { name: 'Human Resources',   icon: 'bi-people-fill' },
      { name: 'Marketing',         icon: 'bi-megaphone' },
      { name: 'Engineering',       icon: 'bi-gear' },
      { name: 'Sales',             icon: 'bi-graph-up' },
      { name: 'Operations',        icon: 'bi-diagram-3' },
      { name: 'Management',        icon: 'bi-suit-heart-fill' },
    ],
  }),
}
</script>

<style scoped>
/* ── Layout ── */
.home-wrapper  { position: relative; }
.home-content  { /* NO blur, NO scale, NO dim — always crystal clear */ }

/* ── Hero ── */
.hero-section {
  background: linear-gradient(135deg, #da1cef 0%, #6610f2 100%);
}
.hero-badge {
  background: rgba(255,255,255,.15);
  border: 1px solid rgba(255,255,255,.25);
  border-radius: 50px;
  padding: .25rem .9rem;
  font-size: .8rem; font-weight: 600;
}
.hero-heading { font-size: clamp(1.75rem, 4vw, 2.5rem); line-height: 1.2; }
.hero-sub     { font-size: .97rem; opacity: .88; max-width: 420px; }
.hero-icon-wrap {
  width: 160px; height: 160px;
  background: rgba(255,255,255,.1);
  border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
}
.hero-icon { font-size: 4.5rem; opacity: .9; }

/* ── Features ── */
.feature-card {
  background: #fff; border-radius: 12px; border: 1px solid #f0f0f0;
  transition: box-shadow .2s, transform .2s;
}
.feature-card:hover { box-shadow: 0 6px 20px rgba(0,0,0,.07); transform: translateY(-2px); }
.feature-icon-wrap {
  width: 40px; height: 40px; border-radius: 10px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; font-size: 1.1rem;
}
.bg-primary-soft { background: #e8f0fe; color: #0ce61e; }
.bg-success-soft { background: #e6f4ea; color: #198754; }
.bg-info-soft    { background: #e0f7fa; color: #0097a7; }

/* ── Categories ── */
.cat-label { letter-spacing: .08em; font-size: .75rem; }
.cat-card {
  background: #fff; border: 1px solid #ebebeb; border-radius: 10px;
  transition: background .2s, border-color .2s, transform .2s;
}
.cat-card:hover { background: #f0f4ff; border-color: #c5d8ff; transform: translateY(-2px); }


/* ══════════════════════════════════
   BACKDROP — barely visible so
   home page shows through clearly
══════════════════════════════════ */
.auth-backdrop {
  position: fixed;
  inset: 0;
  z-index: 1040;
  /* Very light dark tint — home fully readable underneath */
  background: rgba(0, 0, 0, 0.18);
  backdrop-filter: none; /* NO blur — home stays sharp */
}


/* ══════════════════════════════════
   PANEL — covers exactly half page
══════════════════════════════════ */
.auth-panel {
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 50%;          /* half the viewport */
  z-index: 1050;
  background: #ffffff;
  box-shadow: -12px 0 48px rgba(0, 0, 0, 0.14);
  overflow: hidden;    /* inner div handles scroll */
  display: flex;
  flex-direction: column;
}

.panel-inner {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 2.5rem;
  position: relative;
}

/* Close button */
.panel-close {
  position: absolute; top: 1.25rem; right: 1.25rem;
  background: #f1f3f5; border: none; border-radius: 50%;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: .9rem; cursor: pointer; color: #555;
  transition: background .2s, color .2s, transform .2s;
  z-index: 1;
}
.panel-close:hover {
  background: #e2e6ea;
  color: #111;
  transform: rotate(90deg);
}

/* Tabs */
.panel-tabs {
  display: flex;
  background: #f1f3f5;
  border-radius: 12px;
  padding: 4px;
  gap: 3px;
}
.panel-tab {
  flex: 1; padding: .5rem .75rem; text-align: center;
  font-size: .88rem; font-weight: 600; color: #6c757d;
  border-radius: 9px; text-decoration: none;
  transition: all .22s ease;
}
.panel-tab.active {
  background: #fff;
  color: hsl(221, 91%, 48%);
  box-shadow: 0 2px 10px rgba(0,0,0,.09);
}
.panel-tab:hover:not(.active) { color: #343a40; }


/* ══════════════════════════════════
   TRANSITIONS
══════════════════════════════════ */

/* Panel: slides in from the right edge */
.slide-panel-enter-active {
  transition: transform .4s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-panel-leave-active {
  transition: transform .3s cubic-bezier(0.4, 0, 1, 1);
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(100%);
}

/* Backdrop fade */
.fade-backdrop-enter-active { transition: opacity .35s ease; }
.fade-backdrop-leave-active { transition: opacity .25s ease; }
.fade-backdrop-enter-from,
.fade-backdrop-leave-to     { opacity: 0; }

/* Form switch between login ↔ signup */
.form-switch-enter-active { transition: opacity .18s ease, transform .18s ease; }
.form-switch-leave-active { transition: opacity .14s ease, transform .14s ease; }
.form-switch-enter-from   { opacity: 0; transform: translateX(18px); }
.form-switch-leave-to     { opacity: 0; transform: translateX(-18px); }


/* ══════════════════════════════════
   RESPONSIVE
══════════════════════════════════ */
@media (max-width: 768px) {
  .auth-panel {
    width: 100vw;  /* full screen on mobile */
  }
  .panel-inner {
    padding: 1.5rem 1.25rem;
  }
}

@media (min-width: 769px) and (max-width: 1024px) {
  .auth-panel {
    width: 60%;  /* slightly wider on tablets */
  }
}
</style>
