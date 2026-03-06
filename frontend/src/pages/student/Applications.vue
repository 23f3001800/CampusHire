<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Applications</h3>
          <small class="text-muted">Track the status of all your drive applications</small>
        </div>
        <div class="d-flex gap-2">
          <!-- CSV Export -->
          <div>
            <button v-if="!store.csvExport.status"
                    class="btn btn-success btn-sm"
                    :disabled="!store.applications.length"
                    @click="startExport">
              <i class="bi bi-file-earmark-spreadsheet me-1"></i>Export CSV
            </button>
            <button v-else-if="store.csvExport.status === 'PENDING'"
                    class="btn btn-success btn-sm" disabled>
              <span class="spinner-border spinner-border-sm me-1"></span>Exporting…
            </button>
            <div v-else-if="store.csvExport.status === 'SUCCESS'" class="d-flex gap-1">
              <a :href="`${apiBase}${store.csvExport.downloadUrl}`"
                 class="btn btn-success btn-sm" target="_blank">
                <i class="bi bi-download me-1"></i>Download
              </a>
              <button class="btn btn-outline-secondary btn-sm"
                      @click="store.resetCSVExport()">
                <i class="bi bi-arrow-repeat"></i>
              </button>
            </div>
            <button v-else-if="store.csvExport.status === 'FAILURE'"
                    class="btn btn-danger btn-sm"
                    @click="store.resetCSVExport()">
              <i class="bi bi-exclamation-circle me-1"></i>Failed — Retry
            </button>
          </div>

          <router-link :to="`/student/${userStore.studentId}`"
                       class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
        </div>
      </div>

      <!-- Stats strip -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3" v-for="s in statChips" :key="s.label">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-4" :class="s.color">{{ s.value }}</div>
            <small class="text-muted">{{ s.label }}</small>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body d-flex flex-wrap gap-2">
          <div class="input-group" style="max-width:280px">
            <span class="input-group-text bg-white">
              <i class="bi bi-search"></i>
            </span>
            <input v-model="search" type="text"
                   class="form-control border-start-0"
                   placeholder="Search company or drive…" />
          </div>
          <select v-model="statusFilter" class="form-select" style="max-width:160px">
            <option value="">All Statuses</option>
            <option>Applied</option>
            <option>Shortlisted</option>
            <option>Selected</option>
            <option>Rejected</option>
          </select>
          <select v-model="sortBy" class="form-select" style="max-width:160px">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
          <button v-if="search || statusFilter"
                  class="btn btn-outline-secondary btn-sm"
                  @click="search = ''; statusFilter = ''">
            <i class="bi bi-x me-1"></i>Clear
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="store.loadingApps" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="!filtered.length" class="text-center py-5">
        <i class="bi bi-inbox fs-1 text-muted d-block mb-2"></i>
        <p class="text-muted">
          {{ search || statusFilter
              ? 'No applications match your filters'
              : "You haven't applied to any drives yet" }}
        </p>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-primary mt-2">Browse Drives</router-link>
      </div>

      <!-- Application Cards -->
      <div v-else class="d-flex flex-column gap-3">
        <div v-for="app in filtered" :key="app.id"
             class="card border-0 shadow-sm app-card"
             :class="{
               'border-start border-4 border-success': app.status === 'Selected',
               'border-start border-4 border-danger':  app.status === 'Rejected',
             }">
          <div class="card-body">

            <!-- Header row -->
            <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
              <div>
                <h5 class="fw-bold mb-1">{{ app.drive_title }}</h5>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-building me-1"></i>{{ app.company_name }}
                </p>
              </div>
              <span class="badge fs-6 px-3 py-2" :class="statusClass(app.status)">
                <i class="bi me-1" :class="statusIcon(app.status)"></i>{{ app.status }}
              </span>
            </div>

            <!-- Dates row -->
            <div class="row g-2 mt-2 small text-muted">
              <div class="col-auto">
                <i class="bi bi-calendar-event me-1"></i>Applied {{ fmt(app.applied_date) }}
              </div>
              <div v-if="app.reviewed_date" class="col-auto">
                <i class="bi bi-eye me-1"></i>Reviewed {{ fmt(app.reviewed_date) }}
              </div>
            </div>

            <!-- Recruiter note -->
            <div v-if="app.notes"
                 class="alert alert-light border py-2 px-3 mt-3 mb-0 small">
              <strong>Recruiter note:</strong> {{ app.notes }}
            </div>

            <!-- ── Company Feedback ── -->
            <div v-if="app.feedback" class="mt-3">
              <div class="feedback-box rounded-3 p-3">
                <div class="d-flex align-items-center gap-2 mb-1">
                  <i class="bi bi-chat-quote-fill text-primary"></i>
                  <span class="fw-semibold small text-primary">Company Feedback</span>
                </div>
                <p class="mb-0 small text-secondary fst-italic">
                  "{{ app.feedback }}"
                </p>
              </div>
            </div>

            <!-- ── Action Row ── -->
            <div class="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-2">
              <div class="d-flex gap-2 flex-wrap">
                <router-link :to="`/student/drives/${app.drive_id}`"
                             class="btn btn-outline-secondary btn-sm">
                  <i class="bi bi-eye me-1"></i>View Drive
                </router-link>

                <!-- Interview toggle button (Shortlisted or Selected) -->
                <button
                  v-if="app.status === 'Shortlisted' || app.status === 'Selected'"
                  class="btn btn-sm"
                  :class="expandedInterview === app.id
                    ? 'btn-info text-white'
                    : 'btn-outline-info'"
                  @click="toggleInterview(app.id)">
                  <span v-if="interviewLoading[app.id]"
                        class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi me-1"
                     :class="expandedInterview === app.id
                       ? 'bi-chevron-up'
                       : 'bi-camera-video'"></i>
                  {{ expandedInterview === app.id ? 'Hide Interview' : 'Interview Details' }}
                </button>
              </div>

              <button v-if="app.status === 'Applied'"
                      class="btn btn-outline-danger btn-sm"
                      :disabled="rowBusy[app.id]"
                      @click="withdraw(app.id)">
                <span v-if="rowBusy[app.id]"
                      class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-x-circle me-1"></i>Withdraw
              </button>
            </div>

            <!-- ── Inline Interview Panel ── -->
            <transition name="interview-slide">
              <div v-if="expandedInterview === app.id" class="mt-3">

                <!-- Loading state -->
                <div v-if="interviewLoading[app.id]"
                     class="interview-panel rounded-3 p-3 text-center">
                  <div class="spinner-border spinner-border-sm text-info me-2"></div>
                  <span class="small text-muted">Loading interview details…</span>
                </div>

                <!-- Error state -->
                <div v-else-if="interviewError[app.id]"
                     class="alert alert-warning py-2 px-3 small mb-0">
                  <i class="bi bi-exclamation-triangle me-1"></i>
                  {{ interviewError[app.id] }}
                </div>

                <!-- No interview found -->
                <div v-else-if="!interviewData[app.id]"
                     class="interview-panel rounded-3 p-3 text-center">
                  <i class="bi bi-camera-video-off text-muted d-block mb-1 fs-5"></i>
                  <small class="text-muted">No interview scheduled yet.</small>
                </div>

                <!-- Interview data -->
                <div v-else class="interview-panel rounded-3 p-3">
                  <div class="d-flex align-items-center gap-2 mb-3">
                    <div class="interview-icon-wrap">
                      <i class="bi bi-camera-video-fill text-info"></i>
                    </div>
                    <div>
                      <span class="fw-semibold text-info small d-block">
                        Interview Scheduled
                      </span>
                      <span class="text-muted" style="font-size:0.75rem">
                        Round {{ interviewData[app.id].round_number ?? 1 }}
                        —
                        {{ interviewData[app.id].interview_type ?? 'Interview' }}
                      </span>
                    </div>
                    <span class="ms-auto badge"
                          :class="interviewStatusBadge(interviewData[app.id].status)">
                      {{ interviewData[app.id].status ?? 'Scheduled' }}
                    </span>
                  </div>

                  <div class="row g-3 small">
                    <div class="col-sm-4" v-if="interviewData[app.id].scheduled_at">
                      <div class="text-muted mb-1">
                        <i class="bi bi-calendar-event me-1"></i>Date & Time
                      </div>
                      <strong>{{ fmtDateTime(interviewData[app.id].scheduled_at) }}</strong>
                    </div>

                    <div class="col-sm-4" v-if="interviewData[app.id].mode">
                      <div class="text-muted mb-1">
                        <i class="bi bi-display me-1"></i>Mode
                      </div>
                      <strong class="text-capitalize">{{ interviewData[app.id].mode }}</strong>
                    </div>

                    <div class="col-sm-4" v-if="interviewData[app.id].duration_minutes">
                      <div class="text-muted mb-1">
                        <i class="bi bi-clock me-1"></i>Duration
                      </div>
                      <strong>{{ interviewData[app.id].duration_minutes }} min</strong>
                    </div>

                    <!-- Venue (offline) or Link (online) -->
                    <div class="col-12"
                         v-if="interviewData[app.id].venue || interviewData[app.id].meeting_link">
                      <div class="text-muted mb-1">
                        <i class="bi me-1"
                           :class="interviewData[app.id].meeting_link
                             ? 'bi-link-45deg' : 'bi-geo-alt'"></i>
                        {{ interviewData[app.id].meeting_link ? 'Meeting Link' : 'Venue' }}
                      </div>
                      <a v-if="interviewData[app.id].meeting_link"
                         :href="interviewData[app.id].meeting_link"
                         target="_blank"
                         class="btn btn-sm btn-outline-info">
                        <i class="bi bi-box-arrow-up-right me-1"></i>Join Meeting
                      </a>
                      <strong v-else>{{ interviewData[app.id].venue }}</strong>
                    </div>

                    <!-- Instructions -->
                    <div class="col-12" v-if="interviewData[app.id].instructions">
                      <div class="text-muted mb-1">
                        <i class="bi bi-info-circle me-1"></i>Instructions
                      </div>
                      <div class="interview-instructions rounded-2 p-2 small">
                        {{ interviewData[app.id].instructions }}
                      </div>
                    </div>

                    <!-- Interviewer -->
                    <div class="col-sm-6"
                         v-if="interviewData[app.id].interviewer_name">
                      <div class="text-muted mb-1">
                        <i class="bi bi-person me-1"></i>Interviewer
                      </div>
                      <strong>{{ interviewData[app.id].interviewer_name }}</strong>
                    </div>
                  </div>

                  <!-- Interview Feedback (post-interview) -->
                  <div v-if="interviewData[app.id].feedback"
                       class="mt-3 pt-3 border-top">
                    <div class="d-flex align-items-center gap-2 mb-1">
                      <i class="bi bi-chat-square-text-fill text-info"></i>
                      <span class="fw-semibold small text-info">Interview Feedback</span>
                    </div>
                    <p class="mb-0 small text-secondary fst-italic">
                      "{{ interviewData[app.id].feedback }}"
                    </p>
                  </div>
                </div>

              </div>
            </transition>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

const search       = ref('')
const statusFilter = ref('')
const sortBy       = ref('newest')
const rowBusy      = reactive({})

// ── Interview inline state ──
const expandedInterview = ref(null)   // currently open app id
const interviewLoading  = reactive({})
const interviewError    = reactive({})
const interviewData     = reactive({}) // keyed by app.id

async function toggleInterview(appId) {
  if (expandedInterview.value === appId) {
    expandedInterview.value = null
    return
  }
  expandedInterview.value = appId
  

  // Already fetched — don't re-fetch
  if (interviewData[appId] !== undefined) return

  interviewLoading[appId] = true
  interviewError[appId]   = null
  try {
    // NEW store action: fetchInterviewDetails(studentId, applicationId)
    const data = await store.fetchInterview(userStore.studentId, appId)
    interviewData[appId] = data ?? null
  } catch (e) {
    interviewError[appId] = e?.message ?? 'Failed to load interview details'
  } finally {
    interviewLoading[appId] = false
  }
}

// ── Stats ──
const statChips = computed(() => {
  const s = store.applicationStats
  return [
    { label: 'Total',       value: s.total,       color: 'text-dark'    },
    { label: 'Shortlisted', value: s.shortlisted, color: 'text-info'    },
    { label: 'Selected',    value: s.selected,    color: 'text-success' },
    { label: 'Rejected',    value: s.rejected,    color: 'text-danger'  },
  ]
})

const filtered = computed(() => {
  let list = [...store.applications]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.drive_title?.toLowerCase().includes(q) ||
      a.company_name?.toLowerCase().includes(q)
    )
  }
  if (statusFilter.value)
    list = list.filter(a => a.status === statusFilter.value)
  list.sort((a, b) => {
    const diff = new Date(b.applied_date) - new Date(a.applied_date)
    return sortBy.value === 'newest' ? diff : -diff
  })
  return list
})

onMounted(async () => {
  await Promise.all([
    store.fetchProfile(userStore.studentId),
    store.fetchApplications(userStore.studentId),
  ])
})

async function startExport() {
  try {
    await store.startCSVExport(userStore.studentId)
  } catch (e) {
    alert(e.message ?? 'Export failed')
  }
}

async function withdraw(appId) {
  if (!confirm('Withdraw this application?')) return
  rowBusy[appId] = true
  try {
    await store.withdrawApplication(userStore.studentId, appId)
  } catch (e) {
    alert(e?.message ?? 'Failed to withdraw')
  } finally {
    rowBusy[appId] = false
  }
}

// ── Helpers ──
function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : '—'
}

function fmtDateTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function statusClass(s) {
  return {
    Applied:     'bg-primary',
    Shortlisted: 'bg-info text-dark',
    Selected:    'bg-success',
    Rejected:    'bg-danger',
  }[s] ?? 'bg-secondary'
}

function statusIcon(s) {
  return {
    Applied:     'bi-send',
    Shortlisted: 'bi-star',
    Selected:    'bi-trophy',
    Rejected:    'bi-x-circle',
  }[s] ?? 'bi-circle'
}

function interviewStatusBadge(s) {
  return {
    Scheduled:  'bg-info text-dark',
    Completed:  'bg-success',
    Cancelled:  'bg-danger',
    Rescheduled:'bg-warning text-dark',
  }[s] ?? 'bg-secondary'
}
</script>

<style scoped>
.app-card { transition: transform .15s; }
.app-card:hover { transform: translateY(-2px); }

/* Feedback box */
.feedback-box {
  background: linear-gradient(135deg, #f0f7ff 0%, #e8f4fd 100%);
  border: 1px solid #c8e1f7;
}

/* Interview panel */
.interview-panel {
  background: linear-gradient(135deg, #f0fbff 0%, #e6f7fd 100%);
  border: 1px solid #b8e8f7;
}

.interview-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(13,202,240,.12);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
}

.interview-instructions {
  background: rgba(255,255,255,.7);
  border: 1px solid #d0edf7;
  line-height: 1.5;
}

/* Slide transition */
.interview-slide-enter-active,
.interview-slide-leave-active {
  transition: all .25s ease;
  overflow: hidden;
}
.interview-slide-enter-from,
.interview-slide-leave-to {
  opacity: 0;
  max-height: 0;
  transform: translateY(-6px);
}
.interview-slide-enter-to,
.interview-slide-leave-from {
  opacity: 1;
  max-height: 600px;
}
</style>