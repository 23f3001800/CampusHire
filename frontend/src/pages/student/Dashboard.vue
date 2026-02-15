<template>
  <div class="dashboard bg-light min-vh-100">

    <!-- Profile incomplete banner -->
    <div v-if="!studentStore.isProfileComplete" class="container pt-4">
      <div class="alert alert-warning d-flex justify-content-between align-items-start border-0 shadow-sm">
        <div class="flex-grow-1">
          <div class="d-flex align-items-center mb-2">
            <i class="bi bi-exclamation-triangle-fill fs-4 me-3"></i>
            <div>
              <h6 class="mb-1">Profile {{ studentStore.profileCompletionDetails.percentage }}% Complete</h6>
              <small>Complete your profile to unlock all placement drives</small>
            </div>
          </div>
          <div class="progress mb-2" style="height:8px">
            <div class="progress-bar progress-bar-striped progress-bar-animated"
              :class="progressClass(studentStore.profileCompletionDetails.percentage)"
              :style="{ width: studentStore.profileCompletionDetails.percentage + '%' }">
            </div>
          </div>
          <small v-if="studentStore.missingFieldsWithLabels.required.length" class="text-danger">
            <strong>Missing:</strong>
            {{ studentStore.missingFieldsWithLabels.required.map(f => f.label).join(', ') }}
          </small>
        </div>
        <router-link to="/student/profile" class="btn btn-warning btn-sm ms-3 flex-shrink-0">
          Complete Profile
        </router-link>
      </div>
    </div>

    <!-- Stats -->
    <div class="container pt-4">
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

      <div class="row g-4">
        <!-- Left: drives -->
        <div class="col-lg-8">
          <!-- Filters -->
          <div class="card shadow-sm mb-4 border-0">
            <div class="card-body">
              <div class="row g-2">
                <div class="col-md-6">
                  <div class="input-group">
                    <span class="input-group-text bg-white border-end-0"><i class="bi bi-search"></i></span>
                    <input type="text" class="form-control border-start-0" placeholder="Search drives…"
                      v-model="filters.search" @input="applyFilters" />
                  </div>
                </div>
                <div class="col-md-3">
                  <select class="form-select" v-model="filters.jobType" @change="applyFilters">
                    <option value="">All Types</option>
                    <option>Full-time</option>
                    <option>Internship</option>
                    <option>Contract</option>
                  </select>
                </div>
                <div class="col-md-3">
                  <select class="form-select" v-model="filters.sortBy" @change="applyFilters">
                    <option value="application_deadline">Deadline</option>
                    <option value="salary_max">Salary</option>
                    <option value="posted_date">Newest</option>
                  </select>
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

          <!-- Loading -->
          <div v-if="studentStore.loadingDrives" class="text-center py-5">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted">Loading drives…</p>
          </div>

          <!-- Empty -->
          <div v-else-if="!displayedDrives.length" class="text-center py-5">
            <i class="bi bi-inbox fs-1 text-muted"></i>
            <p class="mt-2 text-muted">No drives found</p>
          </div>

          <!-- Drive cards -->
          <div v-else>
            <div v-for="drive in displayedDrives" :key="drive.id" class="card drive-card shadow-sm mb-3 border-0">
              <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                  <div>
                    <h5 class="mb-1">{{ drive.title }}</h5>
                    <p class="text-muted mb-0 small">
                      <i class="bi bi-building me-1"></i>{{ drive.company_name }}
                    </p>
                  </div>
                  <button class="btn btn-sm"
                    :class="studentStore.isDriveSaved(drive.id) ? 'btn-primary' : 'btn-outline-secondary'"
                    @click="toggleSave(drive)">
                    <i class="bi" :class="studentStore.isDriveSaved(drive.id) ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
                  </button>
                </div>

                <div class="mb-2">
                  <span class="badge bg-light text-dark me-2"><i class="bi bi-geo-alt me-1"></i>{{ drive.location }}</span>
                  <span class="badge bg-light text-dark me-2"><i class="bi bi-briefcase me-1"></i>{{ drive.job_type }}</span>
                  <span v-if="drive.salary_max" class="badge bg-success text-white me-2">
                    <i class="bi bi-currency-rupee"></i>{{ formatSalary(drive.salary_max) }}
                  </span>
                  <span v-if="drive.min_cgpa" class="badge bg-info text-white">
                    Min CGPA {{ drive.min_cgpa }}
                  </span>
                </div>

                <div class="d-flex justify-content-between align-items-center">
                  <small class="text-muted">
                    <i class="bi bi-clock me-1"></i>Deadline: {{ formatDate(drive.application_deadline) }}
                    <span v-if="isUrgent(drive.application_deadline)" class="badge bg-danger ms-1">Urgent</span>
                  </small>
                  <div>
                    <button v-if="studentStore.hasApplied(drive.id)"
                      class="btn btn-sm btn-outline-success" disabled>
                      <i class="bi bi-check-circle me-1"></i>Applied
                    </button>
                    <button v-else class="btn btn-sm btn-primary"
                      @click="apply(drive.id)"
                      :disabled="!studentStore.isProfileComplete || !studentStore.hasResume">
                      <i class="bi bi-send me-1"></i>Apply
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Right: sidebar -->
        <div class="col-lg-4">

          <!-- Application status chart -->
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-white fw-bold border-bottom-2">Application Status</div>
            <div class="card-body">
              <div v-for="s in appStatRows" :key="s.label" class="mb-3">
                <div class="d-flex justify-content-between mb-1">
                  <small>{{ s.label }}</small>
                  <small class="fw-bold">{{ s.value }}</small>
                </div>
                <div class="progress" style="height:5px">
                  <div class="progress-bar" :class="s.color"
                    :style="{ width: pct(s.value, studentStore.applicationStats.total) + '%' }">
                  </div>
                </div>
              </div>
              <router-link to="/student/applications" class="btn btn-outline-primary btn-sm w-100 mt-2">
                View All Applications
              </router-link>
            </div>
          </div>

          <!-- Recent applications -->
          <div class="card shadow-sm border-0 mb-4">
            <div class="card-header bg-white fw-bold">Recent Applications</div>
            <div v-if="!studentStore.recentApplications.length" class="card-body text-center text-muted small py-3">
              No applications yet
            </div>
            <ul v-else class="list-group list-group-flush">
              <li v-for="app in studentStore.recentApplications" :key="app.id"
                class="list-group-item">
                <div class="d-flex justify-content-between">
                  <div>
                    <p class="mb-0 small fw-bold">{{ app.drive_title }}</p>
                    <p class="mb-0 text-muted small">{{ app.company_name }}</p>
                  </div>
                  <span class="badge align-self-start" :class="statusBadge(app.status)">
                    {{ app.status }}
                  </span>
                </div>
              </li>
            </ul>
          </div>

          <!-- Quick actions -->
          <div class="card shadow-sm border-0">
            <div class="card-header bg-white fw-bold">Quick Actions</div>
            <div class="card-body d-grid gap-2">
              <router-link to="/student/profile"      class="btn btn-outline-primary btn-sm"><i class="bi bi-person me-2"></i>Edit Profile</router-link>
              <router-link to="/student/applications" class="btn btn-outline-primary btn-sm"><i class="bi bi-file-text me-2"></i>My Applications</router-link>
              <router-link to="/student/saved-drives" class="btn btn-outline-primary btn-sm"><i class="bi bi-bookmark me-2"></i>Saved Drives</router-link>
            </div>
          </div>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

export default {
  name: 'StudentDashboard',
  setup() {
    return {
      studentStore: useStudentStore(),
      userStore:    useUserStore(),
    }
  },
  data: () => ({
    activeTab: 'all',
    filters:   { search: '', jobType: '', sortBy: 'application_deadline' },
  }),
  computed: {
    tabs() {
      const s = this.studentStore
      return [
        { key: 'all',         label: 'All Drives',   count: s.filteredEligibleDrives.length },
        { key: 'recommended', label: 'Recommended',  count: s.recommendedDrives.length },
        { key: 'urgent',      label: 'Urgent',        count: s.urgentDrives.length },
      ]
    },
    displayedDrives() {
      const s = this.studentStore
      return { all: s.filteredEligibleDrives, recommended: s.recommendedDrives, urgent: s.urgentDrives }[this.activeTab] || []
    },
    stats() {
      const s = this.studentStore
      return [
        { label: 'Open Drives',  value: s.eligibleDrives.length,         bg: 'bg-primary', icon: 'bi-briefcase-fill' },
        { label: 'Applied',      value: s.applicationStats.total,        bg: 'bg-success',  icon: 'bi-file-earmark-text-fill' },
        { label: 'Saved',        value: s.savedDrives.length,            bg: 'bg-info',     icon: 'bi-bookmark-fill' },
        { label: 'Urgent',       value: s.urgentDrives.length,           bg: 'bg-warning',  icon: 'bi-clock-fill' },
      ]
    },
    appStatRows() {
      const st = this.studentStore.applicationStats
      return [
        { label: 'Applied',     value: st.applied,     color: 'bg-primary' },
        { label: 'Shortlisted', value: st.shortlisted, color: 'bg-info' },
        { label: 'Selected',    value: st.selected,    color: 'bg-success' },
        { label: 'Rejected',    value: st.rejected,    color: 'bg-danger' },
      ]
    },
  },
  async mounted() {
    const id = this.userStore.studentId
    await Promise.all([
      this.studentStore.fetchProfile(id),
      this.studentStore.fetchEligibleDrives(id),
      this.studentStore.fetchApplications(id),
    ])
  },
  methods: {
    applyFilters() { this.studentStore.setFilters(this.filters) },

    async apply(driveId) {
      if (!this.studentStore.isProfileComplete) {
        alert('Please complete your profile first'); this.$router.push('/student/profile'); return
      }
      if (!this.studentStore.hasResume) {
        alert('Please upload your resume first'); this.$router.push('/student/profile'); return
      }
      if (!confirm('Apply to this drive?')) return
      try {
        await this.studentStore.applyToDrive(this.userStore.studentId, driveId)
      } catch (e) { alert(e.message) }
    },

    toggleSave(drive) {
      this.studentStore.isDriveSaved(drive.id)
        ? this.studentStore.unsaveDrive(drive.id)
        : this.studentStore.saveDrive(drive)
    },

    formatDate(d) {
      if (!d) return 'N/A'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },
    formatSalary(s) {
      if (!s) return ''
      return s >= 100000 ? (s / 100000).toFixed(1) + ' LPA' : s.toLocaleString('en-IN')
    },
    isUrgent(deadline) {
      if (!deadline) return false
      const diff = new Date(deadline) - new Date()
      return diff > 0 && diff <= 3 * 86400000
    },
    progressClass(p) {
      return p < 30 ? 'bg-danger' : p < 70 ? 'bg-warning' : 'bg-success'
    },
    statusBadge(s) {
      return { Applied: 'bg-primary', Shortlisted: 'bg-info', Selected: 'bg-success', Rejected: 'bg-danger' }[s] || 'bg-secondary'
    },
    pct(v, total) { return total ? Math.round((v / total) * 100) : 0 },
  },
}
</script>

<style scoped>
.stat-card   { padding: 1.2rem 1.5rem; border-radius: 12px; display: flex; align-items: center; gap: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,.1); }
.drive-card  { border-left: 4px solid #0d6efd !important; transition: transform .2s; }
.drive-card:hover { transform: translateY(-3px); box-shadow: 0 6px 16px rgba(0,0,0,.1) !important; }
.nav-tabs .nav-link         { color: #6c757d; border: none; border-bottom: 2px solid transparent; }
.nav-tabs .nav-link.active  { color: #0d6efd; border-bottom-color: #0d6efd; background: none; }
</style>