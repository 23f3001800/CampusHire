<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="$router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="drive">

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center
                      gap-2 shadow-sm mb-3"
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

        <!-- Top bar -->
        <div class="d-flex align-items-center
                    justify-content-between mb-4 flex-wrap gap-2">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="$router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>

          <div class="d-flex gap-2 flex-wrap align-items-center">

            <!-- Approval status badge — always visible for all three states -->
            <span class="badge fs-6 px-3 py-2"
                  :class="approvalBadgeClass(drive.admin_approval_status)">
              <i class="bi me-1"
                 :class="drive.admin_approval_status === 'Approved'
                   ? 'bi-check-circle'
                   : drive.admin_approval_status === 'Rejected'
                   ? 'bi-x-circle'
                   : 'bi-hourglass-split'"></i>
              {{ drive.admin_approval_status }}
            </span>

            <!-- Approve button — shown whenever drive is NOT already Approved -->
            <button v-if="drive.admin_approval_status !== 'Approved'"
                    class="btn btn-success btn-sm"
                    :disabled="approving"
                    @click="setApproval('Approved')">
              <span v-if="approving"
                    class="spinner-border spinner-border-sm me-1">
              </span>
              <i v-else class="bi bi-check-circle me-1"></i>
              Approve
            </button>

            <!-- Reject button — shown whenever drive is NOT already Rejected -->
            <button v-if="drive.admin_approval_status !== 'Rejected'"
                    class="btn btn-outline-danger btn-sm"
                    :disabled="approving"
                    @click="setApproval('Rejected')">
              <span v-if="approving"
                    class="spinner-border spinner-border-sm me-1">
              </span>
              <i v-else class="bi bi-x-circle me-1"></i>
              Reject
            </button>

            <!-- Drive open/closed status badge + toggle button -->
            <span class="badge fs-6 px-3 py-2"
                  :class="statusBadge(drive.status)">
              <i class="bi me-1"
                 :class="drive.status === 'Open'
                   ? 'bi-door-open' : 'bi-door-closed'"></i>
              {{ drive.status }}
            </span>
            <button class="btn btn-outline-secondary btn-sm"
                    :disabled="toggling"
                    @click="toggleStatus">
              <span v-if="toggling"
                    class="spinner-border spinner-border-sm me-1">
              </span>
              <template v-else>
                <i class="bi me-1"
                   :class="drive.status === 'Open'
                     ? 'bi-toggle-on text-success'
                     : 'bi-toggle-off'"></i>
                {{ drive.status === 'Open' ? 'Close' : 'Reopen' }}
              </template>
            </button>

            <button class="btn btn-outline-danger btn-sm"
                    @click="confirmDelete">
              <i class="bi bi-trash me-1"></i>Delete
            </button>
          </div>
        </div>

        <!-- Drive header card -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex justify-content-between
                        align-items-start flex-wrap gap-3">
              <div>
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
                  <span v-if="drive.salary_max"
                        class="badge bg-success bg-opacity-10 text-success">
                    {{ fmtSalary(drive.salary_max) }}
                  </span>
                  <span v-if="drive.min_cgpa"
                        class="badge bg-info bg-opacity-10 text-info">
                    Min CGPA {{ drive.min_cgpa }}
                  </span>
                  <span class="badge"
                        :class="statusBadge(drive.status)">
                    {{ drive.status }}
                  </span>
                </div>
              </div>
              <div class="text-center bg-light rounded-3 p-3">
                <div class="fs-2 fw-bold text-primary">
                  {{ drive.total_applications ?? applicants.length }}
                </div>
                <small class="text-muted">Applicants</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Applicants table -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white border-bottom
                      d-flex justify-content-between
                      align-items-center py-3">
            <h6 class="mb-0 fw-bold">
              <i class="bi bi-people me-2 text-primary"></i>
              Applicants ({{ applicants.length }})
            </h6>
            <div class="d-flex gap-2">
              <!-- Search applicants -->
              <input v-if="applicants.length"
                     v-model="appSearch" type="text"
                     class="form-control form-control-sm"
                     style="max-width:200px"
                     placeholder="Search…" />
              <!-- Refresh re-fetches the whole drive (including its relation) -->
              <button class="btn btn-sm btn-outline-secondary"
                      :disabled="loading"
                      @click="loadDrive">
                <span v-if="loading"
                      class="spinner-border spinner-border-sm"></span>
                <i v-else class="bi bi-arrow-clockwise"></i>
              </button>
            </div>
          </div>
          <div class="card-body p-0">
            <div v-if="loading" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </div>
            <div v-else-if="!applicants.length"
                 class="text-center py-4 text-muted">
              No applicants yet.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Student</th><th>Branch</th>
                    <th>CGPA</th><th>Status</th>
                    <th>Applied</th><th>Resume</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in filteredApplicants" :key="a.id">
                    <td>
                      <router-link
                        :to="`/admin/students/${a.student_id}`"
                        class="fw-semibold text-decoration-none">
                        {{ a.student_name }}
                      </router-link>
                    </td>
                    <td>{{ a.branch || '—' }}</td>
                    <td>
                      <span v-if="a.cgpa" class="badge"
                            :class="cgpaBadge(a.cgpa)">
                        {{ a.cgpa }}
                      </span>
                      <span v-else class="text-muted">—</span>
                    </td>
                    <td>
                      <span class="badge"
                            :class="appStatusBadge(a.status)">
                        {{ a.status }}
                      </span>
                    </td>
                    <td>
                      <small>{{ fmtDate(a.applied_date) }}</small>
                    </td>
                    <td>
                      <a v-if="a.resume_filename"
                         :href="`${apiBase}/api/uploads/resumes/${a.resume_filename}`"
                         target="_blank"
                         class="btn btn-sm btn-outline-primary">
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

        <!-- Description + schedule -->
        <div class="row g-4">
          <div class="col-md-8">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-body p-4">
                <h6 class="section-label">Description</h6>
                <p class="text-muted" style="white-space:pre-wrap">
                  {{ drive.description || 'No description.' }}
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
                <h6 class="section-label">Schedule</h6>
                <div class="d-flex flex-column gap-3">
                  <div>
                    <small class="text-muted d-block">Application Deadline</small>
                    <span class="fw-bold"
                          :class="{
                            'text-danger': isUrgent(drive.application_deadline)
                          }">
                      {{ fmtDate(drive.application_deadline) }}
                    </span>
                    <span v-if="isUrgent(drive.application_deadline)"
                          class="badge bg-danger ms-1">Urgent</span>
                  </div>
                  <div>
                    <small class="text-muted d-block">Drive Date</small>
                    <span class="fw-bold">{{ fmtDate(drive.drive_date) }}</span>
                  </div>
                  <div>
                    <small class="text-muted d-block">Posted</small>
                    <span>{{ fmtDate(drive.posted_date) }}</span>
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

            <div class="card border-0 shadow-sm">
              <div class="card-body p-3 d-grid">
                <router-link
                  :to="`/admin/companies/${drive.company_id}`"
                  class="btn btn-outline-secondary">
                  <i class="bi bi-building me-2"></i>
                  View Company
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
import { useAdminStore }       from '@/stores/adminStore'

const router  = useRouter()
const route   = useRoute()
const store   = useAdminStore()

const apiBase     = import.meta.env.VITE_API_BASE_URL ?? ''
const driveId     = computed(() => parseInt(route.params.driveId))
const companyId   = computed(() => parseInt(route.params.companyId))

const drive    = ref(null)
const loading  = ref(true)
const approving = ref(false)
const toggling  = ref(false)
const error    = ref('')
const appSearch = ref('')
const toast    = reactive({ show: false, type: 'success', message: '' })

// ── Derived ───────────────────────────────────────────────────────────────

// Applicants come directly from the drive relation — no separate store slice needed.
// If your backend returns the field under a different name (e.g. "applicants"),
// update the key below accordingly.
const applicants = computed(() => drive.value?.applications ?? [])

const filteredApplicants = computed(() => {
  if (!appSearch.value) return applicants.value
  const q = appSearch.value.toLowerCase()
  return applicants.value.filter(a =>
    a.student_name?.toLowerCase().includes(q) ||
    a.branch?.toLowerCase().includes(q)
  )
})

const skillList = computed(() =>
  drive.value?.skills_required
    ? drive.value.skills_required
        .split(',').map(s => s.trim()).filter(Boolean)
    : []
)

const branchList = computed(() =>
  drive.value?.eligible_branches
    ? drive.value.eligible_branches
        .split(',').map(b => b.trim()).filter(Boolean)
    : []
)

// ── Load ──────────────────────────────────────────────────────────────────
async function loadDrive() {
  loading.value = true; error.value = ''
  try {
    const result = await store.fetchDrive(driveId.value, companyId.value)
    if (!result) { error.value = 'Drive not found.'; return }

    // structuredClone breaks the shared reference between drive.value and
    // the object inside store.drives[]. Without this, patchDrive's _patch()
    // call does Object.assign(storeObject, serverResponse) which mutates
    // drive.value in place — overwriting fields like `status` with whatever
    // the full server response returned, before the component can do its
    // own surgical merge.
    drive.value = structuredClone(result)
  } catch (e) {
    error.value = e?.message ?? 'Failed to load.'
  } finally {
    loading.value = false
  }
}

// ── Approval ──────────────────────────────────────────────────────────────
async function setApproval(status) {
  if (status === 'Rejected' && !confirm('Reject this drive?')) return
  approving.value = true
  try {
    // Diagnostic: confirm the IDs before the request is sent.
    // If companyId prints as NaN here, your router param name is mismatched.
    console.log('[setApproval] driveId:', driveId.value,
                'companyId:', companyId.value, 'payload:', { admin_approval_status: status })

    await store.patchDrive(
      driveId.value,
      { admin_approval_status: status },
      companyId.value
    )
    // Only update the one field we patched — spreading the full server response
    // would overwrite unrelated fields like `status` with stale DB values.
    drive.value = { ...drive.value, admin_approval_status: status }
    showToast('success', `Drive ${status.toLowerCase()}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally {
    approving.value = false
  }
}

// ── Toggle open / closed ──────────────────────────────────────────────────
// Same pattern — just patching the status field via patchDrive.
async function toggleStatus() {
  const newStatus = drive.value.status === 'Open' ? 'Closed' : 'Open'
  toggling.value = true
  try {
    const updated = await store.patchDrive(
      driveId.value,
      { status: newStatus },
      companyId.value
    )
    // Only apply the toggled field — same reasoning as setApproval above.
    drive.value = { ...drive.value, status: newStatus }
    showToast('success', `Drive is now ${newStatus}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed.')
  } finally {
    toggling.value = false
  }
}

// ── Delete ────────────────────────────────────────────────────────────────
async function confirmDelete() {
  if (!confirm('Permanently delete this drive?')) return
  try {
    await store.deleteDrive(driveId.value, companyId.value)
    router.replace('/admin')
  } catch (e) {
    showToast('danger', e?.message ?? 'Delete failed.')
  }
}

// ── Utilities ─────────────────────────────────────────────────────────────
function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}
function fmtDate(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : '—'
}
function fmtSalary(s) {
  if (!s) return ''
  return s >= 100_000
    ? `₹${(s / 100_000).toFixed(1)} LPA`
    : `₹${s.toLocaleString('en-IN')}`
}
function isUrgent(d) {
  if (!d) return false
  const diff = new Date(d) - new Date()
  return diff > 0 && diff < 3 * 86_400_000
}
function statusBadge(s) {
  return {
    Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-primary',
  }[s] ?? 'bg-secondary'
}
function approvalBadgeClass(s) {
  return {
    Approved: 'bg-success',
    Rejected:  'bg-danger',
    Pending:   'bg-warning text-dark',
  }[s] ?? 'bg-secondary'
}
function appStatusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}
function cgpaBadge(cgpa) {
  return cgpa >= 8
    ? 'bg-success' : cgpa >= 6
    ? 'bg-warning text-dark' : 'bg-danger'
}

onMounted(loadDrive)
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