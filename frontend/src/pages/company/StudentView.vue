<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:860px">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3">Loading student profile…</p>
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

      <template v-else-if="student">

        <!-- Header -->
        <div class="d-flex align-items-center mb-4">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>
            Back to Applicants
          </button>
        </div>

        <!-- Application status banner -->
        <div v-if="application"
             class="alert d-flex align-items-center
                    gap-2 shadow-sm mb-4"
             :class="appAlertClass">
          <i class="bi bi-info-circle-fill flex-shrink-0"></i>
          <div>
            Application Status:
            <strong>{{ application.status }}</strong>
            <span v-if="application.applied_date"
                  class="ms-2 small text-muted">
              Applied on {{ formatDate(application.applied_date) }}
            </span>
            <span v-if="application.reviewed_date"
                  class="ms-2 small text-muted">
              · Reviewed {{ formatDate(application.reviewed_date) }}
            </span>
          </div>
        </div>

        <div class="row g-4">

          <!-- LEFT — identity & academics -->
          <div class="col-lg-8 d-flex flex-column gap-4">

            <!-- Identity card -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <div class="d-flex align-items-center gap-3 mb-4">
                  <div class="student-avatar">
                    {{ initials(student.name) }}
                  </div>
                  <div>
                    <h4 class="fw-bold mb-1">
                      {{ student.name || '—' }}
                    </h4>
                    <p class="mb-0 text-muted small">
                      {{ student.email || '—' }}
                    </p>
                    <div class="d-flex gap-2 mt-1 flex-wrap">
                      <span v-if="student.branch"
                            class="badge bg-primary
                                   bg-opacity-10 text-primary">
                        {{ student.branch }}
                      </span>
                      <span v-if="student.cgpa"
                            class="badge bg-success
                                   bg-opacity-10 text-success">
                        CGPA {{ student.cgpa }}
                      </span>
                      <span v-if="student.graduation_year"
                            class="badge bg-info
                                   bg-opacity-10 text-info">
                        {{ student.graduation_year }}
                      </span>
                    </div>
                  </div>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">
                        Roll Number
                      </small>
                      <strong>
                        {{ student.roll_number || '—' }}
                      </strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Phone</small>
                      <strong>{{ student.phone || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Degree</small>
                      <strong>{{ student.degree || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">
                        10th / 12th %
                      </small>
                      <strong>
                        {{ student.tenth_percentage ?? '—' }} /
                        {{ student.twelfth_percentage ?? '—' }}
                      </strong>
                    </div>
                  </div>
                  <div v-if="student.college_name" class="col-12">
                    <div class="info-block">
                      <small class="text-muted d-block">
                        College
                      </small>
                      <strong>{{ student.college_name }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Skills & Bio card -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <template v-if="skillList.length">
                  <h6 class="section-label">Skills</h6>
                  <div class="d-flex flex-wrap gap-1 mb-4">
                    <span v-for="s in skillList" :key="s"
                          class="badge bg-primary
                                 bg-opacity-10 text-primary">
                      {{ s }}
                    </span>
                  </div>
                </template>

                <template v-if="student.bio">
                  <h6 class="section-label">Bio</h6>
                  <p class="text-muted small mb-0"
                     style="white-space:pre-wrap">
                    {{ student.bio }}
                  </p>
                </template>

                <template v-if="student.experience_required">
                  <h6 class="section-label mt-4">Experience</h6>
                  <p class="text-muted small mb-0">
                    {{ student.experience_required }}
                  </p>
                </template>
              </div>
            </div>

            <!-- Cover letter -->
            <div v-if="application?.cover_letter"
                 class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-file-text me-2
                             text-primary"></i>Cover Letter
                </h6>
              </div>
              <div class="card-body">
                <p class="text-muted small mb-0"
                   style="white-space:pre-wrap">
                  {{ application.cover_letter }}
                </p>
              </div>
            </div>

          </div>

          <!-- RIGHT — links + resume + actions -->
          <div class="col-lg-4 d-flex flex-column gap-3">

            <!-- Resume card -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-file-earmark-pdf me-2
                             text-danger"></i>Resume
                </h6>
              </div>
              <div class="card-body d-grid gap-2">
                <template v-if="student.resume_filename">
                  <a :href="`/api/uploads/resumes/
                             ${student.resume_filename}`"
                     target="_blank"
                     class="btn btn-primary btn-sm">
                    <i class="bi bi-eye me-1"></i>View Resume
                  </a>
                  <a :href="`/api/uploads/resumes/
                             ${student.resume_filename}`"
                     download
                     class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-download me-1"></i>
                    Download
                  </a>
                </template>
                <p v-else class="text-muted small mb-0">
                  No resume uploaded.
                </p>
              </div>
            </div>

            <!-- Social / Portfolio links -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-link-45deg me-2
                             text-info"></i>Links
                </h6>
              </div>
              <div class="card-body">
                <div class="d-flex flex-column gap-2">
                  <a v-if="student.linkedin_url"
                     :href="student.linkedin_url"
                     target="_blank"
                     class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-linkedin me-1"></i>LinkedIn
                  </a>
                  <a v-if="student.github_url"
                     :href="student.github_url"
                     target="_blank"
                     class="btn btn-outline-dark btn-sm">
                    <i class="bi bi-github me-1"></i>GitHub
                  </a>
                  <a v-if="student.portfolio_url"
                     :href="student.portfolio_url"
                     target="_blank"
                     class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-globe2 me-1"></i>Portfolio
                  </a>
                  <p v-if="!student.linkedin_url &&
                            !student.github_url &&
                            !student.portfolio_url"
                     class="text-muted small mb-0">
                    No links added.
                  </p>
                </div>
              </div>
            </div>

            <!-- Application notes (read-only) -->
            <div v-if="application?.notes"
                 class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-chat-left-text me-2
                             text-secondary"></i>
                  Recruiter Notes
                </h6>
              </div>
              <div class="card-body">
                <p class="text-muted small mb-0">
                  {{ application.notes }}
                </p>
              </div>
            </div>

          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute }  from 'vue-router'
import { useCompanyStore }      from '@/stores/companyStore'
import { useUserStore }         from '@/stores/userStore'

const router     = useRouter()
const route      = useRoute()
const store      = useCompanyStore()
const userStore  = useUserStore()

// Route: /company/students/:studentId
const studentId = route.params.studentId

// Optional: ?driveId=x&applicationId=y allows banner to show
const driveId       = route.query.driveId
  ? parseInt(route.query.driveId)
  : null
const applicationId = route.query.applicationId
  ? parseInt(route.query.applicationId)
  : null

const student     = ref(null)
const loading     = ref(true)
const error       = ref('')

// Pull application from store cache if IDs are in query
const application = computed(() => {
  if (!driveId || !applicationId) return null
  const apps = store.applicants[driveId] || []
  return apps.find(a => a.id === applicationId) || null
})

const skillList = computed(() =>
  (student.value?.skills || '')
    .split(',')
    .map(s => s.trim())
    .filter(Boolean)
)

const appAlertClass = computed(() => ({
  Applied:     'alert-primary',
  Shortlisted: 'alert-info',
  Selected:    'alert-success',
  Rejected:    'alert-danger',
}[application.value?.status] ?? 'alert-secondary'))

// GET /student/:id  (roles_accepted: company, admin)
// api.get() returns student_fields directly — no .data
async function loadStudent() {
  loading.value = true
  error.value   = ''
  try {
    student.value = await store.fetchStudentProfile(studentId)
  } catch (e) {
    error.value =
      e?.message ?? 'Student not found or access denied.'
  } finally {
    loading.value = false
  }
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

function initials(name) {
  return (name || '?')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

onMounted(loadStudent)
</script>

<style scoped>
.student-avatar {
  width: 64px; height: 64px; border-radius: 50%;
  background: linear-gradient(135deg, #0d6efd, #6610f2);
  color: #fff; display: flex; align-items: center;
  justify-content: center;
  font-size: 1.4rem; font-weight: 700; flex-shrink: 0;
}
.info-block {
  padding: .75rem; background: #f8f9fa;
  border-radius: 8px; height: 100%;
}
.section-label {
  font-size: .7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  color: #6c757d; padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
