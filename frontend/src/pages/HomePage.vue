<template>
  <div class="home-wrapper">

    <!-- ═══ HOME CONTENT ═══ -->
    <div class="home-content">

      <!-- ── Hero ── -->
      <section class="hero-section">
        <div class="hero-grid-overlay"></div>
        <div class="container py-5 position-relative">
          <div class="row align-items-center g-5">
            <div class="col-lg-6">
              <span class="hero-pill mb-3 d-inline-flex align-items-center gap-2">
                <span class="pill-dot"></span>
                Trusted by 10,000+ students across India
              </span>
              <h1 class="hero-heading fw-black mb-3">
                Your Career<br>
                <span class="gradient-text">Starts Here.</span>
              </h1>
              <p class="hero-sub mb-4">
                Connect with top recruiters, track your applications, and land
                your dream placement — all from one platform built for campus hiring.
              </p>
              <div class="d-flex gap-3 flex-wrap">
                <router-link to="/signup" class="btn btn-hero-primary px-4">
                  Get Started Free
                  <i class="bi bi-arrow-right ms-2"></i>
                </router-link>
                <router-link to="/login" class="btn btn-hero-ghost px-4">
                  Sign In
                </router-link>
              </div>

              <!-- Quick stats -->
              <div class="hero-stats mt-5 d-flex gap-4 flex-wrap">
                <div v-for="s in heroStats" :key="s.label" class="stat-item">
                  <div class="stat-num">{{ s.num }}</div>
                  <div class="stat-label">{{ s.label }}</div>
                </div>
              </div>
            </div>

            <div class="col-lg-6 d-none d-lg-block">
              <div class="hero-card-stack">
                <!-- Floating cards -->
                <div class="float-card float-card-1 shadow-lg">
                  <div class="d-flex align-items-center gap-2 mb-2">
                    <div class="fc-avatar bg-success text-white">
                      <i class="bi bi-check-lg"></i>
                    </div>
                    <div>
                      <div class="small fw-bold">Offer Received!</div>
                      <div class="text-muted" style="font-size:.72rem">Google SWE · ₹24 LPA</div>
                    </div>
                  </div>
                  <div class="fc-bar">
                    <div class="fc-bar-fill" style="width:82%"></div>
                  </div>
                </div>

                <div class="float-card float-card-2 shadow-lg">
                  <div class="small text-muted mb-1">Applications This Month</div>
                  <div class="d-flex gap-1 align-items-end">
                    <div v-for="(h, i) in [40,65,55,80,70,90,85]" :key="i"
                         class="mini-bar" :style="`height:${h}%;`"></div>
                  </div>
                </div>

                <div class="float-card float-card-3 shadow-lg">
                  <div class="d-flex gap-2 align-items-center">
                    <i class="bi bi-buildings-fill text-primary fs-4"></i>
                    <div>
                      <div class="small fw-bold">248 companies</div>
                      <div class="text-muted" style="font-size:.72rem">actively hiring</div>
                    </div>
                  </div>
                </div>

                <div class="hero-central-icon">
                  <i class="bi bi-briefcase-fill"></i>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Live Stats Banner ── -->
      <section class="stats-banner">
        <div class="container">
          <div class="row g-0 stats-row">
            <div class="col-6 col-md-3" v-for="s in platformStats" :key="s.label">
              <div class="stats-cell">
                <i :class="`bi ${s.icon} stats-icon`" :style="`color:${s.color}`"></i>
                <div class="stats-num">{{ s.value }}</div>
                <div class="stats-lbl">{{ s.label }}</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Public Dashboard Charts ── -->
      <section class="py-5 bg-light">
        <div class="container">
          <div class="section-header text-center mb-5">
            <span class="section-tag">Live Analytics</span>
            <h2 class="section-title fw-bold mt-2">Placement Insights</h2>
            <p class="text-muted small">
              Aggregated monthly statistics — updated every 30 days
            </p>
          </div>

          <div class="row g-4">
            <!-- Placement Trend -->
            <div class="col-lg-7">
              <div class="chart-card h-100">
                <div class="chart-card-header">
                  <div>
                    <h6 class="fw-bold mb-0">Placement Trend</h6>
                    <small class="text-muted">Monthly offers — last 6 months</small>
                  </div>
                  <span class="badge bg-success bg-opacity-10 text-success">↑ 18% MoM</span>
                </div>
                <div class="chart-body">
                  <canvas ref="trendChart" height="200"></canvas>
                </div>
              </div>
            </div>

            <!-- Skills In Demand -->
            <div class="col-lg-5">
              <div class="chart-card h-100">
                <div class="chart-card-header">
                  <div>
                    <h6 class="fw-bold mb-0">Top Skills in Demand</h6>
                    <small class="text-muted">By drive requirements</small>
                  </div>
                </div>
                <div class="chart-body">
                  <canvas ref="skillsChart" height="200"></canvas>
                </div>
              </div>
            </div>

            <!-- Application Funnel -->
            <div class="col-lg-5">
              <div class="chart-card">
                <div class="chart-card-header">
                  <div>
                    <h6 class="fw-bold mb-0">Application Funnel</h6>
                    <small class="text-muted">This semester</small>
                  </div>
                </div>
                <div class="funnel-body">
                  <div v-for="f in funnel" :key="f.label" class="funnel-row">
                    <div class="funnel-label">{{ f.label }}</div>
                    <div class="funnel-bar-wrap">
                      <div class="funnel-bar"
                           :style="`width:${f.pct}%;background:${f.color}`"></div>
                    </div>
                    <div class="funnel-val">{{ f.value }}</div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Package Distribution -->
            <div class="col-lg-7">
              <div class="chart-card">
                <div class="chart-card-header">
                  <div>
                    <h6 class="fw-bold mb-0">Package Distribution</h6>
                    <small class="text-muted">Offer breakdown by salary range</small>
                  </div>
                  <span class="badge bg-primary bg-opacity-10 text-primary">Avg ₹12.4 LPA</span>
                </div>
                <div class="chart-body">
                  <canvas ref="packageChart" height="160"></canvas>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Features ── -->
      <section class="py-5 bg-white">
        <div class="container">
          <div class="section-header text-center mb-5">
            <span class="section-tag">Why CampusHire</span>
            <h2 class="section-title fw-bold mt-2">Everything You Need</h2>
          </div>
          <div class="row g-4">
            <div class="col-md-4" v-for="f in features" :key="f.title">
              <div class="feature-card">
                <div class="feature-icon-wrap" :class="f.color">
                  <i :class="`bi ${f.icon} fs-4`"></i>
                </div>
                <h6 class="fw-bold mt-3 mb-2">{{ f.title }}</h6>
                <p class="text-muted small mb-0">{{ f.desc }}</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Categories ── -->
      <section class="py-5 bg-light">
        <div class="container">
          <div class="section-header text-center mb-4">
            <span class="section-tag">Explore</span>
            <h2 class="section-title fw-bold mt-2">Browse by Industry</h2>
          </div>
          <div class="row g-2">
            <div class="col-6 col-md-3" v-for="cat in categories" :key="cat.name">
              <div class="cat-card">
                <div class="cat-icon-wrap">
                  <i :class="`bi ${cat.icon}`"></i>
                </div>
                <span class="small fw-semibold">{{ cat.name }}</span>
                <span class="cat-count">{{ cat.count }} drives</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- ── PWA Install Prompt ── -->
      <section v-if="showInstallPrompt" class="pwa-banner">
        <div class="container">
          <div class="pwa-inner d-flex align-items-center gap-3 flex-wrap">
            <div class="pwa-icon">
              <i class="bi bi-phone-fill"></i>
            </div>
            <div class="flex-grow-1">
              <div class="fw-bold small">Add CampusHire to Home Screen</div>
              <div class="text-muted" style="font-size:.78rem">
                Get instant access — works offline, loads faster
              </div>
            </div>
            <div class="d-flex gap-2">
              <button class="btn btn-primary btn-sm fw-semibold" @click="installPWA">
                <i class="bi bi-download me-1"></i>Install
              </button>
              <button class="btn btn-outline-secondary btn-sm"
                      @click="showInstallPrompt = false">
                Later
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- ── Footer ── -->
      <footer class="site-footer">
        <div class="container">
          <div class="d-flex align-items-center justify-content-between flex-wrap gap-3">
            <div class="fw-bold">
              <i class="bi bi-briefcase-fill me-2 text-primary"></i>CampusHire
            </div>
            <div class="small text-muted">
              © {{ new Date().getFullYear() }} CampusHire · Built for campus placement
            </div>
            <div class="d-flex gap-3">
              <a href="#" class="footer-link">Privacy</a>
              <a href="#" class="footer-link">Terms</a>
              <a href="#" class="footer-link">Contact</a>
            </div>
          </div>
        </div>
      </footer>

    </div>
    <!-- ═══ END HOME CONTENT ═══ -->

    <!-- ═══ BACKDROP ═══ -->
    <transition name="fade-backdrop">
      <div v-if="isPanelOpen" class="auth-backdrop" @click="close"></div>
    </transition>

    <!-- ═══ SIDE PANEL ═══ -->
    <transition name="slide-panel">
      <div v-if="isPanelOpen" class="auth-panel">
        <div class="panel-inner">

          <button class="panel-close" @click="close" aria-label="Close">
            <i class="bi bi-x-lg"></i>
          </button>

          <div class="mb-4 pt-2">
            <div class="fw-bold fs-5">
              <i class="bi bi-briefcase-fill me-2 text-primary"></i>CampusHire
            </div>
            <p class="text-muted small mb-0 mt-1">
              {{ isLogin ? 'Welcome back! Sign in to continue.'
                         : 'Create your free account today.' }}
            </p>
          </div>

          <div class="panel-tabs mb-4">
            <router-link to="/login"  class="panel-tab" active-class="active">
              <i class="bi bi-box-arrow-in-right me-1"></i>Sign In
            </router-link>
            <router-link to="/signup" class="panel-tab" active-class="active">
              <i class="bi bi-person-plus me-1"></i>Sign Up
            </router-link>
          </div>

          <transition name="form-switch" mode="out-in">
            <router-view />
          </transition>
        </div>
      </div>
    </transition>

  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'HomeView',

  data: () => ({
    showInstallPrompt: false,
    deferredPrompt:    null,

    heroStats: [
      { num: '10K+',  label: 'Students' },
      { num: '248',   label: 'Companies' },
      { num: '₹24L',  label: 'Highest CTC' },
      { num: '94%',   label: 'Placement Rate' },
    ],

    platformStats: [
      { icon: 'bi-mortarboard-fill', color: '#0d6efd', value: '10,842', label: 'Registered Students' },
      { icon: 'bi-buildings-fill',   color: '#198754', value: '248',    label: 'Partner Companies' },
      { icon: 'bi-briefcase-fill',   color: '#fd7e14', value: '1,240',  label: 'Drives Posted' },
      { icon: 'bi-trophy-fill',      color: '#6f42c1', value: '3,891',  label: 'Total Placements' },
    ],

    funnel: [
      { label: 'Applied',     value: '4,820', pct: 100, color: '#0d6efd' },
      { label: 'Shortlisted', value: '2,140', pct: 44,  color: '#0dcaf0' },
      { label: 'Interviewed', value: '1,230', pct: 26,  color: '#fd7e14' },
      { label: 'Selected',    value: '892',   pct: 18,  color: '#198754' },
      { label: 'Placed',      value: '721',   pct: 15,  color: '#6f42c1' },
    ],

    features: [
      {
        icon: 'bi-graph-up-arrow', color: 'fi-blue',
        title: 'Smart Applications',
        desc:  'One-click apply with your profile. Track every stage from shortlist to offer.',
      },
      {
        icon: 'bi-shield-check', color: 'fi-green',
        title: 'Verified Companies',
        desc:  'Every recruiter is admin-verified. No fake listings, no spam.',
      },
      {
        icon: 'bi-bell-fill', color: 'fi-orange',
        title: 'Deadline Reminders',
        desc:  'Automatic email alerts before drive deadlines so you never miss an opportunity.',
      },
      {
        icon: 'bi-file-earmark-person-fill', color: 'fi-purple',
        title: 'Resume Builder',
        desc:  'Upload your resume, manage skills and bio — all in one student profile.',
      },
      {
        icon: 'bi-camera-video-fill', color: 'fi-teal',
        title: 'Interview Scheduler',
        desc:  'Recruiters schedule interviews directly on the platform with mode & meeting links.',
      },
      {
        icon: 'bi-bar-chart-fill', color: 'fi-red',
        title: 'Placement Analytics',
        desc:  'Admins and placement cells get real-time reports, CSVs and trend charts.',
      },
    ],

    categories: [
      { name: 'IT & Software',     icon: 'bi-laptop',          count: 142 },
      { name: 'Finance & Banking', icon: 'bi-cash-coin',        count: 87  },
      { name: 'Human Resources',   icon: 'bi-people-fill',      count: 34  },
      { name: 'Marketing',         icon: 'bi-megaphone-fill',   count: 61  },
      { name: 'Engineering',       icon: 'bi-gear-fill',        count: 98  },
      { name: 'Sales',             icon: 'bi-graph-up',         count: 45  },
      { name: 'Operations',        icon: 'bi-diagram-3-fill',   count: 29  },
      { name: 'Management',        icon: 'bi-person-workspace', count: 52  },
    ],

    charts: [],
  }),

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
      if (window.innerWidth < 768) {
        document.body.style.overflow = val ? 'hidden' : ''
      }
    },
  },

  mounted() {
    this.initCharts()
    this.initPWA()
  },

  beforeUnmount() {
    document.body.style.overflow = ''
    this.charts.forEach(c => c.destroy())
  },

  methods: {
    close() {
      this.$router.push('/')
    },

    // ── Charts ──────────────────────────────────────────────
    initCharts() {
      this.$nextTick(() => {
        this.initTrendChart()
        this.initSkillsChart()
        this.initPackageChart()
      })
    },

    initTrendChart() {
      const ctx = this.$refs.trendChart
      if (!ctx) return
      const chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar'],
          datasets: [
            {
              label: 'Offers Made',
              data: [124, 189, 156, 221, 198, 265],
              backgroundColor: 'rgba(13,110,253,.75)',
              borderRadius: 6,
              borderSkipped: false,
            },
            {
              label: 'Applications',
              data: [480, 620, 540, 780, 710, 890],
              backgroundColor: 'rgba(13,110,253,.15)',
              borderRadius: 6,
              borderSkipped: false,
            },
          ],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'top', labels: { boxWidth: 12, font: { size: 11 } } },
            tooltip: { mode: 'index' },
          },
          scales: {
            x: { grid: { display: false } },
            y: { grid: { color: '#f0f0f0' }, ticks: { font: { size: 11 } } },
          },
        },
      })
      this.charts.push(chart)
    },

    initSkillsChart() {
      const ctx = this.$refs.skillsChart
      if (!ctx) return
      const chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: ['Python', 'Java', 'React', 'SQL', 'Node.js', 'Others'],
          datasets: [{
            data: [28, 22, 18, 15, 10, 7],
            backgroundColor: [
              '#0d6efd', '#198754', '#fd7e14',
              '#6f42c1', '#0dcaf0', '#adb5bd',
            ],
            borderWidth: 2,
            borderColor: '#fff',
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              position: 'right',
              labels: { boxWidth: 12, font: { size: 11 }, padding: 14 },
            },
          },
          cutout: '62%',
        },
      })
      this.charts.push(chart)
    },

    initPackageChart() {
      const ctx = this.$refs.packageChart
      if (!ctx) return
      const chart = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['< 5 LPA', '5–10 LPA', '10–15 LPA', '15–20 LPA', '20–30 LPA', '> 30 LPA'],
          datasets: [{
            label: 'Offers',
            data: [42, 198, 261, 148, 89, 34],
            backgroundColor: [
              '#adb5bd', '#0dcaf0', '#0d6efd',
              '#6f42c1', '#198754', '#ffc107',
            ],
            borderRadius: 6,
            borderSkipped: false,
          }],
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
          },
          scales: {
            x: { grid: { color: '#f0f0f0' }, ticks: { font: { size: 11 } } },
            y: { grid: { display: false }, ticks: { font: { size: 11 } } },
          },
        },
      })
      this.charts.push(chart)
    },

    // ── PWA ──────────────────────────────────────────────────
    initPWA() {
      window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault()
        this.deferredPrompt    = e
        this.showInstallPrompt = true
      })
      window.addEventListener('appinstalled', () => {
        this.showInstallPrompt = false
        this.deferredPrompt    = null
      })
    },

    async installPWA() {
      if (!this.deferredPrompt) return
      this.deferredPrompt.prompt()
      const { outcome } = await this.deferredPrompt.userChoice
      this.deferredPrompt    = null
      this.showInstallPrompt = outcome !== 'accepted'
    },
  },
}
</script>

<style scoped>
/* ── Layout ── */
.home-wrapper  { position: relative; }

/* ── Hero ── */
.hero-section {
  background: #06091a;
  position: relative;
  overflow: hidden;
  padding-top: 4rem;
  padding-bottom: 5rem;
  color: #fff;
}
.hero-grid-overlay {
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(99,102,241,.08) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99,102,241,.08) 1px, transparent 1px);
  background-size: 48px 48px;
  pointer-events: none;
}
.hero-pill {
  background: rgba(99,102,241,.18);
  border: 1px solid rgba(99,102,241,.35);
  border-radius: 50px;
  padding: .3rem 1rem;
  font-size: .78rem;
  font-weight: 600;
  color: #a5b4fc;
}
.pill-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #6366f1;
  box-shadow: 0 0 6px #6366f1;
  display: inline-block;
  animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
  0%, 100% { opacity: 1; } 50% { opacity: .4; }
}
.hero-heading {
  font-size: clamp(2rem, 5vw, 3.2rem);
  line-height: 1.12;
  letter-spacing: -.02em;
  color: #fff;
}
.gradient-text {
  background: linear-gradient(90deg, #6366f1, #06b6d4);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.hero-sub {
  font-size: .97rem;
  color: rgba(255,255,255,.65);
  max-width: 440px;
  line-height: 1.7;
}

.btn-hero-primary {
  background: #6366f1;
  border: none;
  color: #fff;
  font-weight: 700;
  border-radius: 10px;
  padding: .65rem 1.5rem;
  transition: all .2s;
}
.btn-hero-primary:hover {
  background: #4f46e5;
  color: #fff;
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(99,102,241,.4);
}
.btn-hero-ghost {
  background: transparent;
  border: 1.5px solid rgba(255,255,255,.2);
  color: rgba(255,255,255,.85);
  font-weight: 600;
  border-radius: 10px;
  padding: .65rem 1.5rem;
  transition: all .2s;
}
.btn-hero-ghost:hover {
  background: rgba(255,255,255,.08);
  color: #fff;
  border-color: rgba(255,255,255,.4);
}

.hero-stats { gap: 2.5rem; }
.stat-num   { font-size: 1.5rem; font-weight: 800; color: #fff; }
.stat-label { font-size: .75rem; color: rgba(255,255,255,.5); margin-top: .15rem; }

/* Floating cards */
.hero-card-stack {
  position: relative;
  height: 340px;
}
.float-card {
  position: absolute;
  background: #fff;
  border-radius: 14px;
  padding: 1rem 1.25rem;
}
.float-card-1 { top: 20px; left: 10%; width: 200px; }
.float-card-2 {
  bottom: 30px; left: 5%; width: 160px;
  padding-bottom: 1.25rem;
}
.float-card-3 { top: 50%; right: 5%; transform: translateY(-50%); }
.fc-avatar {
  width: 32px; height: 32px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: .85rem; flex-shrink: 0;
}
.fc-bar { height: 6px; background: #f0f0f0; border-radius: 99px; overflow: hidden; margin-top: .5rem; }
.fc-bar-fill { height: 100%; background: linear-gradient(90deg,#6366f1,#06b6d4); border-radius: 99px; }
.mini-bar {
  flex: 1; background: linear-gradient(to top, #6366f1, #a5b4fc);
  border-radius: 4px 4px 0 0; min-height: 20px;
  max-height: 60px;
}
.float-card-2 .d-flex { height: 60px; align-items: flex-end; }
.hero-central-icon {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 90px; height: 90px; border-radius: 22px;
  background: linear-gradient(135deg, #6366f1, #06b6d4);
  display: flex; align-items: center; justify-content: center;
  font-size: 2.5rem; color: #fff;
  box-shadow: 0 16px 48px rgba(99,102,241,.45);
}

/* ── Stats Banner ── */
.stats-banner { background: #fff; border-bottom: 1px solid #f0f0f0; }
.stats-row    { }
.stats-cell {
  padding: 1.75rem 1rem;
  text-align: center;
  border-right: 1px solid #f0f0f0;
}
.stats-cell:last-child { border-right: none; }
.stats-icon { font-size: 1.4rem; display: block; margin-bottom: .5rem; }
.stats-num  { font-size: 1.5rem; font-weight: 800; color: #111; line-height: 1; }
.stats-lbl  { font-size: .75rem; color: #6c757d; margin-top: .3rem; }

/* ── Section headers ── */
.section-tag {
  font-size: .72rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .12em; color: #6366f1;
  background: rgba(99,102,241,.08);
  padding: .25rem .75rem; border-radius: 50px;
}
.section-title { font-size: clamp(1.4rem, 3vw, 2rem); color: #111; }

/* ── Charts ── */
.chart-card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #f0f0f0;
  overflow: hidden;
  padding: 1.25rem;
}
.chart-card-header {
  display: flex; justify-content: space-between; align-items: flex-start;
  margin-bottom: 1rem;
}
.chart-body { position: relative; height: 200px; }

.funnel-body { padding-top: .5rem; }
.funnel-row  { display: flex; align-items: center; gap: .75rem; margin-bottom: .75rem; }
.funnel-label { width: 90px; font-size: .78rem; color: #555; flex-shrink: 0; }
.funnel-bar-wrap {
  flex: 1; background: #f0f0f0; border-radius: 99px; height: 10px; overflow: hidden;
}
.funnel-bar { height: 100%; border-radius: 99px; transition: width 1s ease; }
.funnel-val { font-size: .78rem; font-weight: 700; color: #333; flex-shrink: 0; width: 40px; text-align: right; }

/* ── Features ── */
.feature-card {
  padding: 1.5rem;
  background: #f8f9ff;
  border-radius: 16px;
  border: 1px solid #eee;
  height: 100%;
  transition: transform .2s, box-shadow .2s;
}
.feature-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(0,0,0,.07); }
.feature-icon-wrap {
  width: 48px; height: 48px; border-radius: 12px;
  display: flex; align-items: center; justify-content: center;
}
.fi-blue   { background: #e8f0fe; color: #0d6efd; }
.fi-green  { background: #e6f4ea; color: #198754; }
.fi-orange { background: #fff3e0; color: #fd7e14; }
.fi-purple { background: #f3e8ff; color: #6f42c1; }
.fi-teal   { background: #e0f7fa; color: #0097a7; }
.fi-red    { background: #fce8e8; color: #dc3545; }

/* ── Categories ── */
.cat-card {
  background: #fff;
  border: 1px solid #ebebeb;
  border-radius: 12px;
  padding: 1rem;
  display: flex; flex-direction: column; align-items: center;
  gap: .4rem; text-align: center; cursor: pointer;
  transition: all .2s;
}
.cat-card:hover {
  background: #f0f4ff;
  border-color: #c5d8ff;
  transform: translateY(-3px);
}
.cat-icon-wrap {
  width: 44px; height: 44px; border-radius: 12px;
  background: #e8f0fe; color: #0d6efd;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem;
}
.cat-count { font-size: .7rem; color: #adb5bd; }

/* ── PWA Banner ── */
.pwa-banner {
  background: linear-gradient(90deg, #06091a, #1a1040);
  color: #fff;
  padding: 1rem 0;
}
.pwa-inner { max-width: 640px; margin: 0 auto; }
.pwa-icon {
  width: 44px; height: 44px; border-radius: 12px;
  background: rgba(99,102,241,.3);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; flex-shrink: 0;
}

/* ── Footer ── */
.site-footer {
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  padding: 1.5rem 0;
}
.footer-link { color: #6c757d; font-size: .82rem; text-decoration: none; }
.footer-link:hover { color: #0d6efd; }

/* ════════════════════════════════
   AUTH PANEL (unchanged logic)
════════════════════════════════ */
.auth-backdrop {
  position: fixed; inset: 0; z-index: 1040;
  background: rgba(0,0,0,.35);
}
.auth-panel {
  position: fixed; top: 0; right: 0; bottom: 0;
  width: 50%; z-index: 1050;
  background: #fff;
  box-shadow: -12px 0 48px rgba(0,0,0,.14);
  overflow: hidden; display: flex; flex-direction: column;
}
.panel-inner {
  flex: 1; overflow-y: auto;
  padding: 2rem 2.5rem;
  position: relative;
}
.panel-close {
  position: absolute; top: 1.25rem; right: 1.25rem;
  background: #f1f3f5; border: none; border-radius: 50%;
  width: 36px; height: 36px;
  display: flex; align-items: center; justify-content: center;
  font-size: .9rem; cursor: pointer; color: #555;
  transition: background .2s, color .2s, transform .2s; z-index: 1;
}
.panel-close:hover { background: #e2e6ea; color: #111; transform: rotate(90deg); }
.panel-tabs {
  display: flex; background: #f1f3f5;
  border-radius: 12px; padding: 4px; gap: 3px;
}
.panel-tab {
  flex: 1; padding: .5rem .75rem; text-align: center;
  font-size: .88rem; font-weight: 600; color: #6c757d;
  border-radius: 9px; text-decoration: none; transition: all .22s;
}
.panel-tab.active {
  background: #fff; color: #0d6efd;
  box-shadow: 0 2px 10px rgba(0,0,0,.09);
}
.panel-tab:hover:not(.active) { color: #343a40; }

/* ── Transitions ── */
.slide-panel-enter-active { transition: transform .4s cubic-bezier(.16,1,.3,1); }
.slide-panel-leave-active { transition: transform .3s cubic-bezier(.4,0,1,1); }
.slide-panel-enter-from,
.slide-panel-leave-to     { transform: translateX(100%); }

.fade-backdrop-enter-active { transition: opacity .35s ease; }
.fade-backdrop-leave-active { transition: opacity .25s ease; }
.fade-backdrop-enter-from,
.fade-backdrop-leave-to     { opacity: 0; }

.form-switch-enter-active { transition: opacity .18s ease, transform .18s ease; }
.form-switch-leave-active { transition: opacity .14s ease, transform .14s ease; }
.form-switch-enter-from   { opacity: 0; transform: translateX(18px); }
.form-switch-leave-to     { opacity: 0; transform: translateX(-18px); }

/* ── Responsive ── */
@media (max-width: 768px) {
  .auth-panel  { width: 100vw; }
  .panel-inner { padding: 1.5rem 1.25rem; }
  .stats-cell  { border-right: none; border-bottom: 1px solid #f0f0f0; }
  .hero-card-stack { display: none; }
  .hero-stats  { gap: 1.5rem; }
}
@media (min-width: 769px) and (max-width: 1024px) {
  .auth-panel { width: 60%; }
}
</style>