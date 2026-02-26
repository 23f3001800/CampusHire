<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:760px">

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger" style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3" @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="drive">

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center gap-2 shadow-sm mb-3"
               :class="`alert-${toast.type}`" role="alert">
            <i class="bi flex-shrink-0"
               :class="toast.type==='success'?'bi-check-circle-fill':'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1">{{ toast.message }}</span>
            <button class="btn-close" @click="toast.show=false"></button>
          </div>
        </Transition>

        <div class="d-flex align-items-center mb-4">
          <button class="btn btn-outline-secondary btn-sm" @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
        </div>

        <!-- Shared header card with apply button in slot -->
        <DriveInfoCard :drive="drive">
          <div class="alert mt-3 mb-0 d-flex align-items-center flex-wrap gap-2"
               :class="drive.has_applied ? 'alert-success' : 'alert-info'">
            <i class="bi flex-shrink-0"
               :class="drive.has_applied ? 'bi-check-circle-fill' : 'bi-info-circle-fill'"></i>
            <span class="flex-grow-1">
              {{ drive.has_applied
                  ? 'You have already applied to this drive.'
                  : drive.status !== 'Open'
                    ? 'This drive is no longer accepting applications.'
                    : 'You have not applied yet.' }}
            </span>
            <button v-if="!drive.has_applied && drive.status === 'Open'"
                    class="btn btn-sm btn-primary"
                    :disabled="applying" @click="applyNow">
              <span v-if="applying" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-send me-1"></i>
              {{ applying ? 'Applying…' : 'Apply Now' }}
            </button>
          </div>
        </DriveInfoCard>

        <!-- Body -->
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
                          class="badge bg-primary bg-opacity-10 text-primary">{{ s }}</span>
                  </div>
                </template>
                <h6 class="section-label mt-4">Eligible Branches</h6>
                <div v-if="branchList.length" class="d-flex flex-wrap gap-1">
                  <span v-for="b in branchList" :key="b"
                        class="badge bg-info bg-opacity-10 text-info">{{ b }}</span>
                </div>
                <p v-else class="text-muted small">All branches eligible</p>
              </div>
            </div>
          </div>

          <div class="col-md-4 d-flex flex-column gap-3">
            <!-- Schedule -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h6 class="section-label">Important Dates</h6>
                <div class="d-flex flex-column gap-3">
                  <div>
                    <small class="text-muted d-block">Application Deadline</small>
                    <span class="fw-bold" :class="{'text-danger': isUrgent}">
                      {{ fmt(drive.application_deadline) }}
                    </span>
                    <span v-if="isUrgent" class="badge bg-danger ms-1">Closing Soon!</span>
                  </div>
                  <div>
                    <small class="text-muted d-block">Drive Date</small>
                    <span class="fw-bold">{{ fmt(drive.drive_date) }}</span>
                  </div>
                  <div>
                    <small class="text-muted d-block">Experience</small>
                    <span>{{ drive.experience_required || 'Freshers / Any' }}</span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Company details -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h6 class="section-label">About Company</h6>
                <p class="fw-semibold mb-1">{{ drive.company_name }}</p>
                <a v-if="drive.company_website"
                   :href="drive.company_website" target="_blank"
                   class="btn btn-outline-secondary btn-sm w-100 mt-2">
                  <i class="bi bi-globe me-1"></i>Visit Website
                </a>
                <router-link
                  :to="`/student/companies/${drive.company_id}`"
                  class="btn btn-outline-primary btn-sm w-100 mt-2">
                  <i class="bi bi-building me-1"></i>View Company Details
                </router-link>
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
import { useRouter, useRoute } from 'vue-router'
import { useUserStore }        from '@/stores/userStore'
import { useStudentStore }     from '@/stores/studentStore'
import { useDriveUtils }       from '@/composables/useDriveUtils'
import DriveInfoCard           from '@/components/DriveInfoCard.vue'

const router       = useRouter()
const route        = useRoute()
const userStore    = useUserStore()
const studentStore = useStudentStore()

const driveId = computed(() => parseInt(route.params.driveId))
const drive   = ref(null)
const loading = ref(true)
const applying = ref(false)
const error   = ref('')
const toast   = reactive({ show: false, type: 'success', message: '' })

const { isUrgent, skillList, branchList, fmt } = useDriveUtils(drive)

// ── Load — uses store's existing fetchDrive ────────────────────────────────
async function loadDrive() {
  loading.value = true; error.value = ''
  try {
    drive.value = await studentStore.fetchDrive(driveId.value)
    if (!drive.value) error.value = 'Drive not found or not available.'
  } catch (e) {
    error.value = e?.response?.data?.message ?? e.message ?? 'Failed to load drive.'
  } finally { loading.value = false }
}

// ── Apply ─────────────────────────────────────────────────────────────────────
async function applyNow() {
  if (!confirm(`Apply to "${drive.value.title}"?`)) return
  applying.value = true
  try {
    await studentStore.applyToDrive(userStore.studentId, driveId.value)
    drive.value = {
      ...drive.value,
      has_applied: true,
      total_applications: (drive.value.total_applications ?? 0) + 1,
    }
    showToast('success', 'Application submitted successfully!')
  } catch (e) {
    showToast('danger', e?.response?.data?.message ?? 'Application failed.')
  } finally { applying.value = false }
}

function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

onMounted(loadDrive)
</script>

<style scoped>
.section-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6c757d;
  padding-bottom: .5rem; border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from,   .fade-leave-to     { opacity: 0; }
</style>
