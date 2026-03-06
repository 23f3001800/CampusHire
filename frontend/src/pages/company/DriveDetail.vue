<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:900px">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger" style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3" @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <!-- Content -->
      <template v-else-if="drive">

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center gap-2 shadow-sm mb-3"
               :class="`alert-${toast.type}`" role="alert">
            <i class="bi flex-shrink-0"
               :class="toast.type === 'success'
                 ? 'bi-check-circle-fill'
                 : 'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1">{{ toast.message }}</span>
            <button class="btn-close" @click="toast.show = false"></button>
          </div>
        </Transition>

        <!-- Header -->
        <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
          <button class="btn btn-outline-secondary btn-sm" @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
          <div class="d-flex gap-2 flex-wrap">
            <button class="btn btn-outline-primary btn-sm" @click="toggleEdit">
              <i class="bi" :class="editMode ? 'bi-x-lg' : 'bi-pencil'"></i>
              {{ editMode ? 'Cancel' : 'Edit Drive' }}
            </button>
            <button v-if="!editMode"
                    class="btn btn-sm"
                    :class="drive.status === 'Open' ? 'btn-warning' : 'btn-success'"
                    :disabled="toggling"
                    @click="toggleStatus">
              <span v-if="toggling" class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi me-1"
                 :class="drive.status === 'Open'
                   ? 'bi-toggle-on'
                   : 'bi-toggle-off'"></i>
              {{ drive.status === 'Open' ? 'Close Drive' : 'Reopen Drive' }}
            </button>
            <button v-if="!editMode"
                    class="btn btn-outline-danger btn-sm"
                    @click="confirmDelete">
              <i class="bi bi-trash me-1"></i>Delete
            </button>
          </div>
        </div>

        <!-- VIEW MODE -->
        <template v-if="!editMode">

          <!-- Top section: drive summary -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-3">
                <div class="flex-grow-1">
                  <h3 class="fw-bold mb-1">{{ drive.title }}</h3>
                  <p class="text-muted mb-1 small">
                    <span v-if="drive.job_type">
                      <i class="bi bi-briefcase me-1"></i>{{ drive.job_type }}
                    </span>
                    <span v-if="drive.location" class="ms-3">
                      <i class="bi bi-geo-alt me-1"></i>{{ drive.location }}
                    </span>
                  </p>
                  <p class="mb-0 small text-muted">
                    <span>
                      <strong>Salary:</strong> {{ salaryText(drive) }}
                    </span>
                    <span class="ms-3">
                      <strong>Min CGPA:</strong> {{ drive.min_cgpa ?? 'N/A' }}
                    </span>
                    <span class="ms-3">
                      <strong>Grad Year:</strong> {{ drive.eligible_graduation_year ?? 'Any' }}
                    </span>
                  </p>
                </div>
                <div class="d-flex flex-column align-items-end gap-2">
                  <span class="badge" :class="statusBadge(drive.status)">
                    {{ drive.status }}
                  </span>
                  <span class="badge"
                        :class="approvalBadge(drive.admin_approval_status)">
                    {{ drive.admin_approval_status || 'Pending' }}
                  </span>
                  <span class="badge bg-light text-dark">
                    Applicants: {{ drive.total_applications ?? 0 }}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Pipeline stats + mini chart -->
          <div class="row g-3 mb-4">
            <div class="col-md-7">
              <div class="row g-3">
                <div class="col-6 col-md-3" v-for="s in appStats" :key="s.label">
                  <div class="card border-0 shadow-sm text-center py-3 h-100">
                    <div class="fw-bold fs-4" :class="s.color">{{ s.value }}</div>
                    <small class="text-muted">{{ s.label }}</small>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-5">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-header bg-white border-bottom py-2">
                  <small class="fw-semibold text-muted">
                    <i class="bi bi-graph-up-arrow me-1 text-primary"></i>
                    Pipeline Overview
                  </small>
                </div>
                <div class="card-body">
                  <DoughnutChart
                    :chart-id="`company-drive-pipeline-${driveId}`"
                    :chart-data="pipelineChartData"
                    :chart-options="pipelineChartOptions"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Main body -->
          <div class="row g-4">
            <!-- Left: description, skills, branches -->
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
                            class="badge bg-primary bg-opacity-10 text-primary">
                        {{ s }}
                      </span>
                    </div>
                  </template>

                  <h6 class="section-label mt-4">Eligible Branches</h6>
                  <div v-if="branchList.length" class="d-flex flex-wrap gap-1">
                    <span v-for="b in branchList" :key="b"
                          class="badge bg-info bg-opacity-10 text-info">
                      {{ b }}
                    </span>
                  </div>
                  <p v-else class="text-muted small">All branches eligible</p>
                </div>
              </div>
            </div>

            <!-- Right: schedule + actions -->
            <div class="col-md-4 d-flex flex-column gap-3">
              <div class="card border-0 shadow-sm">
                <div class="card-body p-4">
                  <h6 class="section-label">Schedule</h6>
                  <div class="d-flex flex-column gap-3">
                    <div>
                      <small class="text-muted d-block">Application Deadline</small>
                      <span class="fw-bold" :class="{'text-danger': urgent}">
                        {{ fmt(drive.application_deadline) }}
                      </span>
                      <span v-if="urgent" class="badge bg-danger ms-1">Urgent</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Drive Date</small>
                      <span class="fw-bold">{{ fmt(drive.drive_date) }}</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Posted</small>
                      <span>{{ fmt(drive.posted_date) }}</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Experience</small>
                      <span>{{ drive.experience_required || 'Freshers / Any' }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div class="card border-0 shadow-sm">
                <div class="card-body p-3 d-grid gap-2">
                  <router-link
                    :to="`/company/drives/${drive.id}/applicants`"
                    class="btn btn-primary">
                    <i class="bi bi-people me-2"></i>View Applicants
                    <span class="badge bg-white text-primary ms-1">
                      {{ drive.total_applications ?? 0 }}
                    </span>
                  </router-link>
                  <router-link
                    :to="`/company/${userStore.companyId}`"
                    class="btn btn-outline-secondary">
                    <i class="bi bi-house-door me-2"></i>Back to Dashboard
                  </router-link>
                </div>
              </div>
            </div>
          </div>
        </template>

        <!-- EDIT MODE -->
        <div v-else class="card border-0 shadow-sm">
          <div class="card-body p-4">
            <h5 class="fw-bold mb-4">
              <i class="bi bi-pencil-square me-2 text-primary"></i>Edit Drive
            </h5>
            <form @submit.prevent="saveEdit" novalidate>
              <div class="row g-3">

                <div class="col-12">
                  <label class="form-label fw-semibold">
                    Title <span class="text-danger">*</span>
                  </label>
                  <input v-model.trim="form.title" class="form-control"
                         :class="{'is-invalid': errors.title}" maxlength="150" />
                  <div class="invalid-feedback">{{ errors.title }}</div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">Job Type</label>
                  <select class="form-select" v-model="form.job_type">
                    <option value="">— Select —</option>
                    <option>Full-time</option>
                    <option>Internship</option>
                    <option>Contract</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Location</label>
                  <input v-model.trim="form.location" class="form-control" maxlength="255" />
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-semibold">Currency</label>
                  <select class="form-select" v-model="form.currency">
                    <option value="INR">INR ₹</option>
                    <option value="USD">USD $</option>
                  </select>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold">Min Salary</label>
                  <input v-model.number="form.salary_min" class="form-control"
                         type="number" min="0" />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold">Max Salary</label>
                  <input v-model.number="form.salary_max" class="form-control"
                         :class="{'is-invalid': errors.salary_max}"
                         type="number" min="0" />
                  <div class="invalid-feedback">{{ errors.salary_max }}</div>
                </div>

                <div class="col-md-4">
                  <label class="form-label fw-semibold">Min CGPA</label>
                  <input v-model.number="form.min_cgpa" class="form-control"
                         :class="{'is-invalid': errors.min_cgpa}"
                         type="number" min="0" max="10" step="0.1" />
                  <div class="invalid-feedback">{{ errors.min_cgpa }}</div>
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold">Grad Year</label>
                  <input v-model.number="form.eligible_graduation_year"
                         class="form-control" type="number"
                         :min="new Date().getFullYear()" />
                </div>
                <div class="col-md-4">
                  <label class="form-label fw-semibold">Experience</label>
                  <input v-model.trim="form.experience_required"
                         class="form-control" maxlength="100" />
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold">Eligible Branches</label>
                  <input v-model.trim="form.eligible_branches" class="form-control"
                         placeholder="CSE, ECE, IT" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-semibold">Skills Required</label>
                  <input v-model.trim="form.skills_required" class="form-control"
                         placeholder="Python, Django, SQL" />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">Application Deadline</label>
                  <input v-model="form.application_deadline" class="form-control"
                         :class="{'is-invalid': errors.application_deadline}"
                         type="datetime-local" />
                  <div class="invalid-feedback">{{ errors.application_deadline }}</div>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-semibold">Drive Date</label>
                  <input v-model="form.drive_date" class="form-control"
                         :class="{'is-invalid': errors.drive_date}"
                         type="datetime-local" />
                  <div class="invalid-feedback">{{ errors.drive_date }}</div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold">Description</label>
                  <textarea v-model.trim="form.description" class="form-control"
                            rows="5" maxlength="5000"></textarea>
                  <div class="form-text text-end">
                    {{ (form.description || '').length }}/5000
                  </div>
                </div>

              </div>
              <div class="d-flex gap-2 justify-content-end mt-4 pt-3 border-top">
                <button type="button" class="btn btn-outline-secondary"
                        @click="cancelEdit">
                  Cancel
                </button>
                <button type="submit" class="btn btn-primary px-5" :disabled="saving">
                  <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                  {{ saving ? 'Saving…' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/userStore'
import { useCompanyStore } from '@/stores/companyStore'
// import DoughnutChart from '@/components/charts/DoughnutChart.vue'

const router       = useRouter()
const route        = useRoute()
const userStore    = useUserStore()
const companyStore = useCompanyStore()

const driveId  = computed(() => parseInt(route.params.driveId))
const drive    = ref(null)
const loading  = ref(true)
const saving   = ref(false)
const toggling = ref(false)
const editMode = ref(false)
const error    = ref('')
const form     = ref({})
const errors   = ref({})
const toast    = reactive({ show: false, type: 'success', message: '' })

// salary formatting similar to dashboard
function salaryText(d) {
  if (!d.salary_min && !d.salary_max) return 'Not specified'
  const sym = d.currency === 'INR' ? '₹' : (d.currency || '')
  const fmt = v => {
    if (!v && v !== 0) return ''
    return v >= 100000
      ? `${sym}${(v / 100000).toFixed(1)}L`
      : `${sym}${v.toLocaleString('en-IN')}`
  }
  if (d.salary_min && d.salary_max) {
    return `${fmt(d.salary_min)}–${fmt(d.salary_max)}`
  }
  return fmt(d.salary_min || d.salary_max)
}

function fmt(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

const urgent = computed(() => {
  if (!drive.value?.application_deadline) return false
  const diff = new Date(drive.value.application_deadline) - new Date()
  return diff > 0 && diff < 3 * 86_400_000
})

function statusBadge(s) {
  return {
    Open: 'bg-success',
    Closed: 'bg-secondary',
    Completed: 'bg-primary',
  }[s] || 'bg-secondary'
}

function approvalBadge(s) {
  return {
    Pending: 'bg-warning text-dark',
    Approved: 'bg-success',
    Rejected: 'bg-danger',
  }[s] || 'bg-secondary'
}

// skills / branches lists
const skillList = computed(() =>
  (drive.value?.skills_required || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
)

const branchList = computed(() =>
  (drive.value?.eligible_branches || '')
    .split(',')
    .map(b => b.trim())
    .filter(Boolean)
)

// applicant stats from companyStore
const appStats = computed(() => {
  const s = companyStore.getDriveStats(driveId.value) ?? {}
  return [
    { label: 'Applied',     value: s.applied     ?? 0, color: 'text-primary' },
    { label: 'Shortlisted', value: s.shortlisted ?? 0, color: 'text-info' },
    { label: 'Selected',    value: s.selected    ?? 0, color: 'text-success' },
    { label: 'Rejected',    value: s.rejected    ?? 0, color: 'text-danger' },
  ]
})

// small pipeline chart
const pipelineChartData = computed(() => {
  const s = companyStore.getDriveStats(driveId.value) ?? {}
  return {
    labels: ['Applied', 'Shortlisted', 'Selected', 'Rejected'],
    datasets: [
      {
        data: [
          s.applied     ?? 0,
          s.shortlisted ?? 0,
          s.selected    ?? 0,
          s.rejected    ?? 0,
        ],
        backgroundColor: ['#0d6efd', '#0dcaf0', '#198754', '#dc3545'],
      },
    ],
  }
})

const pipelineChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { position: 'bottom', labels: { usePointStyle: true } },
  },
}

// load drive + applicants
async function loadDrive() {
  loading.value = true
  error.value   = ''
  try {
    await companyStore.fetchDrives(userStore.companyId)
    drive.value = companyStore.getDriveById(driveId.value)
    if (!drive.value) {
      error.value = 'Drive not found.'
      return
    }
    companyStore
      .fetchApplicants(userStore.companyId, driveId.value)
      .catch(() => {})
    initForm()
  } catch (e) {
    error.value = e?.message ?? 'Failed to load drive.'
  } finally {
    loading.value = false
  }
}

// edit helpers
function initForm() {
  const d = drive.value
  const toLocal = iso => (iso ? iso.slice(0, 16) : '')
  form.value = {
    title:                     d.title                     ?? '',
    job_type:                  d.job_type                  ?? '',
    location:                  d.location                  ?? '',
    description:               d.description               ?? '',
    currency:                  d.currency                  ?? 'INR',
    salary_min:                d.salary_min                ?? null,
    salary_max:                d.salary_max                ?? null,
    min_cgpa:                  d.min_cgpa                  ?? null,
    eligible_graduation_year:  d.eligible_graduation_year  ?? null,
    eligible_branches:         d.eligible_branches         ?? '',
    skills_required:           d.skills_required           ?? '',
    experience_required:       d.experience_required       ?? '',
    application_deadline:      toLocal(d.application_deadline),
    drive_date:                toLocal(d.drive_date),
  }
}

function toggleEdit() {
  if (editMode.value) {
    cancelEdit()
  } else {
    initForm()
    errors.value = {}
    editMode.value = true
  }
}

function cancelEdit() {
  editMode.value = false
  errors.value   = {}
}

function validate() {
  const e = {}
  const f = form.value
  if (!f.title?.trim()) e.title = 'Title is required.'
  if (f.min_cgpa != null && (f.min_cgpa < 0 || f.min_cgpa > 10))
    e.min_cgpa = 'CGPA must be between 0 and 10.'
  if (f.salary_min && f.salary_max && Number(f.salary_min) > Number(f.salary_max))
    e.salary_max = 'Max salary must be greater than or equal to min salary.'
  if (f.application_deadline && f.drive_date &&
      new Date(f.drive_date) < new Date(f.application_deadline))
    e.drive_date = 'Drive date must be after application deadline.'
  errors.value = e
  return !Object.keys(e).length
}

async function saveEdit() {
  if (!validate()) return
  saving.value = true
  try {
    const payload = { ...form.value }
    if (payload.application_deadline)
      payload.application_deadline = new Date(payload.application_deadline).toISOString()
    if (payload.drive_date)
      payload.drive_date = new Date(payload.drive_date).toISOString()
    Object.keys(payload).forEach(k => {
      if (payload[k] === '' || payload[k] === null) delete payload[k]
    })
    const updated = await companyStore.updateDrive(
      userStore.companyId,
      driveId.value,
      payload,
    )
    drive.value = { ...drive.value, ...updated }
    editMode.value = false
    showToast('success', 'Drive updated successfully.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save changes.')
  } finally {
    saving.value = false
  }
}

// status toggle
async function toggleStatus() {
  toggling.value = true
  try {
    const updated = await companyStore.toggleDriveStatus(
      userStore.companyId,
      driveId.value,
    )
    drive.value = { ...drive.value, status: updated.status }
    showToast('success', `Drive is now ${drive.value.status}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to update status.')
  } finally {
    toggling.value = false
  }
}

// delete
async function confirmDelete() {
  if (!confirm('Permanently delete this drive and all its applications?')) return
  try {
    await companyStore.deleteDrive(userStore.companyId, driveId.value)
    alert("drive deleted successfully")
    router.replace(`/company/${userStore.companyId}`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to delete drive.')
  }
}

// toast
function showToast(type, message, ms = 4000) {
  toast.show   = true
  toast.type   = type
  toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

onMounted(loadDrive)
</script>

<style scoped>
.section-label {
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #6c757d;
  padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
