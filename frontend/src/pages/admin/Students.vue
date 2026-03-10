<template>
  <div class="page-root">

    <!-- ── Toast ─────────────────────────────────────────────── -->
    <Transition name="fade">
      <div v-if="toast.show"
           class="toast-fixed alert d-flex align-items-center gap-2 shadow-lg"
           :class="`alert-${toast.type}`">
        <i class="bi flex-shrink-0"
           :class="toast.type === 'success'
             ? 'bi-check-circle-fill' : 'bi-exclamation-triangle-fill'"></i>
        <span class="flex-grow-1 small fw-semibold">{{ toast.message }}</span>
        <button class="btn-close btn-close-sm" @click="toast.show = false"></button>
      </div>
    </Transition>

    <!-- ── Page loading ───────────────────────────────────────── -->
    <div v-if="pageLoading"
         class="d-flex align-items-center justify-content-center min-vh-100">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3"></div>
        <p class="text-muted small">Loading students…</p>
      </div>
    </div>

    <template v-else>

      <!-- ── Top header ─────────────────────────────────────── -->
      <div class="top-header px-4 py-3 bg-white border-bottom
                  d-flex align-items-center justify-content-between
                  gap-3 flex-wrap">
        <div class="d-flex align-items-center gap-3">
          <router-link :to="`/admin/${userStore.id}`"
                       class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
          <div>
            <h5 class="fw-bold mb-0 lh-1">Students</h5>
            <small class="text-muted">
              {{ filtered.length }} of {{ store.students.length }} shown
            </small>
          </div>
        </div>

        <!-- Summary chips -->
        <div class="d-flex gap-2 flex-wrap align-items-center">
          <div class="summary-chip">
            <i class="bi bi-people-fill text-primary me-1"></i>
            <strong>{{ store.students.length }}</strong>
            <span class="chip-label ms-1">Total</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-check-circle-fill text-success me-1"></i>
            <strong>{{ store.activeStudents?.length ?? activeCount }}</strong>
            <span class="chip-label ms-1">Active</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-slash-circle-fill text-danger me-1"></i>
            <strong>{{ store.blockedStudents?.length ?? blockedCount }}</strong>
            <span class="chip-label ms-1">Blocked</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-file-earmark-text text-info me-1"></i>
            <strong>{{ studentsWithResume }}</strong>
            <span class="chip-label ms-1">With Resume</span>
          </div>

          <div class="d-flex gap-2 ms-2">
            <button class="btn btn-success btn-sm"
                    :disabled="store.exportLoading"
                    @click="exportStudents">
              <span v-if="store.exportLoading"
                    class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-download me-1"></i>
              Export CSV
            </button>
            <button class="btn btn-outline-primary btn-sm"
                    :disabled="store.loadingStudents"
                    @click="store.fetchStudents(true)">
              <span v-if="store.loadingStudents"
                    class="spinner-border spinner-border-sm me-1"></span>
              <i v-else class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- ── Master-Detail ─────────────────────────────────── -->
      <div class="master-detail">

        <!-- ════ LEFT — Student list ════ -->
        <div class="list-panel">

          <!-- Filters -->
          <div class="p-2 border-bottom bg-white sticky-top">
            <div class="input-group input-group-sm mb-2">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input class="form-control border-start-0 ps-0"
                     v-model="search"
                     placeholder="Name, email, roll, branch…" />
              <button v-if="search" class="btn btn-outline-secondary"
                      @click="search = ''">
                <i class="bi bi-x"></i>
              </button>
            </div>
            <div class="d-flex gap-1 mb-1">
              <select class="form-select form-select-sm" v-model="branchFilter">
                <option value="">All Branches</option>
                <option v-for="b in branches" :key="b" :value="b">{{ b }}</option>
              </select>
              <select class="form-select form-select-sm" v-model="yearFilter">
                <option value="">All Years</option>
                <option v-for="y in gradYears" :key="y" :value="y">{{ y }}</option>
              </select>
            </div>
            <div class="d-flex align-items-center justify-content-between">
              <select class="form-select form-select-sm" style="max-width:130px"
                      v-model="statusFilter">
                <option value="">All Status</option>
                <option value="active">Active</option>
                <option value="blocked">Blocked</option>
              </select>
              <button v-if="search || branchFilter || yearFilter || statusFilter"
                      class="btn btn-outline-secondary btn-sm"
                      @click="search=''; branchFilter=''; yearFilter=''; statusFilter=''">
                <i class="bi bi-x me-1"></i>Clear
              </button>
              <small v-else class="text-muted">{{ filtered.length }} students</small>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="!filtered.length"
               class="text-center py-5 px-3 text-muted">
            <i class="bi bi-search fs-1 d-block mb-2 opacity-25"></i>
            <small>No students match filters</small>
          </div>

          <!-- Student rows -->
          <button v-for="s in filtered" :key="s.id"
                  class="applicant-row"
                  :class="{ 'row-active': selectedId === s.id }"
                  @click="selectStudent(s)">
            <div class="row-avatar" :class="!isActive(s.active) ? 'avatar-red' : 'avatar-blue'">
              {{ initials(s.name) }}
            </div>
            <div class="row-info">
              <div class="d-flex align-items-center justify-content-between gap-1 mb-1">
                <span class="fw-semibold small text-truncate" style="max-width:130px">
                  {{ s.name }}
                </span>
                <span class="badge flex-shrink-0"
                      style="font-size:.62rem"
                      :class="!isActive(s.active) ? 'bg-danger' : 'bg-success'">
                  {{ !isActive(s.active) ? 'Blocked' : 'Active' }}
                </span>
              </div>
              <div class="d-flex align-items-center justify-content-between">
                <small class="text-muted text-truncate" style="max-width:110px">
                  {{ s.branch || '—' }}
                </small>
                <small class="text-muted flex-shrink-0">
                  {{ s.cgpa ? `CGPA ${s.cgpa}` : '' }}
                </small>
              </div>
              <small class="text-muted" style="font-size:.68rem">
                {{ s.roll_number || s.email }}
              </small>
            </div>
          </button>

        </div>

        <!-- ════ RIGHT — Student detail ════ -->
        <div class="detail-panel bg-light">

          <!-- Empty state -->
          <div v-if="!selectedId"
               class="h-100 d-flex flex-column align-items-center
                      justify-content-center text-center p-4">
            <div class="empty-illustration mb-4">
              <i class="bi bi-person-lines-fill"></i>
            </div>
            <h5 class="fw-bold text-muted mb-1">Select a student</h5>
            <p class="text-muted small mb-0">
              Click any row to view their full profile and manage their account.
            </p>
          </div>

          <!-- Profile loading -->
          <div v-else-if="detailLoading"
               class="h-100 d-flex align-items-center justify-content-center">
            <div class="text-center">
              <div class="spinner-border text-primary mb-2"></div>
              <p class="text-muted small">Loading profile…</p>
            </div>
          </div>

          <!-- Profile loaded -->
          <div v-else-if="student" class="detail-scroll">

            <!-- ── Profile header ────────────────────────── -->
            <div class="detail-header bg-white border-bottom p-4">
              <div class="d-flex align-items-start
                          justify-content-between flex-wrap gap-3">
                <div class="d-flex align-items-center gap-3">
                  <div class="profile-avatar"
                       :class="!isActive(student.active) ? 'avatar-blocked' : ''">
                    {{ initials(student.name) }}
                  </div>
                  <div>
                    <h5 class="fw-bold mb-1">{{ student.name }}</h5>
                    <p class="text-muted small mb-1">
                      <i class="bi bi-envelope me-1"></i>{{ student.email }}
                      <span v-if="student.phone" class="ms-2">
                        <i class="bi bi-telephone me-1"></i>{{ student.phone }}
                      </span>
                    </p>
                    <!-- Badges -->
                    <div class="d-flex gap-1 flex-wrap mb-2">
                      <span v-if="student.branch"
                            class="badge bg-primary bg-opacity-10 text-primary">
                        {{ student.branch }}
                      </span>
                      <span v-if="student.cgpa" class="badge"
                            :class="cgpaBadge(student.cgpa)">
                        CGPA {{ student.cgpa }}
                      </span>
                      <span v-if="student.graduation_year"
                            class="badge bg-info bg-opacity-10 text-info">
                        {{ student.graduation_year }}
                      </span>
                      <span v-if="student.gender"
                            class="badge bg-secondary bg-opacity-10 text-secondary">
                        {{ student.gender }}
                      </span>
                    </div>
                    <!-- Social links -->
                    <div class="d-flex gap-2 flex-wrap align-items-center">
                      <a v-if="student.linkedin_url"
                         :href="student.linkedin_url" target="_blank"
                         class="social-pill social-linkedin">
                        <i class="bi bi-linkedin me-1"></i>LinkedIn
                      </a>
                      <a v-if="student.github_url"
                         :href="student.github_url" target="_blank"
                         class="social-pill social-github">
                        <i class="bi bi-github me-1"></i>GitHub
                      </a>
                      <a v-if="student.portfolio_url"
                         :href="student.portfolio_url" target="_blank"
                         class="social-pill social-portfolio">
                        <i class="bi bi-globe2 me-1"></i>Portfolio
                      </a>
                      <span v-if="!student.linkedin_url && !student.github_url
                                  && !student.portfolio_url"
                            class="text-muted small fst-italic">
                        <i class="bi bi-link-45deg me-1"></i>No social links
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Status + action -->
                <div class="d-flex flex-column align-items-end gap-2">
                  <span class="badge fs-6 px-3 py-2"
                        :class="!isActive(student.active) ? 'bg-danger' : 'bg-success'">
                    {{ !isActive(student.active) ? 'Blocked' : 'Active' }}
                  </span>
                  <button class="btn btn-sm"
                          :class="!isActive(student.active) ? 'btn-outline-success' : 'btn-outline-danger'"
                          :disabled="toggling"
                          @click="toggleActive">
                    <span v-if="toggling"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi me-1"
                       :class="!isActive(student.active) ? 'bi-check-circle' : 'bi-slash-circle'"></i>
                    {{ !isActive(student.active) ? 'Unblock' : 'Block' }}
                  </button>
                </div>
              </div>
            </div>

            <!-- ── Two-column body ───────────────────────── -->
            <div class="row g-0">

              <!-- Left: academic + skills -->
              <div class="col-lg-7 p-4 d-flex flex-column gap-4">

                <!-- Academic details -->
                <div class="card border-0 shadow-sm">
                  <div class="card-body p-4">
                    <h6 class="section-label">Academic Details</h6>
                    <div class="row g-3">
                      <div class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">Roll Number</small>
                          <strong>{{ student.roll_number || '—' }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">College</small>
                          <strong>{{ student.college_name || '—' }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">10th %</small>
                          <strong>{{ student.tenth_percentage ?? '—' }}</strong>
                        </div>
                      </div>
                      <div class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">12th %</small>
                          <strong>{{ student.twelfth_percentage ?? '—' }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Skills & Bio -->
                <div v-if="skillList.length || student.bio"
                     class="card border-0 shadow-sm">
                  <div class="card-body p-4">
                    <template v-if="skillList.length">
                      <h6 class="section-label">Skills</h6>
                      <div class="d-flex flex-wrap gap-1 mb-3">
                        <span v-for="sk in skillList" :key="sk"
                              class="badge bg-primary bg-opacity-10 text-primary py-2 px-3">
                          {{ sk }}
                        </span>
                      </div>
                    </template>
                    <template v-if="student.bio">
                      <h6 class="section-label">Bio</h6>
                      <p class="text-muted small mb-0" style="white-space:pre-wrap">
                        {{ student.bio }}
                      </p>
                    </template>
                  </div>
                </div>

                <!-- Applications table -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3
                              d-flex justify-content-between align-items-center">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-file-text me-2 text-primary"></i>
                      Applications
                      <span class="badge bg-primary bg-opacity-10 text-primary ms-1">
                        {{ applications.length }}
                      </span>
                    </h6>
                    <button class="btn btn-sm btn-outline-secondary"
                            :disabled="loadingApps"
                            @click="loadApplications(true)">
                      <span v-if="loadingApps"
                            class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-arrow-clockwise"></i>
                    </button>
                  </div>
                  <div class="card-body p-0">
                    <div v-if="loadingApps" class="text-center py-3">
                      <div class="spinner-border spinner-border-sm text-primary"></div>
                    </div>
                    <div v-else-if="!applications.length"
                         class="text-center py-4 text-muted small">
                      <i class="bi bi-inbox d-block mb-1 fs-4 opacity-25"></i>
                      No applications yet.
                    </div>
                    <div v-else class="table-responsive">
                      <table class="table table-sm table-hover mb-0 align-middle">
                        <thead class="table-light">
                          <tr>
                            <th>Drive</th>
                            <th>Company</th>
                            <th>Status</th>
                            <th>Applied</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="a in applications" :key="a.id">
                            <td>
                              <router-link :to="`/admin/${a.company_id}/drives/${a.drive_id}`"
                                           class="text-decoration-none fw-semibold small">
                                {{ a.drive_title }}
                              </router-link>
                            </td>
                            <td class="small">{{ a.company_name }}</td>
                            <td>
                              <span class="badge" :class="appStatusBadge(a.status)">
                                {{ a.status }}
                              </span>
                            </td>
                            <td class="small text-muted">
                              {{ fmtDate(a.applied_date) }}
                            </td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

              </div>

              <!-- Right: resume + quick stats -->
              <div class="col-lg-5 p-4 d-flex flex-column gap-3 border-start-lg">

                <!-- Resume -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-file-earmark-pdf me-2 text-danger"></i>
                      Resume
                    </h6>
                  </div>
                  <div class="card-body p-3">
                    <button v-if="student.resume_filename"
                            class="btn btn-primary btn-sm w-100"
                            :disabled="resumeBusy"
                            @click="viewResume(student.resume_filename)">
                      <span v-if="resumeBusy"
                            class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-eye me-1"></i>
                      View / Download
                    </button>
                    <p v-else class="text-muted small mb-0 text-center">
                      No resume uploaded.
                    </p>
                  </div>
                </div>

                <!-- Quick stats -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-bar-chart me-2 text-success"></i>
                      Application Stats
                    </h6>
                  </div>
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Total</span>
                      <strong>{{ applications.length }}</strong>
                    </li>
                    <li v-for="st in appStats" :key="st.label"
                        class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">{{ st.label }}</span>
                      <span class="badge" :class="st.cls">{{ st.count }}</span>
                    </li>
                  </ul>
                </div>

                <!-- Account info -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-person-badge me-2 text-secondary"></i>
                      Account Info
                    </h6>
                  </div>
                  <div class="card-body p-3 d-flex flex-column gap-2">
                    <div class="info-block">
                      <small class="text-muted d-block">User ID</small>
                      <strong>{{ student.user_id || student.id }}</strong>
                    </div>
                    <div v-if="student.created_at" class="info-block">
                      <small class="text-muted d-block">Registered</small>
                      <strong>{{ fmtDate(student.created_at) }}</strong>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>

        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter }       from 'vue-router'
import { useAdminStore }   from '@/stores/adminStore'
import { useUserStore }    from '@/stores/userStore'

const router    = useRouter()
const store     = useAdminStore()
const userStore = useUserStore()

// ── Page state ────────────────────────────────────────────────
const pageLoading = ref(true)
const toast       = reactive({ show: false, type: 'success', message: '' })

// ── List filters ──────────────────────────────────────────────
const search       = ref('')
const branchFilter = ref('')
const yearFilter   = ref('')
const statusFilter = ref('')

// ── Selected student ──────────────────────────────────────────
const selectedId    = ref(null)
const detailLoading = ref(false)
const loadingApps   = ref(false)
const toggling      = ref(false)
const resumeBusy    = ref(false)

const student      = computed(() => store.studentDetail?.[selectedId.value] ?? null)
const applications = computed(() => store.studentApplications?.[selectedId.value] ?? [])

// ── Derived ───────────────────────────────────────────────────
const branches = computed(() =>
  [...new Set(store.students.map(s => s.branch).filter(Boolean))].sort()
)
const gradYears = computed(() =>
  [...new Set(store.students.map(s => s.graduation_year).filter(Boolean))].sort()
)
const activeCount        = computed(() => store.students.filter(s =>  isActive(s.active)).length)
const blockedCount       = computed(() => store.students.filter(s => !isActive(s.active)).length)
const studentsWithResume = computed(() => store.students.filter(s =>  s.resume_link).length)

const skillList = computed(() =>
  (student.value?.skills || '').split(',').map(s => s.trim()).filter(Boolean)
)

const appStats = computed(() => [
  { label: 'Shortlisted', cls: 'bg-info text-dark', count: applications.value.filter(a => a.status === 'Shortlisted').length },
  { label: 'Selected',    cls: 'bg-success',         count: applications.value.filter(a => a.status === 'Selected').length },
  { label: 'Rejected',    cls: 'bg-danger',           count: applications.value.filter(a => a.status === 'Rejected').length },
])

const filtered = computed(() => {
  return store.students.filter(s => {
    const q = search.value.toLowerCase()
    const matchSearch = !q ||
      s.name?.toLowerCase().includes(q)        ||
      s.email?.toLowerCase().includes(q)       ||
      s.roll_number?.toLowerCase().includes(q) ||
      s.branch?.toLowerCase().includes(q)
    const matchBranch  = !branchFilter.value || s.branch === branchFilter.value
    const matchYear    = !yearFilter.value   || String(s.graduation_year) === String(yearFilter.value)
    const matchStatus  =
      !statusFilter.value ||
      (statusFilter.value === 'active'  &&  isActive(s.active)) ||
      (statusFilter.value === 'blocked' && !isActive(s.active))
    return matchSearch && matchBranch && matchYear && matchStatus
  })
})

// ── Load ──────────────────────────────────────────────────────
onMounted(async () => {
  try {
    if (!store.students.length) await store.fetchStudents()
  } finally { pageLoading.value = false }
})

async function selectStudent(s) {
  selectedId.value    = s.id
  detailLoading.value = true
  try {
    await store.fetchStudent(s.id)
    loadApplications()
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to load profile.')
  } finally { detailLoading.value = false }
}

async function loadApplications(force = false) {
  loadingApps.value = true
  try { await store.fetchStudentApplications(selectedId.value, force) }
  finally { loadingApps.value = false }
}

// ── Actions ───────────────────────────────────────────────────
async function toggleActive() {
  if (!student.value) return
  const newActive = !isActive(student.value.active)

  if (!newActive && !confirm('Block this student? They cannot log in.')) return

  toggling.value = true
  try {
    // FIX 1: was student.value.user_id — wrong field entirely.
    //   • user_id is the auth-user's PK; the API and _patch() both key on
    //     the student profile id, which is selectedId.value (s.id from the list)
    //   • Passing user_id caused the PATCH to hit the wrong backend row and
    //     _patch() to find a different student in the list → double-block bug
    // FIX 2: no manual cache patching here — adminstudentactions() already
    //   calls _patch('students', …) and patches studentDetail internally.
    //   Doing it again from the component caused duplicate/conflicting mutations.
    await store.adminstudentactions(selectedId.value, { active: newActive })
    showToast('success', `Student ${newActive ? 'unblocked' : 'blocked'}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally { toggling.value = false }
}

async function viewResume(filename) {
  resumeBusy.value = true
  try {
    const blob = await store.fetchresume(filename)
    if (blob) window.open(URL.createObjectURL(blob), '_blank')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to load resume.')
  } finally { resumeBusy.value = false }
}

async function exportStudents() {
  try { await store.exportData('students') }
  catch (e) { showToast('danger', e?.message ?? 'Export failed.') }
}

// ── Helpers ───────────────────────────────────────────────────

// FIX: _attr with fields.String serialises Python bool as the *string* "True"/"False".
// In JS every non-empty string is truthy, so !"False" === false → always shows Active.
// isActive() normalises all possible API shapes: boolean true/false, integer 1/0,
// or the string "True"/"False"/"true"/"false".
function isActive(val) {
  if (val === null || val === undefined) return true   // unknown → treat as active
  if (typeof val === 'boolean') return val
  if (typeof val === 'number')  return val !== 0
  return String(val).toLowerCase() !== 'false'
}

function showToast(type, message, ms = 4000) {
  Object.assign(toast, { show: true, type, message })
  setTimeout(() => (toast.show = false), ms)
}
function initials(name) {
  return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
function fmtDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  }) : '—'
}
function cgpaBadge(cgpa) {
  return cgpa >= 8 ? 'bg-success' : cgpa >= 6 ? 'bg-warning text-dark' : 'bg-danger'
}
function appStatusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}
</script>

<style scoped>
.page-root     { display:flex; flex-direction:column; height:100vh; overflow:hidden; background:#f4f6fb; }
.top-header    { flex-shrink:0; }
.master-detail { display:flex; flex:1; overflow:hidden; }

.list-panel {
  width:300px; flex-shrink:0;
  border-right:1px solid #dee2e6;
  background:#fff; overflow-y:auto;
}

.detail-panel  { flex:1; overflow-y:auto; }
.detail-scroll { min-height:100%; }
.detail-header { position:sticky; top:0; z-index:10; }

.summary-chip {
  display:flex; align-items:center;
  padding:.35rem .8rem; border-radius:8px;
  background:#fff; border:1px solid #dee2e6; font-size:.82rem;
}
.chip-label { font-size:.7rem; color:#6c757d; }

.applicant-row {
  display:flex; align-items:flex-start; gap:.75rem;
  width:100%; text-align:left; padding:.75rem 1rem;
  border:none; border-bottom:1px solid #f0f0f0;
  background:transparent; cursor:pointer; transition:background .12s;
}
.applicant-row:hover { background:#f8f9fa; }
.row-active {
  background:#eff5ff !important;
  border-left:3px solid #0d6efd;
  padding-left:calc(1rem - 3px);
}
.row-info { flex:1; min-width:0; }

.row-avatar {
  width:38px; height:38px; border-radius:50%; flex-shrink:0;
  display:flex; align-items:center; justify-content:center;
  font-size:.75rem; font-weight:700; color:#fff;
}
.avatar-blue    { background:linear-gradient(135deg,#0d6efd,#0a58ca); }
.avatar-red     { background:linear-gradient(135deg,#dc3545,#b02a37); }

.profile-avatar {
  width:64px; height:64px; border-radius:50%; flex-shrink:0;
  background:linear-gradient(135deg,#0d6efd,#6610f2);
  color:#fff; display:flex; align-items:center;
  justify-content:center; font-size:1.4rem; font-weight:700;
}
.avatar-blocked { background:linear-gradient(135deg,#dc3545,#b02a37) !important; }

.social-pill {
  display:inline-flex; align-items:center;
  padding:.28rem .75rem; border-radius:20px;
  font-size:.75rem; font-weight:600;
  text-decoration:none; transition:all .15s;
  border:1.5px solid transparent;
}
.social-linkedin  { background:#e8f0fe; color:#0a66c2; border-color:#c5d8f8; }
.social-linkedin:hover  { background:#0a66c2; color:#fff; }
.social-github    { background:#f0f0f0; color:#24292e; border-color:#d0d0d0; }
.social-github:hover    { background:#24292e; color:#fff; }
.social-portfolio { background:#e8f5e9; color:#2e7d32; border-color:#c8e6c9; }
.social-portfolio:hover { background:#2e7d32; color:#fff; }

.empty-illustration {
  width:80px; height:80px; border-radius:50%;
  background:#e9ecef; display:flex; align-items:center;
  justify-content:center; font-size:2rem; color:#adb5bd;
}

.info-block { padding:.75rem; background:#f8f9fa; border-radius:8px; height:100%; }
.section-label {
  font-size:.7rem; font-weight:700; text-transform:uppercase;
  letter-spacing:.08em; color:#6c757d;
  padding-bottom:.5rem; border-bottom:1px solid #dee2e6; margin-bottom:1rem;
}
@media (min-width:992px) { .border-start-lg { border-left:1px solid #dee2e6; } }

.toast-fixed {
  position:fixed; top:1rem; right:1rem; z-index:2000;
  min-width:280px; border-radius:10px;
}
.table th {
  font-size:.78rem; text-transform:uppercase;
  letter-spacing:.04em; color:#6c757d; white-space:nowrap;
}

@media (max-width:768px) {
  .page-root     { height:auto; overflow:auto; }
  .master-detail { flex-direction:column; overflow:visible; }
  .list-panel    { width:100%; border-right:none; border-bottom:1px solid #dee2e6; }
  .detail-panel  { overflow:visible; }
}
.fade-enter-active, .fade-leave-active { transition:opacity .3s; }
.fade-enter-from,  .fade-leave-to      { opacity:0; }
</style>