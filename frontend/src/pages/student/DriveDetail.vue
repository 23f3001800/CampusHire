<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:900px">

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="drive">

        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center gap-2
                      shadow-sm mb-3"
               :class="`alert-${toast.type}`">
            <i class="bi flex-shrink-0"
               :class="toast.type === 'success'
                 ? 'bi-check-circle-fill'
                 : 'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1">{{ toast.message }}</span>
            <button class="btn-close"
                    @click="toast.show = false"></button>
          </div>
        </Transition>

        <div class="d-flex align-items-center mb-4">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
        </div>

        <!-- Header card -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between
                        align-items-start flex-wrap gap-3">
              <div class="flex-grow-1">
                <h2 class="fw-bold mb-1">{{ drive.title }}</h2>
                <p class="text-muted mb-2 small">
                  <i class="bi bi-building me-1"></i>
                  {{ drive.company_name }}
                  <span v-if="drive.company_location" class="ms-2">
                    <i class="bi bi-geo-alt me-1"></i>
                    {{ drive.company_location }}
                  </span>
                </p>
                <div class="d-flex flex-wrap gap-1">
                  <span v-if="drive.job_type"
                        class="badge bg-primary bg-opacity-10 text-primary">
                    {{ drive.job_type }}
                  </span>
                  <span v-if="drive.location"
                        class="badge bg-secondary bg-opacity-10 text-secondary">
                    {{ drive.location }}
                  </span>
                  <span v-if="drive.salary_max"
                        class="badge bg-success bg-opacity-10 text-success">
                    {{ formatSalary(drive.salary_max) }}
                  </span>
                  <span v-if="drive.min_cgpa"
                        class="badge bg-info bg-opacity-10 text-info">
                    Min CGPA {{ drive.min_cgpa }}
                  </span>
                  <span :class="drive.status === 'Open'
                    ? 'badge bg-success' : 'badge bg-secondary'">
                    {{ drive.status }}
                  </span>
                </div>
              </div>
              <button class="btn btn-sm flex-shrink-0"
                      :class="store.isDriveSaved(drive.id)
                        ? 'btn-primary' : 'btn-outline-secondary'"
                      @click="toggleSave">
                <i class="bi"
                   :class="store.isDriveSaved(drive.id)
                     ? 'bi-bookmark-fill' : 'bi-bookmark'"></i>
              </button>
            </div>

            <!-- Apply banner -->
            <div class="alert mt-3 mb-0 d-flex
                        align-items-center flex-wrap gap-2"
                 :class="hasApplied ? 'alert-success' : 'alert-info'">
              <i class="bi flex-shrink-0"
                 :class="hasApplied
                   ? 'bi-check-circle-fill'
                   : 'bi-info-circle-fill'"></i>
              <span class="flex-grow-1">{{ applyBannerText }}</span>
              <button v-if="canApply"
                      class="btn btn-sm btn-primary"
                      :disabled="applying"
                      @click="applyNow">
                <span v-if="applying"
                      class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-send me-1"></i>
                {{ applying ? 'Applying…' : 'Apply Now' }}
              </button>
              <router-link
                v-if="!hasApplied && drive.status === 'Open' &&
                      (!store.isProfileComplete || !store.hasResume)"
                to="/student/profile"
                class="btn btn-sm btn-warning">
                <i class="bi bi-person me-1"></i>Complete Profile
              </router-link>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-md-8">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4">

                <h6 class="section-label">Description</h6>
                <p class="text-muted" style="white-space:pre-wrap">
                  {{ drive.description || 'No description provided.' }}
                </p>

                <template v-if="skillList.length">
                  <h6 class="section-label mt-4">Skills Required</h6>
                  <div class="d-flex flex-wrap gap-1">
                    <span v-for="s in skillList" :key="s"
                          class="badge bg-primary
                                 bg-opacity-10 text-primary">
                      {{ s }}
                    </span>
                  </div>
                </template>

                <h6 class="section-label mt-4">Eligible Branches</h6>
                <div v-if="branchList.length"
                     class="d-flex flex-wrap gap-1">
                  <span v-for="b in branchList" :key="b"
                        class="badge bg-info bg-opacity-10 text-info">
                    {{ b }}
                  </span>
                </div>
                <p v-else class="text-muted small">All branches eligible</p>

              </div>
            </div>
          </div>

          <div class="col-md-4 d-flex flex-column gap-3">

            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h6 class="section-label">Important Dates</h6>
                <div class="d-flex flex-column gap-3">
                  <div>
                    <small class="text-muted d-block">
                      Application Deadline
                    </small>
                    <span class="fw-bold"
                          :class="{ 'text-danger': isUrgent }">
                      {{ fmt(drive.application_deadline) }}
                    </span>
                    <span v-if="isUrgent"
                          class="badge bg-danger ms-1">
                      Closing Soon!
                    </span>
                  </div>
                  <div v-if="drive.drive_date">
                    <small class="text-muted d-block">Drive Date</small>
                    <span class="fw-bold">
                      {{ fmt(drive.drive_date) }}
                    </span>
                  </div>
                  <div>
                    <small class="text-muted d-block">Experience</small>
                    <span>
                      {{ drive.experience_required || 'Freshers / Any' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Company — fields from company_fields marshal -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h6 class="section-label">About Company</h6>
                <p class="fw-semibold mb-1">{{ drive.company_name }}</p>
                <p v-if="drive.company_location"
                   class="text-muted small mb-2">
                  <i class="bi bi-geo-alt me-1"></i>
                  {{ drive.company_location }}
                </p>
                <!-- No company_website in drive_fields —
                     link to company page instead -->
                <router-link
                  :to="`/student/companies/${drive.company_id}`"
                  class="btn btn-outline-primary btn-sm w-100">
                  <i class="bi bi-building me-1"></i>
                  View Company Profile
                </router-link>
              </div>
            </div>

            <div class="card border-0 shadow-sm">
              <div class="card-body p-4 text-center">
                <div class="fs-2 fw-bold text-primary">
                  {{ drive.total_applications }}
                </div>
                <small class="text-muted">Total Applicants</small>
              </div>
            </div>

          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute }  from 'vue-router'
import { useUserStore }         from '@/stores/userStore'
import { useStudentStore }      from '@/stores/studentStore'

const router       = useRouter()
const route        = useRoute()
const userStore    = useUserStore()
const store        = useStudentStore()

const driveId = computed(() => parseInt(route.params.driveId))
const drive   = ref(null)
const loading = ref(true)
const applying = ref(false)
const error   = ref('')
const toast   = reactive({ show: false, type: 'success', message: '' })

// ── Derived — no has_applied in marshal, derive from store ────────────────
const hasApplied = computed(() => store.hasApplied(driveId.value))

const canApply = computed(() =>
  !hasApplied.value &&
  drive.value?.status === 'Open' &&
  store.isProfileComplete &&
  store.hasResume
)

const applyBannerText = computed(() => {
  if (hasApplied.value) return 'You have already applied to this drive.'
  if (drive.value?.status !== 'Open')
    return 'This drive is no longer accepting applications.'
  if (!store.isProfileComplete)
    return 'Complete your profile to apply.'
  if (!store.hasResume)
    return 'Upload your resume to apply.'
  return 'You have not applied yet.'
})

// ── Drive utils — inlined, no external composable ─────────────────────────
const isUrgent = computed(() => {
  if (!drive.value?.application_deadline) return false
  const diff = new Date(drive.value.application_deadline) - new Date()
  return diff > 0 && diff <= 3 * 86_400_000
})

// Fields exactly from drive_fields marshal
const skillList = computed(() =>
  drive.value?.skills_required
    ? drive.value.skills_required.split(',').map(s => s.trim()).filter(Boolean)
    : []
)
const branchList = computed(() =>
  drive.value?.eligible_branches
    ? drive.value.eligible_branches.split(',').map(b => b.trim()).filter(Boolean)
    : []
)

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

// ── Load — uses store.fetchDrive → GET /drives/:id ────────────────────────
async function loadDrive() {
  loading.value = true
  error.value   = ''
  try {
    drive.value = await store.fetchDrive(route.params.companyId, driveId.value)
    if (!drive.value) error.value = 'Drive not found.'
  } catch (e) {
    error.value = e?.message ?? 'Failed to load drive.'
  } finally {
    loading.value = false
  }
}

async function applyNow() {
  if (!confirm(`Apply to "${drive.value.title}"?`)) return
  applying.value = true
  try {
    await store.applyToDrive(userStore.studentId, driveId.value)
    showToast('success', 'Application submitted successfully!')
  } catch (e) {
    showToast('danger', e?.message ?? 'Application failed.')
  } finally {
    applying.value = false
  }
}

function toggleSave() {
  store.isDriveSaved(driveId.value)
    ? store.unsaveDrive(driveId.value)
    : store.saveDrive(drive.value)
}

function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

onMounted(async () => {
  await Promise.all([
    loadDrive(),
    store.fetchApplications(userStore.studentId),
  ])
})
</script>

<style scoped>
.section-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6c757d;
  padding-bottom: .5rem; border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
