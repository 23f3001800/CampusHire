<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:1100px">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3">Loading applicants…</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else>

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center
                      gap-2 shadow-sm mb-3"
               :class="`alert-${toast.type}`" role="alert">
            <i class="bi flex-shrink-0"
               :class="toast.type === 'success'
                 ? 'bi-check-circle-fill'
                 : 'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1">{{ toast.message }}</span>
            <button class="btn-close"
                    @click="toast.show = false"></button>
          </div>
        </Transition>

        <!-- Header -->
        <div class="d-flex align-items-center
                    justify-content-between mb-4 flex-wrap gap-2">
          <div>
            <button class="btn btn-outline-secondary btn-sm mb-1"
                    @click="router.back()">
              <i class="bi bi-arrow-left me-1"></i>Back to Drive
            </button>
            <h4 class="fw-bold mb-0">
              Applicants — {{ drive?.title || '…' }}
            </h4>
            <small class="text-muted">
              <i class="bi bi-building me-1"></i>
              {{ store.companyName }}
            </small>
          </div>
          <button class="btn btn-outline-secondary btn-sm"
                  :disabled="store.loadingApps"
                  @click="loadApplicants(true)">
            <span v-if="store.loadingApps"
                  class="spinner-border spinner-border-sm"></span>
            <i v-else class="bi bi-arrow-clockwise"></i>
            Refresh
          </button>
        </div>

        <!-- Pipeline stats -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3"
               v-for="s in pipelineStats" :key="s.label">
            <div class="card border-0 shadow-sm text-center py-3
                        h-100 cursor-pointer"
                 :class="{
                   'border-primary border-2':
                     activeFilter === s.key
                 }"
                 @click="setFilter(s.key)">
              <div class="fw-bold fs-3 lh-1" :class="s.color">
                {{ s.value }}
              </div>
              <small class="text-muted mt-1">{{ s.label }}</small>
            </div>
          </div>
        </div>

        <!-- Filters & search -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body py-3">
            <div class="row g-2 align-items-center">
              <div class="col-md-5">
                <div class="input-group input-group-sm">
                  <span class="input-group-text">
                    <i class="bi bi-search"></i>
                  </span>
                  <input class="form-control"
                         v-model="search"
                         placeholder="Search by name, email, branch…" />
                  <button v-if="search"
                          class="btn btn-outline-secondary"
                          @click="search = ''">
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              </div>
              <div class="col-md-3">
                <select class="form-select form-select-sm"
                        v-model="activeFilter">
                  <option value="">All Statuses</option>
                  <option value="Applied">Applied</option>
                  <option value="Shortlisted">Shortlisted</option>
                  <option value="Selected">Selected</option>
                  <option value="Rejected">Rejected</option>
                </select>
              </div>
              <div class="col-md-3">
                <select class="form-select form-select-sm"
                        v-model="sortBy">
                  <option value="applied_date_desc">
                    Newest First
                  </option>
                  <option value="applied_date_asc">
                    Oldest First
                  </option>
                  <option value="cgpa_desc">
                    CGPA High → Low
                  </option>
                  <option value="name_asc">Name A–Z</option>
                </select>
              </div>
              <div class="col-md-1 text-end">
                <small class="text-muted">
                  {{ filtered.length }}
                </small>
              </div>
            </div>
          </div>
        </div>

        <!-- Applicants table -->
        <div class="card border-0 shadow-sm">
          <div class="card-body p-0">

            <div v-if="store.loadingApps" class="text-center py-4">
              <div class="spinner-border spinner-border-sm
                          text-primary"></div>
            </div>

            <div v-else-if="!filtered.length"
                 class="text-center py-5 text-muted">
              <i class="bi bi-people fs-1 d-block mb-2"></i>
              {{
                search || activeFilter
                  ? 'No applicants match your filters.'
                  : 'No applicants yet.'
              }}
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Applicant</th>
                    <th>Branch / CGPA</th>
                    <th>Applied</th>
                    <th>Status</th>
                    <th>Interview</th>
                    <th class="text-end">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in filtered" :key="app.id">

                    <!-- Applicant info -->
                    <td>
                      <router-link
                        :to="`/company/students/${app.student_id}`"
                        class="fw-semibold text-decoration-none
                               text-dark">
                        {{ app.student_name }}
                      </router-link>
                      <div class="small text-muted">
                        {{ app.student_email }}
                      </div>
                      <div v-if="app.student_roll"
                           class="small text-muted">
                        {{ app.student_roll }}
                      </div>
                    </td>

                    <!-- Branch / CGPA -->
                    <td>
                      <span class="badge bg-light text-dark">
                        {{ app.student_branch || '—' }}
                      </span>
                      <div class="small text-muted mt-1">
                        CGPA: {{ app.student_cgpa ?? '—' }}
                      </div>
                    </td>

                    <!-- Applied date -->
                    <td class="small">
                      {{ formatDate(app.applied_date) }}
                    </td>

                    <!-- Status badge -->
                    <td>
                      <span class="badge"
                            :class="statusBadge(app.status)">
                        {{ app.status }}
                      </span>
                      <div v-if="app.reviewed_date"
                           class="small text-muted mt-1">
                        {{ formatDate(app.reviewed_date) }}
                      </div>
                    </td>

                    <!-- Interview indicator -->
                    <td>
                      <span v-if="store.getInterviewForApp(app.id)"
                            class="badge bg-info text-dark">
                        <i class="bi bi-calendar-check me-1"></i>
                        Scheduled
                      </span>
                      <span v-else class="text-muted small">—</span>
                    </td>

                    <!-- Action buttons -->
                    <td class="text-end">
                      <div class="d-flex justify-content-end
                                  gap-1 flex-wrap">

                        <!-- View profile -->
                        <router-link
                          :to="`/company/students/${app.student_id}`"
                          class="btn btn-sm
                                 btn-outline-secondary"
                          title="View Profile">
                          <i class="bi bi-person"></i>
                        </router-link>

                        <!-- Shortlist -->
                        <button
                          v-if="app.status === 'Applied'"
                          class="btn btn-sm btn-outline-info"
                          :disabled="actionPending === app.id"
                          title="Shortlist"
                          @click="updateStatus(
                            app, 'Shortlisted'
                          )">
                          <span v-if="actionPending === app.id"
                                class="spinner-border
                                       spinner-border-sm"></span>
                          <i v-else class="bi bi-person-check"></i>
                        </button>

                        <!-- Schedule Interview -->
                        <button
                          v-if="['Applied','Shortlisted']
                                 .includes(app.status)"
                          class="btn btn-sm btn-outline-primary"
                          :disabled="actionPending === app.id"
                          title="Schedule Interview"
                          @click="openInterviewModal(app)">
                          <i class="bi bi-calendar-event"></i>
                        </button>

                        <!-- Select -->
                        <button
                          v-if="['Shortlisted'].includes(app.status)"
                          class="btn btn-sm btn-outline-success"
                          :disabled="actionPending === app.id"
                          title="Mark Selected"
                          @click="openSelectionModal(app, 'Selected')">
                          <span v-if="actionPending === app.id"
                                class="spinner-border
                                       spinner-border-sm"></span>
                          <i v-else class="bi bi-check-circle"></i>
                        </button>

                        <!-- Reject -->
                        <button
                          v-if="!['Rejected','Selected']
                                  .includes(app.status)"
                          class="btn btn-sm btn-outline-danger"
                          :disabled="actionPending === app.id"
                          title="Reject"
                          @click="rejectApplicant(app)">
                          <i class="bi bi-x-circle"></i>
                        </button>

                        <!-- Notes -->
                        <button
                          class="btn btn-sm btn-outline-secondary"
                          title="Add Note"
                          @click="openNotesModal(app)">
                          <i class="bi bi-chat-left-text"></i>
                        </button>

                      </div>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </template>
    </div>

    <!-- ── Interview Schedule Modal ── -->
    <div v-if="interviewModal.show"
         class="modal-backdrop-custom"
         @click.self="interviewModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom">
          <h6 class="fw-bold mb-0">
            <i class="bi bi-calendar-event me-2 text-primary"></i>
            Schedule Interview —
            {{ interviewModal.app?.student_name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="interviewModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Interview Type <span class="text-danger">*</span>
              </label>
              <select class="form-select form-select-sm"
                      v-model="interviewForm.interview_type">
                <option value="Technical">Technical</option>
                <option value="HR">HR</option>
                <option value="Managerial">Managerial</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Mode <span class="text-danger">*</span>
              </label>
              <select class="form-select form-select-sm"
                      v-model="interviewForm.interview_mode">
                <option value="Online">Online</option>
                <option value="Onsite">Onsite</option>
                <option value="Phone">Phone</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Interview Date & Time
                <span class="text-danger">*</span>
              </label>
              <input class="form-control form-control-sm"
                     type="datetime-local"
                     v-model="interviewForm.interview_date" />
            </div>
            <div v-if="interviewForm.interview_mode === 'Online'"
                 class="col-12">
              <label class="form-label fw-semibold small">
                Meeting Link / URL
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interview_link"
                     placeholder="https://meet.google.com/…" />
            </div>
            <div v-else class="col-12">
              <label class="form-label fw-semibold small">
                Venue / Location
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interview_link"
                     placeholder="Room 101, Block A" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Interviewer Name(s)
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interviewer"
                     placeholder="John Doe, Jane Smith" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Instructions for Candidate
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="interviewForm.instructions"
                        rows="2"
                        placeholder="Bring ID proof, join 5 min early…">
              </textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="interviewModal.show = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="interviewModal.saving"
                  @click="submitInterview">
            <span v-if="interviewModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            <i v-else class="bi bi-calendar-check me-1"></i>
            Schedule
          </button>
        </div>
      </div>
    </div>

    <!-- ── Selection / Rejection Confirmation Modal ── -->
    <div v-if="selectionModal.show"
         class="modal-backdrop-custom"
         @click.self="selectionModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom"
             :class="selectionModal.status === 'Selected'
               ? 'bg-success' : 'bg-danger'">
          <h6 class="fw-bold mb-0 text-white">
            <i class="bi me-2"
               :class="selectionModal.status === 'Selected'
                 ? 'bi-check-circle' : 'bi-x-circle'"></i>
            {{ selectionModal.status === 'Selected'
                ? 'Finalise Selection' : 'Reject Applicant' }} —
            {{ selectionModal.app?.student_name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="selectionModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <div class="row g-3">
            <template v-if="selectionModal.status === 'Selected'">
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                  Offered Salary ({{ selectionForm.currency }})
                </label>
                <input class="form-control form-control-sm"
                       type="number" min="0"
                       v-model.number="selectionForm.salary"
                       :placeholder="
                         drive?.salary_min ?? '500000'
                       " />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                  Joining Date
                </label>
                <input class="form-control form-control-sm"
                       type="date"
                       v-model="selectionForm.joining_date" />
              </div>
            </template>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Notes / Feedback (optional)
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="selectionForm.notes"
                        rows="2"
                        placeholder="Internal notes…">
              </textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="selectionModal.show = false">
            Cancel
          </button>
          <button class="btn btn-sm px-4"
                  :class="selectionModal.status === 'Selected'
                    ? 'btn-success' : 'btn-danger'"
                  :disabled="selectionModal.saving"
                  @click="submitSelection">
            <span v-if="selectionModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            <i v-else class="bi me-1"
               :class="selectionModal.status === 'Selected'
                 ? 'bi-check-circle' : 'bi-x-circle'"></i>
            Confirm {{ selectionModal.status }}
          </button>
        </div>
      </div>
    </div>

    <!-- ── Notes Modal ── -->
    <div v-if="notesModal.show"
         class="modal-backdrop-custom"
         @click.self="notesModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom">
          <h6 class="fw-bold mb-0">
            <i class="bi bi-chat-left-text me-2
                       text-primary"></i>
            Notes — {{ notesModal.app?.student_name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="notesModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <textarea class="form-control"
                    v-model="notesModal.text"
                    rows="4"
                    placeholder="Internal recruiter notes…">
          </textarea>
          <div v-if="notesModal.app?.notes"
               class="mt-2 text-muted small">
            <strong>Saved:</strong> {{ notesModal.app.notes }}
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="notesModal.show = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="notesModal.saving"
                  @click="saveNotes">
            <span v-if="notesModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            Save Notes
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute }  from 'vue-router'
import { useCompanyStore }      from '@/stores/companyStore'
import { useUserStore }         from '@/stores/userStore'

const router    = useRouter()
const route     = useRoute()
const store     = useCompanyStore()
const userStore = useUserStore()

const driveId = computed(() => parseInt(route.params.driveId))
const cid     = computed(() => userStore.companyId)

// ── Local state ────────────────────────────────────────────────────────────
const loading      = ref(true)
const error        = ref('')
const drive        = ref(null)
const search       = ref('')
const activeFilter = ref('')
const sortBy       = ref('applied_date_desc')
const actionPending = ref(null)   // applicationId being actioned
const toast        = reactive({ show: false, type: 'success', message: '' })

// Modal state
const interviewModal = reactive({
  show: false, saving: false, app: null,
})
const interviewForm = reactive({
  interview_type: 'Technical',
  interview_mode: 'Online',
  interview_date: '',
  interview_link: '',
  interviewer:    '',
  instructions:   '',
})

const selectionModal = reactive({
  show: false, saving: false,
  app: null, status: 'Selected',
})
const selectionForm  = reactive({
  salary: null, joining_date: '',
  notes: '', currency: 'INR',
})

const notesModal = reactive({
  show: false, saving: false, app: null, text: '',
})

// ── Computed list ──────────────────────────────────────────────────────────
const filtered = computed(() => {
  let list = [...(store.applicants[driveId.value] || [])]

  // Status filter
  if (activeFilter.value) {
    list = list.filter(a => a.status === activeFilter.value)
  }
  // Search
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.student_name?.toLowerCase().includes(q) ||
      a.student_email?.toLowerCase().includes(q) ||
      a.student_branch?.toLowerCase().includes(q) ||
      a.student_roll?.toLowerCase().includes(q)
    )
  }
  // Sort
  const sorters = {
    applied_date_desc: (a, b) =>
      new Date(b.applied_date) - new Date(a.applied_date),
    applied_date_asc:  (a, b) =>
      new Date(a.applied_date) - new Date(b.applied_date),
    cgpa_desc: (a, b) =>
      (b.student_cgpa ?? 0) - (a.student_cgpa ?? 0),
    name_asc:  (a, b) =>
      (a.student_name ?? '').localeCompare(b.student_name ?? ''),
  }
  if (sorters[sortBy.value]) list.sort(sorters[sortBy.value])
  return list
})

// Pipeline summary (uses live filtered data per status)
const pipelineStats = computed(() => {
  const all = store.applicants[driveId.value] || []
  const count = s => all.filter(a => a.status === s).length
  return [
    {
      key: '',        label: 'Total',
      value: all.length, color: 'text-dark',
    },
    {
      key: 'Applied', label: 'Applied',
      value: count('Applied'), color: 'text-primary',
    },
    {
      key: 'Shortlisted', label: 'Shortlisted',
      value: count('Shortlisted'), color: 'text-info',
    },
    {
      key: 'Selected', label: 'Selected',
      value: count('Selected'), color: 'text-success',
    },
  ]
})

// ── Load ───────────────────────────────────────────────────────────────────
async function loadApplicants(force = false) {
  loading.value = true
  error.value   = ''
  try {
    // Ensure drive list is loaded so we can show the drive title
    await store.fetchDrives(cid.value)
    drive.value = store.getDriveById(driveId.value)
    // Fetch applicants
    await store.fetchApplicants(cid.value, driveId.value, force)
    // Set currency from drive
    if (drive.value?.currency) {
      selectionForm.currency = drive.value.currency
    }
  } catch (e) {
    error.value = e?.message ?? 'Failed to load applicants.'
  } finally {
    loading.value = false
  }
}

// ── Filter pill click ──────────────────────────────────────────────────────
function setFilter(key) {
  activeFilter.value = activeFilter.value === key ? '' : key
}

// ── Status update (Shortlist) ──────────────────────────────────────────────
// PUT /company/:cid/drives/:did/applicants/:aid  { status, notes? }
async function updateStatus(app, status) {
  actionPending.value = app.id
  try {
    await store.updateApplicationStatus(
      cid.value, driveId.value, app.id, status
    )
    showToast('success', `${app.student_name} ${status.toLowerCase()}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Update failed.')
  } finally {
    actionPending.value = null
  }
}

// ── Reject (inline, no modal) ──────────────────────────────────────────────
async function rejectApplicant(app) {
  if (!confirm(`Reject ${app.student_name}?`)) return
  actionPending.value = app.id
  try {
    // Uses finalizeSelection to align with backend
    // (Creates no Placement record for Rejected)
    await store.finalizeSelection(cid.value, app.id, {
      status: 'Rejected',
    })
    showToast('success', `${app.student_name} rejected.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Rejection failed.')
  } finally {
    actionPending.value = null
  }
}

// ── Interview modal ────────────────────────────────────────────────────────
function openInterviewModal(app) {
  interviewModal.app  = app
  interviewModal.show = true
  // Reset form
  Object.assign(interviewForm, {
    interview_type: 'Technical',
    interview_mode: 'Online',
    interview_date: '',
    interview_link: '',
    interviewer:    '',
    instructions:   '',
  })
}

// POST /company/:cid/applications/:aid/interview
async function submitInterview() {
  if (!interviewForm.interview_date) {
    showToast('danger', 'Interview date is required.')
    return
  }
  interviewModal.saving = true
  try {
    const payload = {
      ...interviewForm,
      interview_date: new Date(
        interviewForm.interview_date
      ).toISOString(),
    }
    await store.scheduleInterview(
      cid.value, interviewModal.app.id, payload
    )
    interviewModal.show = false
    showToast(
      'success',
      `Interview scheduled for ${interviewModal.app.student_name}.`
    )
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to schedule interview.')
  } finally {
    interviewModal.saving = false
  }
}

// ── Selection modal ────────────────────────────────────────────────────────
function openSelectionModal(app, status) {
  selectionModal.app    = app
  selectionModal.status = status
  selectionModal.show   = true
  selectionForm.salary      = drive.value?.salary_min ?? null
  selectionForm.joining_date = ''
  selectionForm.notes        = ''
}

// PUT /company/:cid/applications/:aid/selection
async function submitSelection() {
  selectionModal.saving = true
  try {
    const payload = {
      status:  selectionModal.status,
      notes:   selectionForm.notes || null,
      ...(selectionModal.status === 'Selected' && {
        salary:       selectionForm.salary,
        joining_date: selectionForm.joining_date || null,
        currency:     selectionForm.currency,
      }),
    }
    // Strip nulls
    Object.keys(payload).forEach(
      k => payload[k] === null && delete payload[k]
    )
    await store.finalizeSelection(
      cid.value, selectionModal.app.id, payload
    )
    selectionModal.show = false
    showToast(
      'success',
      `${selectionModal.app.student_name} marked as `
      + `${selectionModal.status.toLowerCase()}.`
    )
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally {
    selectionModal.saving = false
  }
}

// ── Notes modal ────────────────────────────────────────────────────────────
function openNotesModal(app) {
  notesModal.app  = app
  notesModal.text = app.notes || ''
  notesModal.show = true
}

async function saveNotes() {
  notesModal.saving = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId.value,
      notesModal.app.id,
      notesModal.app.status,    // keep existing status
      notesModal.text
    )
    notesModal.show = false
    showToast('success', 'Notes saved.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save notes.')
  } finally {
    notesModal.saving = false
  }
}

// ── Helpers ────────────────────────────────────────────────────────────────
function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

function statusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}

onMounted(() => loadApplicants())
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
.modal-backdrop-custom {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(0,0,0,.45);
  display: flex; align-items: center; justify-content: center;
  padding: 1rem;
}
.modal-card {
  background: #fff; border-radius: 12px;
  width: 100%; max-width: 540px;
  max-height: 90vh; overflow-y: auto;
}
.modal-header-custom {
  background: #0d6efd; color: #fff;
  padding: 1rem 1.25rem;
  border-radius: 12px 12px 0 0;
  display: flex; align-items: center;
  justify-content: space-between;
}
.modal-body-custom { padding: 1.25rem; }
.modal-footer-custom {
  padding: .75rem 1.25rem;
  border-top: 1px solid #dee2e6;
  display: flex; justify-content: flex-end; gap: .5rem;
}
.table th {
  font-size: .78rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d; white-space: nowrap;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
