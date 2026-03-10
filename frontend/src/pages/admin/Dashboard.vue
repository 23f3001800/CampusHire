<template>
  <div class="dashboard bg-light min-vh-100 py-4">
    <div class="container-fluid px-4">

      <!-- Header -->
      <div class="d-flex justify-content-between
                  align-items-center mb-4 flex-wrap gap-2">
        <div>
          <h3 class="fw-bold mb-0">Admin Dashboard</h3>
          <small class="text-muted">Full platform overview</small>
        </div>
        <div class="d-flex gap-2 flex-wrap">
          <!-- Export buttons -->
          <div class="dropdown">
            <button class="btn btn-success btn-sm dropdown-toggle"
                    :disabled="adminStore.exportLoading"
                    data-bs-toggle="dropdown">
              <span v-if="adminStore.exportLoading"
                    class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-download me-1"></i>Export CSV
            </button>
            <ul class="dropdown-menu shadow">
              <li v-for="e in exportOptions" :key="e.type">
                <a class="dropdown-item" href="#"
                   @click.prevent="exportData(e.type)">
                  <i :class="`bi ${e.icon} me-2 text-${e.color}`"></i>
                  {{ e.label }}
                </a>
              </li>
            </ul>
          </div>

          <button class="btn btn-outline-secondary btn-sm"
                  :disabled="adminStore.loading"
                  @click="adminStore.fetchAll(true)">
            <span v-if="adminStore.loading"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-arrow-clockwise me-1"></i>Refresh
          </button>
        </div>
      </div>

      <!-- Error banner -->
      <div v-if="adminStore.error"
           class="alert alert-danger d-flex align-items-center mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>
        {{ adminStore.error }}
        <button class="btn-close ms-auto"
                @click="adminStore.error = null"></button>
      </div>

      <!-- Stat cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-4 col-lg-2"
             v-for="s in statCards" :key="s.label">
          <router-link :to="s.to" class="text-decoration-none">
            <div class="stat-card text-white h-100" :class="s.bg">
              <i :class="`bi ${s.icon} fs-3 opacity-75`"></i>
              <div class="mt-1">
                <div class="fs-4 fw-bold lh-1">{{ s.value }}</div>
                <small class="opacity-90">{{ s.label }}</small>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Chart row -->
      <div class="row g-4 mb-4">
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-pie-chart me-2 text-primary"></i>
                Application Status Distribution
              </h6>
            </div>
            <div class="card-body d-flex align-items-center
                        justify-content-center" style="height:240px">
              <canvas ref="statusChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-header bg-white border-bottom py-3">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-bar-chart me-2 text-success"></i>
                Students by Branch
              </h6>
            </div>
            <div class="card-body d-flex align-items-center
                        justify-content-center" style="height:240px">
              <canvas ref="branchChart"></canvas>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-0 border-bottom">
        <li class="nav-item" v-for="t in tabs" :key="t.key">
          <a class="nav-link px-4 py-3"
            :class="{ active: activeTab === t.key }"
            @click.prevent="activeTab = t.key"
            href="#">
            <i :class="`bi ${t.icon} me-1`"></i>{{ t.label }}
            <span v-if="t.badge"
                  class="badge bg-danger rounded-pill ms-1">
              {{ t.badge }}
            </span>
          </a>
        </li>
      </ul>

      <div class="tab-content bg-white rounded-bottom
                  shadow-sm p-4">
        <!-- ── PLACEMENT DRIVES ────────────────────────────────── -->
        <div v-show="activeTab === 'drives'">
          <!-- Filters -->
          <div class="d-flex flex-wrap gap-2 mb-4">
            <div class="input-group" style="max-width:280px">
              <span class="input-group-text bg-white">
                <i class="bi bi-search"></i>
              </span>
              <input v-model="driveSearch" type="text"
                     class="form-control border-start-0"
                     placeholder="Search drives, companies…" />
            </div>
            <select v-model="driveStatusFilter"
                    class="form-select" style="max-width:160px">
              <option value="">All Statuses</option>
              <option>Open</option>
              <option>Closed</option>
              <option>Completed</option>
            </select>
            <select v-model="driveApprovalFilter"
                    class="form-select" style="max-width:180px">
              <option value="">All Approvals</option>
              <option value="Pending">Pending Approval</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
            <button v-if="driveSearch || driveStatusFilter ||
                          driveApprovalFilter"
                    class="btn btn-outline-secondary btn-sm"
                    @click="driveSearch = '';
                            driveStatusFilter = '';
                            driveApprovalFilter = ''">
              <i class="bi bi-x me-1"></i>Clear
            </button>
          </div>

          <div v-if="adminStore.loadingDrives"
               class="text-center py-5">
            <div class="spinner-border text-primary"></div>
          </div>

          <div v-else-if="!filteredDrives.length"
               class="text-center text-muted py-5">
            <i class="bi bi-folder-x fs-1 d-block mb-2"></i>
            No drives found
          </div>

          <div v-else class="row g-4">
            <div class="col-lg-6"
                 v-for="d in filteredDrives" :key="d.id">
              <div class="card drive-card shadow-sm h-100 border-0"
                   :class="{
                     'border-start border-4 border-warning':
                       d.admin_approval_status === 'Pending',
                     'border-start border-4 border-danger':
                       d.admin_approval_status === 'Rejected',
                   }">
                <div class="card-body">
                  <div class="d-flex justify-content-between mb-2">
                    <div class="flex-grow-1 pe-2">
                      <h5 class="mb-1">{{ d.title }}</h5>
                      <p class="text-muted mb-0 small">
                        <i class="bi bi-building me-1"></i>
                        {{ d.company_name }}
                        <span v-if="d.location" class="ms-2">
                          <i class="bi bi-geo-alt me-1"></i>
                          {{ d.location }}
                        </span>
                      </p>
                    </div>
                    <div class="d-flex flex-column align-items-end
                                gap-1 flex-shrink-0">
                      <span class="badge"
                            :class="statusBadge(d.status)">
                        {{ d.status }}
                      </span>
                      <span class="badge"
                            :class="approvalBadge(
                              d.admin_approval_status)">
                        {{ d.admin_approval_status || 'N/A' }}
                      </span>
                    </div>
                  </div>

                  <!-- Info grid -->
                  <div class="row g-2 bg-light rounded
                              p-2 mb-3 small">
                    <div class="col-6">
                      <span class="text-muted d-block">Type</span>
                      <strong>{{ d.job_type || '—' }}</strong>
                    </div>
                    <div class="col-6">
                      <span class="text-muted d-block">
                        Deadline
                      </span>
                      <strong :class="{
                        'text-danger': isUrgent(
                          d.application_deadline)
                      }">
                        {{ fmtDate(d.application_deadline) }}
                      </strong>
                    </div>
                    <div class="col-6">
                      <span class="text-muted d-block">
                        Drive Date
                      </span>
                      <strong>{{ fmtDate(d.drive_date) }}</strong>
                    </div>
                    <div class="col-6">
                      <span class="text-muted d-block">
                        Applicants
                      </span>
                      <strong>{{ d.total_applications ?? 0 }}</strong>
                    </div>
                  </div>

                  <!-- Applicant stats badges -->
                  <div v-if="d.total_applications > 0"
                       class="d-flex flex-wrap gap-1 mb-3">
                    <template
                      v-for="(v, k) in adminStore
                        .getDriveApplicantStats(d.id)"
                      :key="k">
                      <span v-if="k !== 'total' && v > 0"
                            class="badge"
                            :class="statusBadge(k)">
                        {{ v }} {{ k }}
                      </span>
                    </template>
                  </div>

                  <!-- Drive actions -->
                  <div class="d-flex gap-2 flex-wrap">
                    <router-link
                      :to="`/admin/${d.company_id}/drives/${d.id}`"
                      class="btn btn-outline-primary btn-sm flex-grow-1">
                      <i class="bi bi-eye me-1"></i>Details
                    </router-link>

                    <!-- Approval quick-actions on card -->
                    <td>
                      <span class="badge bg-light text-dark border">
                        <i class="bi bi-people"></i>
                        {{ d.total_applications || 0 }} Applications
                      </span>
                    </td>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- ── PLACEMENTS ───────────────────────────────────────── -->
        <div v-show="activeTab === 'placements'">
          <!-- Stats strip -->
          <div class="d-flex flex-wrap gap-2 mb-4">
            <span class="badge fs-6 bg-primary px-3 py-2">
              Total: {{ adminStore.placementStats.total }}
            </span>
            <span class="badge fs-6 bg-warning
                         text-dark px-3 py-2">
              Offered: {{ adminStore.placementStats.offered }}
            </span>
            <span class="badge fs-6 bg-success px-3 py-2">
              Joined: {{ adminStore.placementStats.joined }}
            </span>
            <span class="badge fs-6 bg-danger px-3 py-2">
              Declined: {{ adminStore.placementStats.declined }}
            </span>
          </div>

          <!-- Placement search -->
          <div class="mb-4">
            <div class="input-group" style="max-width:320px">
              <span class="input-group-text bg-white">
                <i class="bi bi-search"></i>
              </span>
              <input v-model="placementSearch" type="text"
                     class="form-control border-start-0"
                     placeholder="Search student, company…" />
            </div>
          </div>

          <div v-if="!adminStore.placements.length"
               class="empty-state py-5">
            <i class="bi bi-trophy fs-1 text-muted
                       d-block mb-2"></i>
            <p class="text-muted">No placements recorded yet</p>
          </div>

          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Student</th><th>Company</th>
                  <th>Role</th><th>Package</th>
                  <th>Status</th><th>Joining Date</th>
                  <th>Offer</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in filteredPlacements" :key="p.id">
                  <td>
                    <router-link
                      :to="`/admin/students`"
                      class="fw-semibold text-decoration-none">
                      {{ p.student_name }}
                    </router-link>
                  </td>
                  <td>{{ p.company_name }}</td>
                  <td>{{ p.position_title }}</td>
                  <td>
                    <span v-if="p.salary"
                          class="text-success fw-bold">
                      {{ fmtSalary(p.salary, p.currency) }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>
                    <span class="badge"
                          :class="placementBadge(p.status)">
                      {{ p.status }}
                    </span>
                  </td>
                  <td>
                    <small>
                      {{ p.joining_date
                          ? fmtDate(p.joining_date) : '—' }}
                    </small>
                  </td>
                  <td>
                    <a v-if="p.offer_letter_filename"
                      @click.prevent="viewOffer(p.offer_letter_filename)"
                      class="btn btn-sm btn-outline-secondary">
                      <i class="bi bi-file-earmark-pdf"></i>
                    </a>

                    <span v-else class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/adminStore'
import { useUserStore }  from '@/stores/userStore'
import {
  Chart,
  DoughnutController,
  BarController,
  ArcElement,
  BarElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
} from 'chart.js'



Chart.register(
  DoughnutController, BarController,
  ArcElement, BarElement,
  CategoryScale, LinearScale,
  Tooltip, Legend
)


export default {
  name: 'AdminDashboard',

  setup() {
    return {
      adminStore: useAdminStore(),
      userStore:  useUserStore(),
      id:    useUserStore().id,
    }
  },

  data: () => ({
    activeTab: 'drives',
    exportOptions: [
      { type: 'students', icon: 'bi-people-fill', color: 'primary', label: 'Students' },
      { type: 'companies', icon: 'bi-building', color: 'success', label: 'Companies' },
      { type: 'drives',    icon: 'bi-briefcase-fill', color: 'info', label: 'Drives' },
      { type: 'placements',icon: 'bi-trophy-fill', color: 'warning', label: 'Placements' },
    ],
    rowBusy:            {},
    offerBusy:             {},
    driveSearch:        '',
    driveStatusFilter:  '',
    driveApprovalFilter:'',
    placementSearch:    '',
    _statusChart:       null,
    _branchChart:       null,
  }),

  computed: {
    tabs() {
      const s = this.adminStore.dashboardStats
      return [
        // {
        //   key: 'pending', icon: 'bi-hourglass-split',
        //   label: 'Pending Approvals',
        //   badge: s.pending_companies || null,
        // },
        { key: 'drives',     icon: 'bi-briefcase', label: 'Placement Drives' },
        { key: 'placements', icon: 'bi-trophy',    label: 'Placements'       },
      ]
    },

    statCards() {
      const s = this.adminStore.dashboardStats
      return [
        {
          label: 'Students',
          value: s.total_students    ?? 0,
          bg: 'bg-primary', icon: 'bi-mortarboard-fill',
          to: '/admin/students',
        },
        {
          label: 'Companies',
          value: s.total_companies   ?? 0,
          bg: 'bg-success', icon: 'bi-building',
          to: '/admin/companies',
        },
        {
          label: 'Pending',
          value: s.pending_companies ?? 0,
          bg: 'bg-warning', icon: 'bi-hourglass-split',
          to: '/admin/companies',
        },
        {
          label: 'Open Drives',
          value: s.open_drives ?? 0,
          bg: 'bg-info', 
          icon: 'bi-briefcase-fill',
          to: `/admin/1`, // Use '/admin/id' if it's meant to be a literal string
          active: false,
        },
        {
          label: 'Placed',
          value: s.total_placements ?? 0,
          bg: 'bg-success', 
          icon: 'bi-trophy-fill',
          to: `/admin/1`,
          active: true, // Sets this tab as active
        },
        {
          label: 'Applications',
          value: s.total_applications ?? 0,
          bg: 'bg-secondary', 
          icon: 'bi-file-earmark-text-fill',
          to: `/admin/1`,
          active: false,
        },
      ]
    },

    filteredDrives() {
      return this.adminStore.drives.filter(d => {
        const q = this.driveSearch.toLowerCase()
        const matchSearch = !q ||
          d.title?.toLowerCase().includes(q) ||
          d.company_name?.toLowerCase().includes(q)
        const matchStatus = !this.driveStatusFilter ||
          d.status === this.driveStatusFilter
        const matchApproval = !this.driveApprovalFilter ||
          d.admin_approval_status === this.driveApprovalFilter
        return matchSearch && matchStatus && matchApproval
      })
    },

    filteredPlacements() {
      if (!this.placementSearch) return this.adminStore.placements
      const q = this.placementSearch.toLowerCase()
      return this.adminStore.placements.filter(p =>
        p.student_name?.toLowerCase().includes(q) ||
        p.company_name?.toLowerCase().includes(q) ||
        p.position_title?.toLowerCase().includes(q)
      )
    },
  },

  async mounted() {
    await this.adminStore.fetchAll()
    this.$nextTick(() => this.renderCharts())
  },

  watch: {
    'adminStore.students'() {
      this.$nextTick(() => this.renderBranchChart())
    },
  },

  methods: {
    async exportData(type) {
      try { await this.adminStore.exportData(type) }
      catch (e) { alert(e.message ?? 'Export failed') }
    },

    async viewOffer(filename) {
      this.offerBusy = true  // ✅ no .value
      try {
        const blob = await this.adminStore.fetchofferletter(filename)
        if (blob) window.open(URL.createObjectURL(blob), '_blank')
      } catch (e) {
        showToast('danger', e?.message ?? 'Failed to load resume.')
      } finally {
        this.offerBusy = false // ✅ correct
      }
    },

    // ── Charts ──────────────────────────────────────────────────────────
    renderCharts() {
      this.renderStatusChart()
      this.renderBranchChart()
    },

    renderStatusChart() {
      const el = this.$refs.statusChart
      if (!el) return
      const dist = this.adminStore.applicationStatusDistribution
      const data = [
        dist.Applied, dist.Shortlisted,
        dist.Selected, dist.Rejected,
      ]
      if (data.every(v => v === 0)) return
      if (this._statusChart) this._statusChart.destroy()
      this._statusChart = new Chart(el, {
        type: 'doughnut',
        data: {
          labels: ['Applied', 'Shortlisted', 'Selected', 'Rejected'],
          datasets: [{
            data,
            backgroundColor: ['#0d6efd','#0dcaf0','#198754','#dc3545'],
            borderWidth: 2,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { boxWidth: 12 } },
          },
        },
      })
    },

    renderBranchChart() {
      const el = this.$refs.branchChart
      if (!el) return
      const map = this.adminStore.studentsByBranch
      const labels = Object.keys(map)
      const values = Object.values(map)
      if (!labels.length) return
      if (this._branchChart) this._branchChart.destroy()
      this._branchChart = new Chart(el, {
        type: 'bar',
        data: {
          labels,
          datasets: [{
            label: 'Students',
            data: values,
            backgroundColor: '#0d6efd',
            borderRadius: 4,
          }],
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: {
            y: { beginAtZero: true, ticks: { precision: 0 } },
          },
        },
      })
    },

    // ── Utilities ───────────────────────────────────────────────────────
    fmtDate(d) {
      return d
        ? new Date(d).toLocaleDateString('en-IN', {
            day: 'numeric', month: 'short', year: 'numeric',
          })
        : '—'
    },

    fmtSalary(s, currency = 'INR') {
      if (!s) return '—'
      const sym = currency === 'INR' ? '₹' : currency
      return s >= 100_000
        ? `${sym}${(s / 100_000).toFixed(1)} LPA`
        : `${sym}${s.toLocaleString('en-IN')}`
    },

    isUrgent(deadline) {
      if (!deadline) return false
      const diff = new Date(deadline) - new Date()
      return diff > 0 && diff < 3 * 86_400_000
    },

    initials(name) {
      return (name || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },

    statusBadge(s) {
      return {
        Open: 'bg-success', Closed: 'bg-secondary',
        Completed: 'bg-primary',
        Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
        Selected: 'bg-success', Rejected: 'bg-danger',
      }[s] ?? 'bg-secondary'
    },

    approvalBadge(s) {
      return {
        Pending:  'bg-warning text-dark',
        Approved: 'bg-success',
        Rejected: 'bg-danger',
      }[s] ?? 'bg-secondary'
    },

    placementBadge(s) {
      return {
        Offered:  'bg-warning text-dark',
        Joined:   'bg-success',
        Declined: 'bg-danger',
      }[s] ?? 'bg-secondary'
    },
  },

  // Clean up Chart.js instances
  beforeUnmount() {
    this._statusChart?.destroy()
    this._branchChart?.destroy()
  },
}
</script>

<style scoped>
.stat-card {
  padding: 1.1rem 1.25rem; border-radius: 10px;
  display: flex; flex-direction: column; gap: .4rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.12);
  transition: transform .15s;
}
.stat-card:hover { transform: translateY(-2px); }
.company-avatar {
  width: 32px; height: 32px; border-radius: 6px;
  background: #e9ecef; color: #495057;
  display: flex; align-items: center; justify-content: center;
  font-size: .7rem; font-weight: 700; flex-shrink: 0;
}
.drive-card { transition: transform .15s; }
.drive-card:hover { transform: translateY(-2px); }
.tab-content {
  border: 1px solid #dee2e6; border-top: none;
}
.empty-state { text-align: center; }
.nav-tabs .nav-link {
  color: #6c757d; border: none;
  border-bottom: 3px solid transparent;
  padding: .75rem 1.25rem;
}
.nav-tabs .nav-link.active {
  color: #0d6efd; border-bottom-color: #0d6efd;
  background: none; font-weight: 600;
}
.nav-tabs .nav-link:hover {
  color: #0d6efd; background: #f8f9fa;
}
.table th {
  font-size: .8rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d;
}
</style>
