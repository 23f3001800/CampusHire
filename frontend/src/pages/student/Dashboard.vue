<template>
  <div class="bg-light min-vh-100 pb-5">

    <!-- Top navbar -->
    <nav class="navbar navbar-expand-lg navbar-white
                bg-white shadow-sm px-3 py-2 mb-4">
    </nav>

    <div class="container" style="max-width:1100px">

      <!-- Welcome + completion banner -->
      <div class="row g-3 mb-4">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <h4 class="fw-bold mb-1">
                Welcome back, {{ firstName }}! 👋
              </h4>
              <p class="text-muted mb-3 small">
                Here's what's happening with your placement journey.
              </p>
              <!-- Quick stats row -->
              <div class="row g-2">
                <div class="col-6 col-md-3"
                     v-for="s in quickStats" :key="s.label">
                  <router-link :to="s.to"
                               class="text-decoration-none">
                    <div class="rounded-3 p-2 text-center"
                         :class="s.bg">
                      <div class="fw-bold fs-4" :class="s.color">
                        {{ s.value }}
                      </div>
                      <small :class="s.color" class="opacity-75">
                        {{ s.label }}
                      </small>
                    </div>
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Profile completion -->
        <div class="col-md-4">
          <div class="card border-0 shadow-sm h-100 border-start border-4"
               :class="store.isProfileComplete
                 ? 'border-success' : 'border-warning'">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between mb-2">
                <small class="fw-bold">Profile Completion</small>
                <small class="fw-bold">
                  {{ store.profileCompletionDetails?.percentage ?? 0 }}%
                </small>
              </div>
              <div class="progress mb-3" style="height:8px">
                <div class="progress-bar"
                     :class="progressBarClass"
                     :style="{
                       width: (store.profileCompletionDetails?.percentage ?? 0) + '%'
                     }">
                </div>
              </div>

              <div v-if="store.missingFieldsWithLabels?.required?.length"
                   class="mb-3">
                <small class="text-danger">
                  Missing:
                  {{
                    store.missingFieldsWithLabels.required
                      .map(f => f.label).join(', ')
                  }}
                </small>
              </div>

              <router-link to="/student/profile"
                           class="btn btn-sm w-100"
                           :class="store.isProfileComplete
                             ? 'btn-outline-success'
                             : 'btn-warning'">
                <i class="bi bi-pencil me-1"></i>
                {{ store.isProfileComplete
                    ? 'View Profile' : 'Complete Profile' }}
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- Urgent drives alert -->
      <div v-if="store.urgentDrives.length"
           class="alert alert-warning d-flex align-items-center
                  gap-2 mb-4 shadow-sm">
        <i class="bi bi-alarm-fill fs-5"></i>
        <div>
          <strong>{{ store.urgentDrives.length }} drive(s)</strong>
          closing within 3 days!
          <router-link :to="`/student/${userStore.studentId}/drives`"
                       class="alert-link ms-1">
            View now →
          </router-link>
        </div>
      </div>

      <!-- Active placement alert -->
      <div v-if="store.hasActivePlacement"
           class="alert alert-success d-flex align-items-center
                  gap-2 mb-4 shadow-sm">
        <i class="bi bi-trophy-fill fs-5"></i>
        <div>
          You have a pending placement offer!
          <router-link
            :to="`/student/${userStore.studentId}/placements`"
            class="alert-link ms-1">
            View offer →
          </router-link>
        </div>
      </div>

      <div class="row g-4">

        <!-- ── LEFT COLUMN ─────────────────────────────────────────── -->
        <div class="col-lg-8">

          <!-- Drive filters -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-3">
              <div class="d-flex flex-wrap gap-2">
                <div class="input-group flex-grow-1"
                     style="min-width:200px;max-width:320px">
                  <span class="input-group-text bg-white">
                    <i class="bi bi-search"></i>
                  </span>
                  <input type="text"
                         class="form-control border-start-0"
                         placeholder="Search drives, companies…"
                         :value="store.filters.search"
                         @input="store.setFilters({
                           search: $event.target.value
                         })" />
                </div>
                <select class="form-select"
                        style="max-width:150px"
                        :value="store.filters.jobType"
                        @change="store.setFilters({
                          jobType: $event.target.value
                        })">
                  <option value="">All Types</option>
                  <option>Full-time</option>
                  <option>Internship</option>
                  <option>Part-time</option>
                  <option>Contract</option>
                </select>
                <select class="form-select"
                        style="max-width:180px"
                        :value="store.filters.sortBy"
                        @change="store.setFilters({
                          sortBy: $event.target.value
                        })">
                  <option value="application_deadline">
                    Deadline First
                  </option>
                  <option value="salary_max">Highest Salary</option>
                  <option value="posted_date">Newest</option>
                </select>
                <button v-if="store.filters.search ||
                              store.filters.jobType"
                        class="btn btn-outline-secondary btn-sm"
                        @click="store.clearFilters()">
                  <i class="bi bi-x me-1"></i>Clear
                </button>
                <button class="btn btn-outline-primary btn-sm ms-auto"
                        @click="store.fetchEligibleDrives(
                          userStore.studentId, true
                        )">
                  <i class="bi bi-arrow-repeat"></i>
                </button>
              </div>
            </div>
          </div>

          <!-- Loading drives -->
          <div v-if="store.loadingDrives" class="text-center py-5">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted small">Loading drives…</p>
          </div>

          <!-- No drives -->
          <div v-else-if="!store.filteredEligibleDrives.length"
               class="text-center py-5">
            <i class="bi bi-briefcase fs-1 text-muted d-block mb-2"></i>
            <p class="text-muted">
              {{ store.eligibleDrives.length
                  ? 'No drives match your filters'
                  : 'No eligible drives right now' }}
            </p>
            <button v-if="store.filters.search || store.filters.jobType"
                    class="btn btn-outline-secondary btn-sm mt-2"
                    @click="store.clearFilters()">
              Clear Filters
            </button>
          </div>

          <!-- Drive cards -->
          <div v-else class="d-flex flex-column gap-3">
            <div v-for="drive in store.filteredEligibleDrives"
                 :key="drive.id"
                 class="card border-0 shadow-sm drive-card">
              <div class="card-body p-4">

                <div class="d-flex justify-content-between
                            align-items-start flex-wrap gap-2">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <h5 class="fw-bold mb-0">{{ drive.title }}</h5>
                      <span v-if="store.hasApplied(drive.id)"
                            class="badge bg-success">Applied</span>
                      <span v-if="isUrgentDrive(drive)"
                            class="badge bg-danger">
                        <i class="bi bi-alarm me-1"></i>Closing Soon
                      </span>
                    </div>
                    <p class="text-muted mb-2 small">
                      <i class="bi bi-building me-1"></i>
                      {{ drive.company_name }}
                      <span v-if="drive.company_location" class="ms-2">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ drive.company_location }}
                      </span>
                    </p>
                    <!-- Badges -->
                    <div class="d-flex flex-wrap gap-1">
                      <span v-if="drive.job_type"
                            class="badge bg-primary
                                   bg-opacity-10 text-primary">
                        {{ drive.job_type }}
                      </span>
                      <span v-if="drive.salary_max"
                            class="badge bg-success
                                   bg-opacity-10 text-success">
                        {{ formatSalary(drive.salary_max) }}
                      </span>
                      <span v-if="drive.min_cgpa"
                            class="badge bg-info
                                   bg-opacity-10 text-info">
                        Min CGPA {{ drive.min_cgpa }}
                      </span>
                      <span v-if="drive.location"
                            class="badge bg-secondary
                                   bg-opacity-10 text-secondary">
                        {{ drive.location }}
                      </span>
                    </div>
                  </div>

                  <!-- Bookmark -->
                  <button class="btn btn-sm flex-shrink-0"
                          :class="store.isDriveSaved(drive.id)
                            ? 'btn-primary' : 'btn-outline-secondary'"
                          @click="toggleSave(drive)">
                    <i class="bi"
                       :class="store.isDriveSaved(drive.id)
                         ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
                  </button>
                </div>

                <!-- Deadline -->
                <div class="d-flex justify-content-between
                            align-items-center mt-3">
                  <small class="text-muted">
                    <i class="bi bi-calendar-event me-1"></i>
                    Deadline:
                    <span :class="{ 'text-danger fw-bold':
                                    isUrgentDrive(drive) }">
                      {{ fmt(drive.application_deadline) }}
                    </span>
                  </small>
                  <small class="text-muted">
                    <i class="bi bi-people me-1"></i>
                    {{ drive.total_applications }} applicants
                  </small>
                </div>

                <!-- Actions -->
                <div class="d-flex gap-2 mt-3 pt-3 border-top">
                  <router-link
                    :to="`/student/drives/${drive.id}`"
                    class="btn btn-sm btn-outline-primary flex-grow-1">
                    <i class="bi bi-eye me-1"></i>View Details
                  </router-link>
                  <button v-if="!store.hasApplied(drive.id)"
                          class="btn btn-sm btn-primary flex-grow-1"
                          :disabled="applyingId === drive.id"
                          @click="quickApply(drive)">
                    <span v-if="applyingId === drive.id"
                          class="spinner-border
                                 spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-send me-1"></i>
                    {{ applyingId === drive.id
                        ? 'Applying…' : 'Quick Apply' }}
                  </button>
                  <button v-else
                          class="btn btn-sm btn-success flex-grow-1"
                          disabled>
                    <i class="bi bi-check-lg me-1"></i>Applied
                  </button>
                </div>

              </div>
            </div>
          </div>

        </div>

        <!-- ── RIGHT SIDEBAR ──────────────────────────────────────── -->
        <div class="col-lg-4 d-flex flex-column gap-3">

          <!-- Recent applications -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom py-3
                        d-flex justify-content-between
                        align-items-center">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-send me-2 text-primary"></i>
                Recent Applications
              </h6>
              <router-link
                :to="`/student/${userStore.studentId}/applications`"
                class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div v-if="store.loadingApps"
                 class="card-body text-center py-3">
              <div class="spinner-border spinner-border-sm
                          text-primary"></div>
            </div>
            <div v-else-if="!store.recentApplications.length"
                 class="card-body text-center text-muted small py-3">
              No applications yet
            </div>
            <div v-else class="list-group list-group-flush">
              <div v-for="app in store.recentApplications"
                   :key="app.id"
                   class="list-group-item py-2 px-3">
                <div class="d-flex justify-content-between
                            align-items-center">
                  <div>
                    <p class="mb-0 small fw-semibold text-truncate"
                       style="max-width:160px">
                      {{ app.drive_title }}
                    </p>
                    <small class="text-muted">
                      {{ app.company_name }}
                    </small>
                  </div>
                  <span class="badge small"
                        :class="statusClass(app.status)">
                    {{ app.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Saved drives -->
          <div v-if="store.savedDrives.length"
               class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom py-3">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-bookmark me-2 text-warning"></i>
                Saved Drives ({{ store.savedDrives.length }})
              </h6>
            </div>
            <div class="list-group list-group-flush">
              <router-link
                v-for="d in store.savedDrives" :key="d.id"
                :to="`/student/drives/${d.id}`"
                class="list-group-item list-group-item-action py-2 px-3">
                <div class="d-flex justify-content-between
                            align-items-center">
                  <div>
                    <p class="mb-0 small fw-semibold text-truncate"
                       style="max-width:150px">
                      {{ d.title }}
                    </p>
                    <small class="text-muted">{{ d.company_name }}</small>
                  </div>
                  <button class="btn btn-sm p-0 text-danger"
                          @click.prevent="store.unsaveDrive(d.id)">
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </router-link>
            </div>
          </div>

          <!-- Quick links -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom py-3">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-grid me-2"></i>Quick Links
              </h6>
            </div>
            <div class="list-group list-group-flush">
              <router-link
                v-for="link in quickLinks" :key="link.label"
                :to="link.to"
                class="list-group-item list-group-item-action
                       d-flex align-items-center gap-2 py-2 px-3">
                <i class="bi" :class="link.icon + ' text-primary'"></i>
                <span class="small">{{ link.label }}</span>
                <span v-if="link.badge"
                      class="badge ms-auto"
                      :class="link.badgeClass">
                  {{ link.badge }}
                </span>
              </router-link>
            </div>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStudentStore }          from '@/stores/studentStore'
import { useUserStore }             from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

const applyingId = ref(null)

// ── Computed ───────────────────────────────────────────────────────────────
const firstName = computed(() =>
  (userStore.userName || '').split(' ')[0] || 'Student'
)

const progressBarClass = computed(() => {
  const p = store.profileCompletionDetails?.percentage ?? 0
  return p >= 70 ? 'bg-success' : p >= 40 ? 'bg-warning' : 'bg-danger'
})

const quickStats = computed(() => [
  {
    label: 'Eligible Drives',
    value: store.eligibleDrives.length,
    color: 'text-primary',
    bg:    'bg-primary bg-opacity-10',
    to:    `/student/${userStore.studentId}/drives`,
  },
  {
    label: 'Applications',
    value: store.applicationStats.total,
    color: 'text-info',
    bg:    'bg-info bg-opacity-10',
    to:    `/student/${userStore.studentId}/applications`,
  },
  {
    label: 'Selected',
    value: store.applicationStats.selected,
    color: 'text-success',
    bg:    'bg-success bg-opacity-10',
    to:    `/student/${userStore.studentId}/applications`,
  },
  {
    label: 'Placements',
    value: store.placements.length,
    color: 'text-warning',
    bg:    'bg-warning bg-opacity-10',
    to:    `/student/${userStore.studentId}/placements`,
  },
])

const quickLinks = computed(() => [
  {
    label: 'My Applications',
    to:    `/student/${userStore.studentId}/applications`,
    icon:  'bi-send',
    badge: store.applicationStats.shortlisted || null,
    badgeClass: 'bg-info',
  },
  {
    label: 'Placement History',
    to:    `/student/${userStore.studentId}/placements`,
    icon:  'bi-trophy',
    badge: store.hasActivePlacement ? 'New' : null,
    badgeClass: 'bg-success',
  },
  {
    label: 'My Profile',
    to:    '/student/profile',
    icon:  'bi-person',
    badge: store.isProfileComplete ? null : '!',
    badgeClass: 'bg-warning text-dark',
  },
  {
    label: 'Saved Drives',
    to:    `/student/${userStore.studentId}/drives`,
    icon:  'bi-bookmark',
    badge: store.savedDrives.length || null,
    badgeClass: 'bg-secondary',
  },
])

// ── Helpers ────────────────────────────────────────────────────────────────
function isUrgentDrive(drive) {
  if (!drive.application_deadline) return false
  const diff = new Date(drive.application_deadline) - new Date()
  return diff > 0 && diff <= 3 * 86_400_000
}

function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : 'N/A'
}

function formatSalary(s) {
  if (!s) return ''
  return s >= 100_000
    ? `₹${(s / 100_000).toFixed(1)} LPA`
    : `₹${s.toLocaleString('en-IN')}`
}

function statusClass(s) {
  return {
    Applied:     'bg-primary',
    Shortlisted: 'bg-info text-dark',
    Selected:    'bg-success',
    Rejected:    'bg-danger',
  }[s] ?? 'bg-secondary'
}

// ── Actions ────────────────────────────────────────────────────────────────
async function quickApply(drive) {
  if (!store.isProfileComplete) {
    alert('Please complete your profile before applying.')
    return
  }
  if (!store.hasResume) {
    alert('Please upload your resume before applying.')
    return
  }
  applyingId.value = drive.id
  try {
    await store.applyToDrive(userStore.studentId, drive.id)
  } catch (e) {
    alert(e.message ?? 'Application failed')
  } finally {
    applyingId.value = null
  }
}

function toggleSave(drive) {
  store.isDriveSaved(drive.id)
    ? store.unsaveDrive(drive.id)
    : store.saveDrive(drive)
}

function logout() {
  userStore.logout()
}

// ── Mount ──────────────────────────────────────────────────────────────────
onMounted(async () => {
  await Promise.all([
    store.fetchProfile(userStore.studentId),
    store.fetchEligibleDrives(userStore.studentId),
    store.fetchApplications(userStore.studentId),
    store.fetchPlacements(userStore.studentId),
  ])
})
</script>

<style scoped>
.drive-card { transition: transform .15s; }
.drive-card:hover { transform: translateY(-2px); }
</style>
