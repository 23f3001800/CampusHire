<template>
  <div class="dashboard-root min-vh-100 pb-5">
    <div class="container py-4" style="max-width:1100px">

      <!-- ── Toast ─────────────────────────────────────────────── -->
      <Transition name="fade">
        <div v-if="toast.show"
             class="toast-banner alert d-flex align-items-center
                    gap-2 shadow-sm mb-3"
             :class="`alert-${toast.type}`" role="alert">
          <i class="bi flex-shrink-0"
             :class="toast.type === 'success'
               ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'">
          </i>
          <span class="flex-grow-1 fw-semibold small">
            {{ toast.message }}
          </span>
          <button class="btn-close btn-close-sm"
                  @click="toast.show = false"></button>
        </div>
      </Transition>

      <!-- ── Welcome + Stats ───────────────────────────────────── -->
      <div class="row g-3 mb-4">
        <div class="col-md-8">
          <div class="card border-0 shadow-sm h-100">
            <div class="card-body p-4">
              <div class="d-flex align-items-center
                          justify-content-between flex-wrap gap-2 mb-3">
                <div>
                  <h4 class="fw-bold mb-1">
                    Welcome back, {{ firstName }}! 👋
                  </h4>
                  <p class="text-muted mb-0 small">
                    Here's what's happening with your placement journey.
                  </p>
                </div>
              </div>

              <!-- Quick stats -->
              <div class="row g-2">
                <div class="col-6 col-md-3"
                     v-for="s in quickStats" :key="s.label">
                  <router-link :to="s.to" class="text-decoration-none">
                    <div class="stat-card rounded-3 p-3 text-center"
                         :class="s.bg">
                      <div class="fw-bold fs-3 lh-1 mb-1" :class="s.color">
                        {{ s.value }}
                      </div>
                      <small :class="s.color" class="opacity-75 d-block">
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
            <div class="card-body p-4 d-flex flex-column">
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
                       width: (store.profileCompletionDetails?.percentage ?? 0)
                              + '%'
                     }">
                </div>
              </div>

              <div v-if="store.missingFieldsWithLabels?.required?.length"
                   class="mb-3 flex-grow-1">
                <p class="text-muted small mb-1">Missing fields:</p>
                <div class="d-flex flex-wrap gap-1">
                  <span
                    v-for="f in store.missingFieldsWithLabels.required"
                    :key="f.label"
                    class="badge bg-danger bg-opacity-10
                           text-danger small">
                    {{ f.label }}
                  </span>
                </div>
              </div>

              <router-link to="/student/profile"
                           class="btn btn-sm w-100 mt-auto"
                           :class="store.isProfileComplete
                             ? 'btn-outline-success' : 'btn-warning'">
                <i class="bi me-1"
                   :class="store.isProfileComplete
                     ? 'bi-person-check' : 'bi-pencil'"></i>
                {{ store.isProfileComplete
                    ? 'View Profile' : 'Complete Profile' }}
              </router-link>
            </div>
          </div>
        </div>
      </div>

      <!-- ── Alert banners ─────────────────────────────────────── -->
      <div v-if="store.urgentDrives?.length"
           class="alert alert-warning d-flex align-items-center
                  gap-2 mb-3 shadow-sm py-2">
        <i class="bi bi-alarm-fill"></i>
        <div class="small">
          <strong>{{ store.urgentDrives.length }} drive(s)</strong>
          closing within 3 days — check the list below.
        </div>
      </div>

      <div v-if="store.hasActivePlacement"
           class="alert alert-success d-flex align-items-center
                  gap-2 mb-3 shadow-sm py-2">
        <i class="bi bi-trophy-fill"></i>
        <div class="small">
          You have a pending placement offer!
          <!-- FIX: correct route -->
          <router-link to="/student/applications"
                       class="alert-link ms-1">
            View offer →
          </router-link>
        </div>
      </div>

      <div v-if="!store.hasResume"
           class="alert alert-info d-flex align-items-center
                  gap-2 mb-3 shadow-sm py-2">
        <i class="bi bi-info-circle-fill"></i>
        <div class="small">
          Upload your resume to unlock Quick Apply.
          <router-link to="/student/profile" class="alert-link ms-1">
            Go to profile →
          </router-link>
        </div>
      </div>

      <div class="row g-4">

        <!-- ════════ LEFT — Drive listing ════════ -->
        <div class="col-lg-8">

          <!-- Filter bar -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-3">
              <div class="d-flex flex-wrap gap-2 align-items-center">

                <div class="input-group flex-grow-1"
                     style="min-width:180px;max-width:280px">
                  <span class="input-group-text bg-white border-end-0">
                    <i class="bi bi-search text-muted"></i>
                  </span>
                  <input type="text"
                         class="form-control border-start-0 ps-0"
                         placeholder="Search drives, companies…"
                         :value="store.filters.search"
                         @input="store.setFilters({
                           search: $event.target.value
                         })" />
                </div>

                <select class="form-select form-select-sm"
                        style="max-width:140px"
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

                <select class="form-select form-select-sm"
                        style="max-width:160px"
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

                <!--
                  FIX: Toggle to show/hide already-applied drives.
                  Default OFF so list stays focused on actionable drives.
                -->
                <div class="form-check form-switch ms-1 mb-0">
                  <input class="form-check-input" type="checkbox"
                         id="showApplied" v-model="showApplied" />
                  <label class="form-check-label small text-muted"
                         for="showApplied">
                    Show Applied
                  </label>
                </div>

                <button
                  v-if="store.filters.search || store.filters.jobType"
                  class="btn btn-outline-secondary btn-sm"
                  @click="store.clearFilters()">
                  <i class="bi bi-x me-1"></i>Clear
                </button>

                <button class="btn btn-outline-primary btn-sm ms-auto"
                        :disabled="store.loadingDrives"
                        @click="store.fetchEligibleDrives(
                          userStore.studentId, true
                        )">
                  <span v-if="store.loadingDrives"
                        class="spinner-border spinner-border-sm"></span>
                  <i v-else class="bi bi-arrow-repeat"></i>
                </button>
              </div>

              <!-- Applied drives count hint -->
              <div v-if="hiddenAppliedCount > 0 && !showApplied"
                   class="mt-2 pt-2 border-top">
                <small class="text-muted">
                  <i class="bi bi-eye-slash me-1"></i>
                  {{ hiddenAppliedCount }} applied drive(s) hidden.
                  <button
                    class="btn btn-link btn-sm p-0 text-muted
                           text-decoration-underline align-baseline"
                    @click="showApplied = true">
                    Show them
                  </button>
                </small>
              </div>
            </div>
          </div>

          <!-- Loading -->
          <div v-if="store.loadingDrives" class="text-center py-5">
            <div class="spinner-border text-primary"></div>
            <p class="mt-2 text-muted small">Loading drives…</p>
          </div>

          <!-- No results -->
          <div v-else-if="!visibleDrives.length"
               class="text-center py-5">
            <i class="bi bi-briefcase fs-1 text-muted d-block mb-2"></i>
            <p class="text-muted mb-2">
              {{ store.eligibleDrives?.length
                  ? 'No drives match your filters'
                  : 'No eligible drives right now' }}
            </p>
            <div class="d-flex justify-content-center gap-2 flex-wrap">
              <button
                v-if="store.filters.search || store.filters.jobType"
                class="btn btn-outline-secondary btn-sm"
                @click="store.clearFilters()">
                Clear Filters
              </button>
              <button
                v-if="!showApplied && hiddenAppliedCount > 0"
                class="btn btn-outline-primary btn-sm"
                @click="showApplied = true">
                Show Applied ({{ hiddenAppliedCount }})
              </button>
            </div>
          </div>

          <!-- Drive cards -->
          <div v-else class="d-flex flex-column gap-3">
            <div v-for="drive in visibleDrives" :key="drive.id"
                 class="card border-0 shadow-sm drive-card"
                 :class="{
                   'applied-card':
                     store.hasApplied(drive.id),
                   'urgent-card':
                     isUrgentDrive(drive) && !store.hasApplied(drive.id)
                 }">
              <div class="card-body p-4">

                <div class="d-flex justify-content-between
                            align-items-start flex-wrap gap-2">
                  <div class="flex-grow-1">
                    <div class="d-flex align-items-center
                                gap-2 mb-1 flex-wrap">
                      <h5 class="fw-bold mb-0">{{ drive.title }}</h5>
                      <span v-if="store.hasApplied(drive.id)"
                            class="badge bg-success">
                        <i class="bi bi-check-lg me-1"></i>Applied
                      </span>
                      <span
                        v-if="isUrgentDrive(drive) &&
                              !store.hasApplied(drive.id)"
                        class="badge bg-danger">
                        <i class="bi bi-alarm me-1"></i>Closing Soon
                      </span>
                    </div>

                    <p class="text-muted mb-2 small">
                      <router-link
                        :to="`/student/companies/${drive.company_id}`"
                        class="text-muted text-decoration-none company-link">
                        <i class="bi bi-building me-1"></i>
                        {{ drive.company_name }}
                      </router-link>
                      <span v-if="drive.company_location" class="ms-2">
                        <i class="bi bi-geo-alt me-1"></i>
                        {{ drive.company_location }}
                      </span>
                    </p>

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
                            class="badge bg-info bg-opacity-10 text-info">
                        Min CGPA {{ drive.min_cgpa }}
                      </span>
                      <span v-if="drive.location"
                            class="badge bg-secondary
                                   bg-opacity-10 text-secondary">
                        <i class="bi bi-geo me-1"></i>
                        {{ drive.location }}
                      </span>
                    </div>
                  </div>

                  <!-- Bookmark -->
                  <button class="btn btn-sm flex-shrink-0"
                          :class="store.isDriveSaved(drive.id)
                            ? 'btn-primary' : 'btn-outline-secondary'"
                          :title="store.isDriveSaved(drive.id)
                            ? 'Remove bookmark' : 'Save drive'"
                          @click="toggleSave(drive)">
                    <i class="bi"
                       :class="store.isDriveSaved(drive.id)
                         ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
                  </button>
                </div>

                <!-- Deadline + applicant count -->
                <div class="d-flex justify-content-between
                            align-items-center mt-3">
                  <small class="text-muted">
                    <i class="bi bi-calendar-event me-1"></i>
                    Deadline:
                    <span :class="{
                      'text-danger fw-bold':
                        isUrgentDrive(drive) && !store.hasApplied(drive.id)
                    }">
                      {{ fmt(drive.application_deadline) }}
                    </span>
                    <span
                      v-if="isUrgentDrive(drive) &&
                            !store.hasApplied(drive.id)"
                      class="ms-1 text-danger small">
                      ({{ daysLeft(drive.application_deadline) }}d left)
                    </span>
                  </small>
                  <small class="text-muted">
                    <i class="bi bi-people me-1"></i>
                    {{ drive.total_applications ?? 0 }} applicants
                  </small>
                </div>

                <!-- Actions -->
                <div class="d-flex gap-2 mt-3 pt-3 border-top">
                  <!-- FIX: /student/:companyId/drives/:driveId -->
                  <router-link
                    :to="`/student/${drive.company_id}/drives/${drive.id}`"
                    class="btn btn-sm btn-outline-primary flex-grow-1">
                    <i class="bi bi-eye me-1"></i>View Details
                  </router-link>

                  <!-- Not yet applied -->
                  <button v-if="!store.hasApplied(drive.id)"
                          class="btn btn-sm btn-primary flex-grow-1"
                          :disabled="applyingId === drive.id"
                          @click="quickApply(drive)">
                    <span v-if="applyingId === drive.id"
                          class="spinner-border spinner-border-sm me-1">
                    </span>
                    <i v-else class="bi bi-send me-1"></i>
                    {{ applyingId === drive.id ? 'Applying…' : 'Quick Apply' }}
                  </button>

                  <!-- Already applied — show current status -->
                  <button v-else
                          class="btn btn-sm btn-outline-success flex-grow-1"
                          disabled>
                    <i class="bi bi-check-lg me-1"></i>
                    {{ applicationStatusFor(drive.id) || 'Applied' }}
                  </button>
                </div>

              </div>
            </div>

            <p class="text-center text-muted small mt-1">
              Showing {{ visibleDrives.length }} of
              {{ store.filteredEligibleDrives?.length ?? 0 }} drive(s)
              <span v-if="!showApplied && hiddenAppliedCount > 0">
                · {{ hiddenAppliedCount }} applied hidden
              </span>
            </p>
          </div>

        </div>

        <!-- ════════ RIGHT SIDEBAR ════════ -->
        <div class="col-lg-4 d-flex flex-column gap-3">

          <!-- Recent Applications -->
          <div class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom py-3
                        d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-send me-2 text-primary"></i>
                Recent Applications
              </h6>
              <!-- FIX: /student/applications -->
              <router-link to="/student/applications"
                           class="btn btn-sm btn-outline-primary">
                View All
              </router-link>
            </div>
            <div v-if="store.loadingApps"
                 class="card-body text-center py-3">
              <div class="spinner-border spinner-border-sm text-primary">
              </div>
            </div>
            <div v-else-if="!store.recentApplications?.length"
                 class="card-body text-center text-muted small py-3">
              <i class="bi bi-inbox d-block mb-1 fs-4 opacity-50"></i>
              No applications yet
            </div>
            <div v-else class="list-group list-group-flush">
              <div v-for="app in store.recentApplications" :key="app.id"
                   class="list-group-item py-2 px-3">
                <div class="d-flex justify-content-between
                            align-items-center gap-2">
                  <div class="overflow-hidden">
                    <p class="mb-0 small fw-semibold text-truncate">
                      {{ app.drive_title }}
                    </p>
                    <small class="text-muted text-truncate d-block">
                      {{ app.company_name }}
                    </small>
                  </div>
                  <span class="badge flex-shrink-0 small"
                        :class="statusClass(app.status)">
                    {{ app.status }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Saved Drives -->
          <div v-if="store.savedDrives?.length"
               class="card border-0 shadow-sm">
            <div class="card-header bg-white border-bottom py-3
                        d-flex justify-content-between align-items-center">
              <h6 class="mb-0 fw-bold">
                <i class="bi bi-bookmark-fill me-2 text-warning"></i>
                Saved ({{ store.savedDrives.length }})
              </h6>
              <!-- FIX: /student/saved-drives -->
              <router-link to="/student/saved-drives"
                           class="btn btn-sm btn-outline-secondary">
                View All
              </router-link>
            </div>
            <div class="list-group list-group-flush">
              <div v-for="d in store.savedDrives.slice(0, 5)" :key="d.id"
                   class="list-group-item py-2 px-3">
                <div class="d-flex justify-content-between
                            align-items-center gap-2">
                  <div class="overflow-hidden">
                    <!-- FIX: route uses company_id -->
                    <router-link
                      :to="`/student/${d.company_id}/drives/${d.id}`"
                      class="small fw-semibold text-truncate d-block
                             text-decoration-none text-body saved-link">
                      {{ d.title }}
                    </router-link>
                    <small class="text-muted">{{ d.company_name }}</small>
                  </div>
                  <button class="btn btn-sm p-0 text-danger flex-shrink-0"
                          title="Remove bookmark"
                          @click="store.unsaveDrive(d.id)">
                    <i class="bi bi-x-lg"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- Quick Links -->
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
                <i class="bi flex-shrink-0"
                   :class="link.icon + ' text-primary'"></i>
                <span class="small flex-grow-1">{{ link.label }}</span>
                <span v-if="link.badge"
                      class="badge ms-auto flex-shrink-0"
                      :class="link.badgeClass">
                  {{ link.badge }}
                </span>
              </router-link>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════
         APPLY MODAL — cover letter optional
    ══════════════════════════════════════════ -->
    <div v-if="applyModal.show"
         class="modal-backdrop-custom"
         @click.self="closeApplyModal">
      <div class="modal-card shadow-lg">

        <div class="modal-header-custom">
          <div>
            <h6 class="fw-bold mb-0">
              <i class="bi bi-send me-2"></i>Apply — {{ applyModal.drive?.title }}
            </h6>
            <small class="text-white opacity-75">
              {{ applyModal.drive?.company_name }}
            </small>
          </div>
          <button class="btn-close btn-close-white"
                  @click="closeApplyModal"></button>
        </div>

        <div class="modal-body-custom">
          <!-- Drive summary -->
          <div class="d-flex flex-wrap gap-1 mb-3">
            <span v-if="applyModal.drive?.job_type"
                  class="badge bg-primary bg-opacity-10 text-primary">
              {{ applyModal.drive.job_type }}
            </span>
            <span v-if="applyModal.drive?.salary_max"
                  class="badge bg-success bg-opacity-10 text-success">
              {{ formatSalary(applyModal.drive.salary_max) }}
            </span>
            <span v-if="applyModal.drive?.location"
                  class="badge bg-secondary bg-opacity-10 text-secondary">
              <i class="bi bi-geo me-1"></i>{{ applyModal.drive.location }}
            </span>
            <span v-if="applyModal.drive?.application_deadline"
                  class="badge bg-warning bg-opacity-10 text-warning">
              <i class="bi bi-calendar-event me-1"></i>
              Deadline: {{ fmt(applyModal.drive.application_deadline) }}
            </span>
          </div>

          <!-- Cover letter -->
          <label class="form-label fw-semibold small">
            Cover Letter
            <span class="fw-normal text-muted">(optional)</span>
          </label>
          <textarea
            class="form-control form-control-sm"
            rows="6"
            maxlength="2000"
            v-model="applyModal.coverLetter"
            placeholder="Introduce yourself, highlight relevant skills,
explain why you're a great fit for this role…

Leave blank to apply with just your resume."
          ></textarea>
          <div class="d-flex justify-content-between mt-1">
            <small class="text-muted">
              A strong cover letter improves your chances significantly.
            </small>
            <small class="text-muted">
              {{ applyModal.coverLetter.length }} / 2000
            </small>
          </div>
        </div>

        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="closeApplyModal">
            Cancel
          </button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="applyModal.saving"
                  @click="submitApply">
            <span v-if="applyModal.saving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-send me-1"></i>
            {{ applyModal.saving ? 'Applying…' : 'Submit Application' }}
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStudentStore }                    from '@/stores/studentStore'
import { useUserStore }                       from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

// ── Local state ────────────────────────────────────────────────────────────
const applyingId  = ref(null)
const exportBusy  = ref(false)
const showApplied = ref(false)   // default OFF — hide applied drives

const toast = reactive({ show: false, type: 'success', message: '' })

// Cover letter apply modal
const applyModal = reactive({
  show:        false,
  saving:      false,
  drive:       null,    // the drive being applied to
  coverLetter: '',
})

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
    value: store.eligibleDrives?.length ?? 0,
    color: 'text-primary',
    bg:    'bg-primary bg-opacity-10',
    to:    `/student/${userStore.studentId}`,
  },
  {
    label: 'Applications',
    value: store.applicationStats?.total ?? 0,
    color: 'text-info',
    bg:    'bg-info bg-opacity-10',
    to:    '/student/applications',             // FIX
  },
  {
    label: 'Selected',
    value: store.applicationStats?.selected ?? 0,
    color: 'text-success',
    bg:    'bg-success bg-opacity-10',
    to:    '/student/applications',             // FIX
  },
  {
    label: 'Placements',
    value: store.placements?.length ?? 0,
    color: 'text-warning',
    bg:    'bg-warning bg-opacity-10',
    to:    '/student/applications',        // FIX
  },
])

const quickLinks = computed(() => [
  {
    label:      'My Applications',
    to:         '/student/applications',        // FIX
    icon:       'bi-send',
    badge:      store.applicationStats?.shortlisted || null,
    badgeClass: 'bg-info',
  },
  {
    label:      'Placement History',
    to:         '/student/applications',   // FIX
    icon:       'bi-trophy',
    badge:      store.hasActivePlacement ? 'New' : null,
    badgeClass: 'bg-success',
  },
  {
    label:      'My Profile',
    to:         '/student/profile',
    icon:       'bi-person',
    badge:      store.isProfileComplete ? null : '!',
    badgeClass: 'bg-warning text-dark',
  },
  {
    label:      'Saved Drives',
    to:         '/student/saved-drives',        // FIX
    icon:       'bi-bookmark',
    badge:      store.savedDrives?.length || null,
    badgeClass: 'bg-secondary',
  },
])

/**
 * FIX — Applied drives are hidden by default.
 * Toggle showApplied to include them in the listing.
 */
const visibleDrives = computed(() => {
  const base = store.filteredEligibleDrives ?? []
  if (showApplied.value) return base
  return base.filter(d => !store.hasApplied(d.id))
})

const hiddenAppliedCount = computed(() =>
  (store.filteredEligibleDrives ?? [])
    .filter(d => store.hasApplied(d.id)).length
)

// ── Helpers ────────────────────────────────────────────────────────────────
function isUrgentDrive(drive) {
  if (!drive.application_deadline) return false
  const diff = new Date(drive.application_deadline) - new Date()
  return diff > 0 && diff <= 3 * 86_400_000
}

function daysLeft(deadline) {
  if (!deadline) return 0
  return Math.ceil((new Date(deadline) - new Date()) / 86_400_000)
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

function applicationStatusFor(driveId) {
  return store.recentApplications?.find(a => a.drive_id === driveId)
    ?.status ?? null
}

function showToast(type, message, ms = 4000) {
  toast.show = true
  toast.type = type
  toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

// ── Actions ────────────────────────────────────────────────────────────────

// Step 1 — validate then open the cover letter modal
function quickApply(drive) {
  if (!store.isProfileComplete) {
    showToast('warning', 'Please complete your profile before applying.')
    return
  }
  if (!store.hasResume) {
    showToast('warning', 'Please upload your resume before applying.')
    return
  }
  applyModal.drive       = drive
  applyModal.coverLetter = ''
  applyModal.saving      = false
  applyModal.show        = true
}

function closeApplyModal() {
  applyModal.show  = false
  applyModal.drive = null
}

// Step 2 — submit with optional cover letter
async function submitApply() {
  if (!applyModal.drive) return
  applyModal.saving = true
  applyingId.value  = applyModal.drive.id
  try {
    await store.applyToDrive(
      userStore.studentId,
      applyModal.drive.id,
      applyModal.coverLetter.trim() || null   // pass null if blank
    )
    applyModal.show = false
    showToast('success', `Applied to "${applyModal.drive.title}" successfully!`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Application failed. Please try again.')
  } finally {
    applyModal.saving = false
    applyingId.value  = null
  }
}

function toggleSave(drive) {
  if (store.isDriveSaved(drive.id)) {
    store.unsaveDrive(drive.id)
    showToast('success', 'Drive removed from saved.')
  } else {
    store.saveDrive(drive)
    showToast('success', 'Drive saved!')
  }
}

async function triggerExport() {
  exportBusy.value = true
  try {
    await store.startCSVExport(userStore.studentId)
    showToast(
      'success',
      "Export started! You'll receive an email when it's ready."
    )
  } catch (e) {
    showToast('danger', e?.message ?? 'Export failed. Please try again.')
  } finally {
    exportBusy.value = false
  }
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
.dashboard-root {
  background: #f4f6fb;
}
.stat-card {
  transition: transform .15s, box-shadow .15s;
  cursor: pointer;
}
.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,.08);
}
.drive-card {
  transition: transform .15s, box-shadow .15s;
}
.drive-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0,0,0,.08) !important;
}
/* Applied drives get a subtle muted look */
.applied-card {
  border-left: 4px solid #198754 !important;
  opacity: .88;
}
/* Urgent drives get a red left border */
.urgent-card {
  border-left: 4px solid #dc3545 !important;
}
.company-link:hover,
.saved-link:hover {
  color: #0d6efd !important;
  text-decoration: underline !important;
}
.toast-banner {
  border-radius: 10px;
  position: sticky;
  top: 1rem;
  z-index: 100;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }

/* Apply modal */
.modal-backdrop-custom {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(0,0,0,.5);
  display: flex; align-items: center;
  justify-content: center; padding: 1rem;
}
.modal-card {
  background: #fff; border-radius: 14px;
  width: 100%; max-width: 520px;
  max-height: 92vh; overflow-y: auto;
}
.modal-header-custom {
  background: #0d6efd; color: #fff;
  padding: 1rem 1.25rem;
  border-radius: 14px 14px 0 0;
  display: flex; align-items: flex-start;
  justify-content: space-between; gap: .5rem;
  position: sticky; top: 0; z-index: 1;
}
.modal-body-custom  { padding: 1.25rem; }
.modal-footer-custom {
  padding: .75rem 1.25rem;
  border-top: 1px solid #dee2e6;
  display: flex; justify-content: flex-end; gap: .5rem;
  position: sticky; bottom: 0;
  background: #fff; z-index: 1;
}
</style>