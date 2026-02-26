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
                @click="$router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="student">

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

        <!-- Header -->
        <div class="d-flex align-items-center
                    justify-content-between mb-4 flex-wrap gap-2">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="$router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
          <div class="d-flex align-items-center gap-2">
            <span class="badge fs-6 px-3 py-2"
                  :class="student.is_active
                    ? 'bg-success' : 'bg-danger'">
              {{ student.is_active ? 'Active' : 'Blocked' }}
            </span>
            <button class="btn btn-sm"
                    :class="student.is_active
                      ? 'btn-outline-danger'
                      : 'btn-outline-success'"
                    :disabled="toggling"
                    @click="toggleActive">
              <span v-if="toggling"
                    class="spinner-border spinner-border-sm me-1">
              </span>
              <i v-else class="bi me-1"
                 :class="student.is_active
                   ? 'bi-slash-circle' : 'bi-check-circle'"></i>
              {{ student.is_active
                  ? 'Block Student' : 'Unblock Student' }}
            </button>
          </div>
        </div>

        <!-- Profile card -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center gap-4
                        flex-wrap mb-4">
              <div class="avatar-lg">
                {{ initials(student.name) }}
              </div>
              <div class="flex-grow-1">
                <h3 class="fw-bold mb-1">{{ student.name }}</h3>
                <p class="text-muted mb-1 small">
                  <i class="bi bi-envelope me-1"></i>
                  {{ student.email }}
                </p>
                <p v-if="student.phone"
                   class="text-muted mb-0 small">
                  <i class="bi bi-telephone me-1"></i>
                  {{ student.phone }}
                </p>
              </div>
              <a v-if="student.resume_link"
                 :href="`${apiBase}/api/uploads/resumes/${student.resume_filename}`"
                 target="_blank"
                 class="btn btn-outline-primary btn-sm">
                <i class="bi bi-file-earmark-pdf me-1"></i>
                View Resume
              </a>
            </div>

            <!-- Info grid -->
            <div class="row g-3">
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">Roll Number</small>
                  <strong>{{ student.roll_number || '—' }}</strong>
                </div>
              </div>
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">Branch</small>
                  <strong>{{ student.branch || '—' }}</strong>
                </div>
              </div>
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">
                    Graduation Year
                  </small>
                  <strong>{{ student.graduation_year || '—' }}</strong>
                </div>
              </div>
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">CGPA</small>
                  <span v-if="student.cgpa" class="badge"
                        :class="cgpaBadge(student.cgpa)">
                    {{ student.cgpa }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </div>
              </div>
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">Gender</small>
                  <strong>{{ student.gender || '—' }}</strong>
                </div>
              </div>
              <div class="col-md-4">
                <div class="info-block">
                  <small class="text-muted d-block">College</small>
                  <strong>{{ student.college_name || '—' }}</strong>
                </div>
              </div>
              <div v-if="student.skills" class="col-12">
                <div class="info-block">
                  <small class="text-muted d-block mb-1">Skills</small>
                  <div class="d-flex flex-wrap gap-1">
                    <span v-for="sk in skillList" :key="sk"
                          class="badge bg-primary
                                 bg-opacity-10 text-primary">
                      {{ sk }}
                    </span>
                  </div>
                </div>
              </div>
              <div v-if="student.linkedin_url" class="col-md-6">
                <div class="info-block">
                  <small class="text-muted d-block">LinkedIn</small>
                  <a :href="student.linkedin_url" target="_blank"
                     class="small text-primary">
                    <i class="bi bi-linkedin me-1"></i>
                    View Profile
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Applications table -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-header bg-white border-bottom
                      d-flex justify-content-between
                      align-items-center py-3">
            <h6 class="mb-0 fw-bold">
              <i class="bi bi-file-text me-2 text-primary"></i>
              Applications
              ({{ store.studentApplications[studentId]?.length ?? 0 }})
            </h6>
            <button class="btn btn-sm btn-outline-secondary"
                    :disabled="loadingApps"
                    @click="loadApplications(true)">
              <span v-if="loadingApps"
                    class="spinner-border spinner-border-sm">
              </span>
              <i v-else class="bi bi-arrow-clockwise"></i>
            </button>
          </div>
          <div class="card-body p-0">
            <div v-if="loadingApps" class="text-center py-3">
              <div class="spinner-border spinner-border-sm
                          text-primary"></div>
            </div>
            <div v-else-if="!applications.length"
                 class="text-center py-3 text-muted small">
              No applications yet.
            </div>
            <div v-else class="table-responsive">
              <table class="table table-sm table-hover
                            mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Drive</th><th>Company</th>
                    <th>Status</th><th>Applied</th>
                    <th>Notes</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="a in applications" :key="a.id">
                    <td>
                      <router-link
                        :to="`/admin/drives/${a.drive_id}`"
                        class="text-decoration-none fw-semibold">
                        {{ a.drive_title }}
                      </router-link>
                    </td>
                    <td>{{ a.company_name }}</td>
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
                      <small class="text-muted">
                        {{ a.notes || '—' }}
                      </small>
                    </td>
                  </tr>
                </tbody>
              </table>
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
import { useAdminStore }        from '@/stores/adminStore'

const router = useRouter()
const route  = useRoute()
const store  = useAdminStore()

const apiBase   = import.meta.env.VITE_API_BASE_URL ?? ''
const studentId = route.params.studentId

const loading     = ref(true)
const loadingApps = ref(false)
const toggling    = ref(false)
const error       = ref('')
const toast       = reactive({ show: false, type: 'success', message: '' })

// Read from store cache
const student = computed(
  () => store.studentDetail[studentId] ?? null
)
const applications = computed(
  () => store.studentApplications[studentId] ?? []
)

const skillList = computed(() =>
  student.value?.skills
    ? student.value.skills
        .split(',').map(s => s.trim()).filter(Boolean)
    : []
)

// ── Load ──────────────────────────────────────────────────────────────────
async function loadStudent() {
  loading.value = true; error.value = ''
  try {
    // store action → GET /admin/students/:id
    await store.fetchStudent(studentId)
    if (!store.studentDetail[studentId]) {
      error.value = 'Student not found.'
      return
    }
    loadApplications()
  } catch (e) {
    error.value = e?.message ?? 'Failed to load student.'
  } finally {
    loading.value = false
  }
}

// store action → GET /admin/students/:id/applications
async function loadApplications(force = false) {
  loadingApps.value = true
  try {
    await store.fetchStudentApplications(studentId, force)
  } finally {
    loadingApps.value = false
  }
}

// store action → PUT /admin/users/:userId/active
async function toggleActive() {
  if (!student.value) return
  const newActive = !student.value.is_active
  if (!newActive &&
      !confirm('Block this student? They cannot log in.'))
    return
  toggling.value = true
  try {
    await store.toggleStudentActive(
      student.value.user_id, newActive
    )
    // store._patch already updates studentDetail.is_active
    showToast('success',
      `Student ${newActive ? 'unblocked' : 'blocked'}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally {
    toggling.value = false
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
function initials(name) {
  return (name || '?')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
function cgpaBadge(cgpa) {
  return cgpa >= 8
    ? 'bg-success' : cgpa >= 6
    ? 'bg-warning text-dark' : 'bg-danger'
}
function appStatusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}

onMounted(loadStudent)
</script>

<style scoped>
.avatar-lg {
  width: 72px; height: 72px; border-radius: 16px;
  background: #0d6efd; color: #fff;
  display: flex; align-items: center; justify-content: center;
  font-size: 1.5rem; font-weight: 700; flex-shrink: 0;
}
.info-block {
  padding: .75rem; background: #f8f9fa;
  border-radius: 8px; height: 100%;
}
.table th {
  font-size: .8rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
