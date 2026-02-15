<template>
  <div class="dashboard bg-light min-vh-100">

    <!-- Loading -->
    <div v-if="companyStore.loadingProfile" class="d-flex justify-content-center align-items-center" style="min-height:60vh">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3"></div>
        <p class="text-muted">Loading company profile…</p>
      </div>
    </div>

    <!-- Profile incomplete -->
    <div v-else-if="!companyStore.isProfileComplete" class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card shadow-sm border-warning">
            <div class="card-body text-center p-5">
              <i class="bi bi-exclamation-triangle-fill text-warning fs-1 mb-3"></i>
              <h4>Complete Your Company Profile</h4>
              <p class="text-muted mb-4">
                {{ companyStore.profileCompletionDetails.percentage }}% complete — finish your profile to start posting drives.
              </p>
              <div class="progress mb-4" style="height:10px">
                <div class="progress-bar" :class="progressClass(companyStore.profileCompletionDetails.percentage)"
                  :style="{ width: companyStore.profileCompletionDetails.percentage + '%' }">
                </div>
              </div>
              <div v-if="companyStore.missingFieldsWithLabels.required.length" class="text-start mb-4">
                <h6 class="text-danger"><i class="bi bi-x-circle me-2"></i>Required:</h6>
                <ul class="list-unstyled ms-3">
                  <li v-for="f in companyStore.missingFieldsWithLabels.required" :key="f.key">
                    <i class="bi bi-arrow-right me-2"></i>{{ f.label }}
                  </li>
                </ul>
              </div>
              <router-link to="/company/profile" class="btn btn-primary btn-lg">
                <i class="bi bi-pencil me-2"></i>Complete Profile
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pending approval -->
    <div v-else-if="!companyStore.isApproved" class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card shadow-sm border-info">
            <div class="card-body text-center p-5">
              <i class="bi bi-clock-history text-info fs-1 mb-3"></i>
              <h4>Profile Under Review</h4>
              <p class="text-muted mb-4">Your company profile is being reviewed by our admin team.</p>
              <div class="alert alert-info">
                <strong>Status:</strong>
                <span class="badge bg-warning ms-2">{{ companyStore.approvalStatus }}</span>
              </div>
              <div class="d-flex justify-content-center gap-2">
                <router-link to="/company/profile" class="btn btn-outline-primary">View Profile</router-link>
                <button class="btn btn-outline-secondary" @click="refresh">
                  <i class="bi bi-arrow-clockwise me-1"></i>Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Main dashboard (approved) -->
    <div v-else class="container py-4">

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 class="fw-bold mb-1">{{ companyStore.companyName }}</h3>
          <p class="text-muted mb-0">
            <i class="bi bi-check-circle-fill text-success me-1"></i>Verified Company
          </p>
        </div>
        <router-link to="/company/create-drive" class="btn btn-success">
          <i class="bi bi-plus-circle me-2"></i>New Drive
        </router-link>
      </div>

      <!-- Stats -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3" v-for="s in stats" :key="s.label">
          <div class="stat-card text-white" :class="s.bg">
            <i :class="`bi ${s.icon} fs-2 opacity-75`"></i>
            <div>
              <h3 class="mb-0 fw-bold">{{ s.value }}</h3>
              <small>{{ s.label }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item" v-for="t in tabs" :key="t.key">
          <a class="nav-link" :class="{ active: activeTab === t.key }"
            @click.prevent="activeTab = t.key" href="#">
            {{ t.label }} ({{ t.count }})
          </a>
        </li>
      </ul>

      <!-- Loading drives -->
      <div v-if="companyStore.loadingDrives" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- No drives -->
      <div v-else-if="!displayedDrives.length" class="text-center py-5">
        <i class="bi bi-inbox fs-1 text-muted"></i>
        <p class="mt-2 text-muted">No drives yet</p>
        <router-link to="/company/create-drive" class="btn btn-primary mt-2">
          <i class="bi bi-plus-circle me-2"></i>Create First Drive
        </router-link>
      </div>

      <!-- Drive cards -->
      <div v-else class="row g-4">
        <div class="col-lg-6" v-for="drive in displayedDrives" :key="drive.id">
          <div class="card drive-card shadow-sm h-100 border-0"
            :class="{ 'border-start border-warning': drive.status !== 'Open' }">
            <div class="card-body">
              <div class="d-flex justify-content-between mb-2">
                <div>
                  <h5 class="mb-1">{{ drive.title }}</h5>
                  <p class="text-muted mb-0 small"><i class="bi bi-geo-alt me-1"></i>{{ drive.location }}</p>
                </div>
                <span class="badge" :class="statusBadge(drive.status)">{{ drive.status }}</span>
              </div>

              <!-- Details grid -->
              <div class="row g-2 bg-light rounded p-2 mb-3 small">
                <div class="col-6"><span class="text-muted d-block">Type</span><strong>{{ drive.job_type || '—' }}</strong></div>
                <div class="col-6"><span class="text-muted d-block">Deadline</span><strong>{{ formatDate(drive.application_deadline) }}</strong></div>
                <div class="col-6"><span class="text-muted d-block">Drive Date</span><strong>{{ formatDate(drive.drive_date) }}</strong></div>
                <div class="col-6"><span class="text-muted d-block">Applicants</span><strong>{{ drive.total_applications }}</strong></div>
              </div>

              <!-- Applicant breakdown -->
              <div v-if="drive.total_applications > 0" class="d-flex flex-wrap gap-1 mb-3">
                <template v-for="(v, k) in companyStore.getDriveStats(drive.id)" :key="k">
                  <span v-if="v > 0" class="badge" :class="statusBadge(k)">{{ v }} {{ k }}</span>
                </template>
              </div>

              <!-- Actions -->
              <div class="d-flex gap-2">
                <router-link :to="`/company/drives/${drive.id}`" class="btn btn-outline-primary btn-sm flex-grow-1">
                  <i class="bi bi-eye me-1"></i>Details
                </router-link>
                <router-link v-if="drive.total_applications" :to="`/company/drives/${drive.id}/applicants`"
                  class="btn btn-primary btn-sm">
                  <i class="bi bi-people me-1"></i>Applicants
                </router-link>
                <button class="btn btn-outline-secondary btn-sm" @click="toggleStatus(drive.id)"
                  :title="drive.status === 'Open' ? 'Close drive' : 'Reopen drive'">
                  <i class="bi" :class="drive.status === 'Open' ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Recent applicants -->
      <div v-if="companyStore.recentApplicants.length" class="mt-5">
        <h5 class="fw-bold mb-3">Recent Applicants</h5>
        <div class="card shadow-sm border-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0">
              <thead class="table-light">
                <tr>
                  <th>Applicant</th><th>Drive</th><th>Applied</th><th>Status</th><th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in companyStore.recentApplicants" :key="a.id">
                  <td>
                    <strong>{{ a.student_name }}</strong><br>
                    <small class="text-muted">{{ a.student_email }}</small>
                  </td>
                  <td>{{ a.drive_title }}</td>
                  <td>{{ formatDate(a.applied_date) }}</td>
                  <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
                  <td>
                    <router-link :to="`/company/drives/${a.drive_id}/applicants`"
                      class="btn btn-sm btn-outline-primary">View</router-link>
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
import { useCompanyStore } from '@/stores/companyStore'
import { useUserStore }    from '@/stores/userStore'
import ApplicationsChart   from '@/components/ApplicationsChart.vue'
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  components: { ApplicationsChart },
  name: 'CompanyDashboard',
  setup() {
    return {
      companyStore: useCompanyStore(),
      userStore:    useUserStore(),
    }
  },
  data: () => ({ activeTab: 'active' }),
  computed: {
    tabs() {
      const s = this.companyStore
      return [
        { key: 'active',    label: 'Active',    count: s.activeDrives.length },
        { key: 'all',       label: 'All',        count: s.drives.length },
        { key: 'closed',    label: 'Closed',     count: s.closedDrives.length },
        { key: 'completed', label: 'Completed',  count: s.completedDrives.length },
      ]
    },
    displayedDrives() {
      const s = this.companyStore
      return { active: s.activeDrives, all: s.drives, closed: s.closedDrives, completed: s.completedDrives }[this.activeTab] || []
    },
    stats() {
      const s = this.companyStore
      return [
        { label: 'Total Drives',  value: s.drives.length,          bg: 'bg-primary', icon: 'bi-briefcase-fill' },
        { label: 'Active Drives', value: s.activeDrives.length,    bg: 'bg-success',  icon: 'bi-check-circle-fill' },
        { label: 'Applicants',    value: s.totalApplicants,         bg: 'bg-info',     icon: 'bi-people-fill' },
        { label: 'Completed',     value: s.completedDrives.length, bg: 'bg-warning',  icon: 'bi-trophy-fill' },
      ]
    },
  },
  async mounted() {
    const cid = this.userStore.companyId
    await this.companyStore.fetchProfile(cid)
    if (this.companyStore.isApproved) await this.companyStore.fetchDrives(cid)
  },
  methods: {
    async refresh() {
      await this.companyStore.fetchProfile(this.userStore.companyId, true)
    },
    async toggleStatus(driveId) {
      try { await this.companyStore.toggleDriveStatus(this.userStore.companyId, driveId) }
      catch (e) { alert(e.message) }
    },
    formatDate(d) {
      if (!d) return 'N/A'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    progressClass(p) {
      return p < 30 ? 'bg-danger' : p < 70 ? 'bg-warning' : 'bg-success'
    },
    statusBadge(s) {
      const m = {
        Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-primary',
        Applied: 'bg-primary', Shortlisted: 'bg-info', Selected: 'bg-success', Rejected: 'bg-danger',
        total: 'bg-dark',
      }
      return m[s] || 'bg-secondary'
    },
  },
}
</script>

<style scoped>
.stat-card  { padding: 1.2rem 1.5rem; border-radius: 12px; display: flex; align-items: center; gap: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.drive-card { border-left: 4px solid #0d6efd !important; transition: transform .2s; }
.drive-card:hover { transform: translateY(-3px); }
.nav-tabs .nav-link         { color: #6c757d; border: none; border-bottom: 2px solid transparent; }
.nav-tabs .nav-link.active  { color: #0d6efd; border-bottom-color: #0d6efd; background: none; }
</style>