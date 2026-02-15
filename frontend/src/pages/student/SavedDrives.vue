<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">Saved Drives</h3>
          <small class="text-muted">{{ store.savedDrives.length }} bookmarked</small>
        </div>
        <router-link :to="{ name: 'StudentDashboard', params: { id: userStore.studentId } }"
          class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <div v-if="!store.savedDrives.length" class="text-center py-5">
        <i class="bi bi-bookmark fs-1 text-muted d-block mb-2"></i>
        <p class="text-muted mb-3">No saved drives yet. Bookmark drives while browsing to see them here.</p>
        <router-link :to="{ name: 'StudentDashboard', params: { id: userStore.studentId } }"
          class="btn btn-primary px-4">Browse Drives</router-link>
      </div>

      <div v-else class="row g-3">
        <div v-for="drive in store.savedDrives" :key="drive.id" class="col-md-6">
          <div class="card border-0 shadow-sm h-100 drive-card">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-2">
                <div class="flex-grow-1 pe-2">
                  <h6 class="fw-bold mb-1">{{ drive.title }}</h6>
                  <small class="text-muted">
                    <i class="bi bi-building me-1"></i>{{ drive.company_name }}
                  </small>
                </div>
                <button class="btn btn-sm btn-outline-secondary border-0" @click="store.unsaveDrive(drive.id)">
                  <i class="bi bi-bookmark-fill text-warning"></i>
                </button>
              </div>

              <div class="d-flex flex-wrap gap-1 mb-3">
                <span class="badge bg-light text-dark border">{{ drive.location || 'Remote' }}</span>
                <span class="badge bg-light text-dark border">{{ drive.job_type || 'Full-time' }}</span>
                <span v-if="drive.salary_max" class="badge bg-success text-white">
                  {{ formatSalary(drive.salary_max) }}
                </span>
                <span v-if="drive.min_cgpa" class="badge bg-info text-white">
                  CGPA {{ drive.min_cgpa }}+
                </span>
              </div>

              <div class="d-flex justify-content-between align-items-center">
                <small :class="isUrgent(drive.application_deadline) ? 'text-danger fw-bold' : 'text-muted'">
                  <i class="bi bi-clock me-1"></i>{{ formatDate(drive.application_deadline) }}
                  <span v-if="isUrgent(drive.application_deadline)"> · Urgent!</span>
                </small>
                <button class="btn btn-sm"
                  :class="store.hasApplied(drive.id) ? 'btn-outline-success disabled' : 'btn-primary'"
                  @click="apply(drive)">
                  <i class="bi me-1" :class="store.hasApplied(drive.id) ? 'bi-check-circle' : 'bi-send'"></i>
                  {{ store.hasApplied(drive.id) ? 'Applied' : 'Apply Now' }}
                </button>
              </div>
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
  name: 'SavedDrives',
  setup() {
    return { store: useStudentStore(), userStore: useUserStore() }
  },
  async mounted() {
    await this.store.fetchApplications(this.userStore.studentId)
  },
  methods: {
    async apply(drive) {
      if (!this.store.isProfileComplete)
        return this.$router.push({ name: 'StudentProfile' })
      if (!this.store.hasResume) {
        alert('Please upload your resume first')
        return this.$router.push({ name: 'StudentProfile' })
      }
      if (!confirm(`Apply to "${drive.title}"?`)) return
      try { await this.store.applyToDrive(this.userStore.studentId, drive.id) }
      catch (e) { alert(e.message) }
    },
    formatDate(d) {
      return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
    },
    formatSalary(s) {
      return s >= 100000 ? `₹${(s / 100000).toFixed(1)} LPA` : `₹${s.toLocaleString('en-IN')}`
    },
    isUrgent(d) {
      if (!d) return false
      const diff = new Date(d) - new Date()
      return diff > 0 && diff < 3 * 86400000
    },
  },
}
</script>

<style scoped>
.drive-card { border-left: 3px solid #0d6efd !important; transition: transform .15s; }
.drive-card:hover { transform: translateY(-2px); }
</style>