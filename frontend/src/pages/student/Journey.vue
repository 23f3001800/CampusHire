<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <!-- Header -->
      <div class="d-flex align-items-center
                  justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <h3 class="fw-bold mb-0">My Journey</h3>
          <small class="text-muted">Applications &amp; Placements</small>
        </div>
        <div class="d-flex gap-2 align-items-center flex-wrap">

          <!-- CSV Export — only on Applications tab -->
          <template v-if="activeTab === 'applications'">
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
              <button class="btn btn-outline-secondary btn-sm" @click="store.resetCSVExport()">
                <i class="bi bi-arrow-repeat"></i>
              </button>
            </div>
            <button v-else-if="store.csvExport.status === 'FAILURE'"
                    class="btn btn-danger btn-sm" @click="store.resetCSVExport()">
              <i class="bi bi-exclamation-circle me-1"></i>Failed — Retry
            </button>
          </template>

          <router-link :to="`/student/${userStore.studentId}`"
                       class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
        </div>
      </div>

      <!-- Active placement banner -->
      <div v-if="store.hasActivePlacement"
           class="alert alert-success d-flex align-items-center gap-2 mb-3 py-2">
        <i class="bi bi-trophy-fill"></i>
        <div class="small">
          <strong>Congratulations!</strong> You have a pending offer.
          <button class="btn btn-link btn-sm p-0 alert-link align-baseline"
                  @click="activeTab = 'placements'">View offer →</button>
        </div>
      </div>

      <!-- ── ONE stats strip ── -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-3 text-dark">{{ store.applicationStats.total }}</div>
            <small class="text-muted">Applications</small>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-3 text-info">{{ store.applicationStats.shortlisted }}</div>
            <small class="text-muted">Shortlisted</small>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-3 text-success">{{ store.applicationStats.selected }}</div>
            <small class="text-muted">Selected</small>
          </div>
        </div>
        <div class="col-6 col-md-3">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-3 text-warning">{{ highestSalary }}</div>
            <small class="text-muted">Best Package</small>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item">
          <button class="nav-link fw-semibold"
                  :class="activeTab === 'applications' ? 'active text-primary' : 'text-muted'"
                  @click="activeTab = 'applications'">
            <i class="bi bi-send me-2"></i>Applications
            <span class="badge ms-2 rounded-pill"
                  :class="activeTab === 'applications' ? 'bg-primary' : 'bg-secondary bg-opacity-25 text-secondary'">
              {{ store.applications.length }}
            </span>
          </button>
        </li>
        <li class="nav-item">
          <button class="nav-link fw-semibold"
                  :class="activeTab === 'placements' ? 'active text-success' : 'text-muted'"
                  @click="activeTab = 'placements'">
            <i class="bi bi-trophy me-2"></i>Placements
            <span class="badge ms-2 rounded-pill"
                  :class="activeTab === 'placements' ? 'bg-success' : 'bg-secondary bg-opacity-25 text-secondary'">
              {{ store.placements.length }}
            </span>
            <span v-if="store.hasActivePlacement"
                  class="ms-1 badge bg-warning text-dark rounded-pill"
                  style="font-size:.65rem">New</span>
          </button>
        </li>
      </ul>

      <!-- ═══════════════ TAB: APPLICATIONS ═══════════════ -->
      <div v-if="activeTab === 'applications'">

        <!-- Filters -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body d-flex flex-wrap gap-2">
            <div class="input-group" style="max-width:280px">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input v-model="search" type="text"
                     class="form-control border-start-0"
                     placeholder="Search company or drive…" />
            </div>
            <select v-model="statusFilter" class="form-select" style="max-width:160px">
              <option value="">All Statuses</option>
              <option>Applied</option><option>Shortlisted</option>
              <option>Selected</option><option>Rejected</option>
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

        <div v-if="store.loadingApps" class="text-center py-5">
          <div class="spinner-border text-primary"></div>
        </div>

        <div v-else-if="!filtered.length" class="text-center py-5">
          <i class="bi bi-inbox fs-1 text-muted d-block mb-2"></i>
          <p class="text-muted">
            {{ search || statusFilter ? 'No applications match your filters'
                                      : "You haven't applied to any drives yet" }}
          </p>
          <router-link :to="`/student/${userStore.studentId}`" class="btn btn-primary mt-2">
            Browse Drives
          </router-link>
        </div>

        <div v-else class="d-flex flex-column gap-3">
          <div v-for="app in filtered" :key="app.id"
               :id="`app-${app.id}`"
               class="card border-0 shadow-sm app-card"
               :class="{
                 'border-start border-4 border-success': app.status === 'Selected',
                 'border-start border-4 border-danger':  app.status === 'Rejected',
                 'border-start border-4 border-info':    app.status === 'Shortlisted',
               }">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="fw-bold mb-1">{{ app.drive_title }}</h5>
                  <p class="text-muted mb-0 small">
                    <i class="bi bi-building me-1"></i>{{ app.company_name }}
                  </p>
                </div>
                <div class="d-flex align-items-center gap-2 flex-wrap">
                  <span class="badge fs-6 px-3 py-2" :class="appStatusClass(app.status)">
                    <i class="bi me-1" :class="appStatusIcon(app.status)"></i>{{ app.status }}
                  </span>
                  <button v-if="app.status === 'Selected' && placementForApp(app.id)"
                          class="btn btn-sm btn-outline-success"
                          @click="jumpToPlacement(app.id)">
                    <i class="bi bi-trophy me-1"></i>View Offer
                  </button>
                </div>
              </div>

              <div class="row g-2 mt-2 small text-muted">
                <div class="col-auto">
                  <i class="bi bi-calendar-event me-1"></i>Applied {{ fmt(app.applied_date) }}
                </div>
                <div v-if="app.reviewed_date" class="col-auto">
                  <i class="bi bi-eye me-1"></i>Reviewed {{ fmt(app.reviewed_date) }}
                </div>
              </div>

              <div v-if="app.notes"
                   class="alert alert-light border py-2 px-3 mt-3 mb-0 small">
                <strong>Recruiter note:</strong> {{ app.notes }}
              </div>

              <div v-if="app.feedback" class="mt-3">
                <div class="feedback-box rounded-3 p-3">
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="bi bi-chat-quote-fill text-primary"></i>
                    <span class="fw-semibold small text-primary">Company Feedback</span>
                  </div>
                  <p class="mb-0 small text-secondary fst-italic">"{{ app.feedback }}"</p>
                </div>
              </div>

              <div class="d-flex justify-content-between align-items-center mt-3 flex-wrap gap-2">
                <div class="d-flex gap-2 flex-wrap">
                  <router-link :to="`/student/${app.company_id}/drives/${app.drive_id}`"
                               class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-eye me-1"></i>View Drive
                  </router-link>
                  <button v-if="app.status === 'Shortlisted' || app.status === 'Selected'"
                          class="btn btn-sm"
                          :class="expandedInterview === app.id ? 'btn-info text-white' : 'btn-outline-info'"
                          @click="toggleInterview(app.id)">
                    <span v-if="interviewLoading[app.id]"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi me-1"
                       :class="expandedInterview === app.id ? 'bi-chevron-up' : 'bi-camera-video'"></i>
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

              <!-- Interview panel -->
              <transition name="slide">
                <div v-if="expandedInterview === app.id" class="mt-3">
                  <div v-if="interviewLoading[app.id]"
                       class="interview-panel rounded-3 p-3 text-center">
                    <div class="spinner-border spinner-border-sm text-info me-2"></div>
                    <span class="small text-muted">Loading…</span>
                  </div>
                  <div v-else-if="interviewError[app.id]"
                       class="alert alert-warning py-2 px-3 small mb-0">
                    {{ interviewError[app.id] }}
                  </div>
                  <div v-else-if="!interviewData[app.id]"
                       class="interview-panel rounded-3 p-3 text-center">
                    <i class="bi bi-camera-video-off text-muted d-block mb-1 fs-5"></i>
                    <small class="text-muted">No interview scheduled yet.</small>
                  </div>
                  <div v-else class="interview-panel rounded-3 p-3">
                    <div class="d-flex align-items-center gap-2 mb-3">
                      <div class="iv-icon"><i class="bi bi-camera-video-fill text-info"></i></div>
                      <div>
                        <span class="fw-semibold text-info small d-block">Interview Scheduled</span>
                        <span class="text-muted" style="font-size:.75rem">
                          Round {{ interviewData[app.id].round_number ?? 1 }} —
                          {{ interviewData[app.id].interview_type ?? 'Interview' }}
                        </span>
                      </div>
                      <span class="ms-auto badge"
                            :class="ivStatusBadge(interviewData[app.id].status)">
                        {{ interviewData[app.id].status ?? 'Scheduled' }}
                      </span>
                    </div>
                    <div class="row g-3 small">
                      <div class="col-sm-4" v-if="interviewData[app.id].scheduled_at">
                        <div class="text-muted mb-1"><i class="bi bi-calendar-event me-1"></i>Date & Time</div>
                        <strong>{{ fmtDT(interviewData[app.id].scheduled_at) }}</strong>
                      </div>
                      <div class="col-sm-4" v-if="interviewData[app.id].mode">
                        <div class="text-muted mb-1"><i class="bi bi-display me-1"></i>Mode</div>
                        <strong class="text-capitalize">{{ interviewData[app.id].mode }}</strong>
                      </div>
                      <div class="col-sm-4" v-if="interviewData[app.id].duration_minutes">
                        <div class="text-muted mb-1"><i class="bi bi-clock me-1"></i>Duration</div>
                        <strong>{{ interviewData[app.id].duration_minutes }} min</strong>
                      </div>
                      <div class="col-12"
                           v-if="interviewData[app.id].venue || interviewData[app.id].meeting_link">
                        <div class="text-muted mb-1">
                          <i class="bi me-1"
                             :class="interviewData[app.id].meeting_link ? 'bi-link-45deg' : 'bi-geo-alt'"></i>
                          {{ interviewData[app.id].meeting_link ? 'Meeting Link' : 'Venue' }}
                        </div>
                        <a v-if="interviewData[app.id].meeting_link"
                           :href="interviewData[app.id].meeting_link"
                           target="_blank" class="btn btn-sm btn-outline-info">
                          <i class="bi bi-box-arrow-up-right me-1"></i>Join Meeting
                        </a>
                        <strong v-else>{{ interviewData[app.id].venue }}</strong>
                      </div>
                      <div class="col-12" v-if="interviewData[app.id].instructions">
                        <div class="text-muted mb-1"><i class="bi bi-info-circle me-1"></i>Instructions</div>
                        <div class="iv-instructions rounded-2 p-2">
                          {{ interviewData[app.id].instructions }}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </transition>
            </div>
          </div>
        </div>
      </div>

      <!-- ═══════════════ TAB: PLACEMENTS ═══════════════ -->
      <div v-else-if="activeTab === 'placements'">
        <div v-if="store.loadingPlacements" class="text-center py-5">
          <div class="spinner-border text-success"></div>
        </div>

        <div v-else-if="!store.placements.length" class="text-center py-5">
          <i class="bi bi-trophy fs-1 text-muted d-block mb-3"></i>
          <h5 class="text-muted">No Placements Yet</h5>
          <p class="text-muted small">When you get selected, your offers will appear here.</p>
          <button class="btn btn-primary mt-2" @click="activeTab = 'applications'">
            <i class="bi bi-send me-2"></i>View My Applications
          </button>
        </div>

        <div v-else class="d-flex flex-column gap-3">
          <div v-for="p in store.placements" :key="p.id"
               :id="`placement-${p.application_id}`"
               class="card border-0 shadow-sm placement-card"
               :class="{
                 'border-start border-4 border-success': p.status === 'Joined',
                 'border-start border-4 border-warning': p.status === 'Offered',
                 'border-start border-4 border-danger':  p.status === 'Declined',
               }">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="fw-bold mb-1">{{ p.position_title }}</h5>
                  <p class="text-muted mb-0 small">
                    <i class="bi bi-building me-1"></i>{{ p.company_name }}
                  </p>
                </div>
                <span class="badge fs-6 px-3 py-2" :class="pStatusBadge(p.status)">
                  <i class="bi me-1" :class="pStatusIcon(p.status)"></i>{{ p.status }}
                </span>
              </div>

              <div class="row g-3 mt-2">
                <div class="col-md-4">
                  <small class="text-muted d-block">Package</small>
                  <strong class="text-success">{{ fmtSalary(p.salary, p.currency) }}</strong>
                </div>
                <div v-if="p.joining_date" class="col-md-4">
                  <small class="text-muted d-block">Joining Date</small>
                  <strong>{{ fmt(p.joining_date) }}</strong>
                </div>
                <div class="col-md-4">
                  <small class="text-muted d-block">Offer Received</small>
                  <strong>{{ fmt(p.created_at) }}</strong>
                </div>
              </div>

              <div v-if="p.offer_letter_filename || p.offer_letter_url" class="mt-3">
                <button class="btn btn-outline-primary btn-sm"
                        :disabled="dlBusy[p.id]" @click="viewOffer(p)">
                  <span v-if="dlBusy[p.id]" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-file-earmark-pdf me-1"></i>
                  {{ dlBusy[p.id] ? 'Opening…' : 'View Offer Letter' }}
                </button>
              </div>

              <button class="btn btn-link btn-sm p-0 text-muted small mt-2"
                      @click="jumpToApplication(p.application_id)">
                <i class="bi bi-send me-1"></i>View original application →
              </button>

              <div v-if="p.feedback" class="mt-3">
                <div class="feedback-box-success rounded-3 p-3">
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="bi bi-chat-quote-fill text-success"></i>
                    <span class="fw-semibold small text-success">Company Feedback</span>
                  </div>
                  <p class="mb-0 small text-secondary fst-italic">"{{ p.feedback }}"</p>
                </div>
              </div>

              <div v-if="p.status === 'Offered'" class="mt-3 pt-3 border-top">
                <p class="small text-muted mb-2">
                  <i class="bi bi-exclamation-circle me-1 text-warning"></i>
                  Please respond to this offer.
                </p>
                <div class="d-flex gap-2 flex-wrap">
                  <button class="btn btn-success btn-sm" :disabled="offerBusy[p.id]"
                          @click="handleAccept(p.id)">
                    <span v-if="offerBusy[p.id] === 'accept'"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-check-circle me-1"></i>Accept Offer
                  </button>
                  <button class="btn btn-outline-danger btn-sm" :disabled="offerBusy[p.id]"
                          @click="handleDecline(p.id)">
                    <span v-if="offerBusy[p.id] === 'decline'"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-x-circle me-1"></i>Decline Offer
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, nextTick } from 'vue'
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()
const apiBase   = import.meta.env.VITE_API_BASE_URL ?? ''

const activeTab    = ref('applications')
const search       = ref('')
const statusFilter = ref('')
const sortBy       = ref('newest')
const rowBusy      = reactive({})
const offerBusy    = reactive({})
const dlBusy       = reactive({})

const expandedInterview = ref(null)
const interviewLoading  = reactive({})
const interviewError    = reactive({})
const interviewData     = reactive({})

// ── Computed ──────────────────────────────────────────────────
const filtered = computed(() => {
  let list = [...store.applications]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.drive_title?.toLowerCase().includes(q) ||
      a.company_name?.toLowerCase().includes(q)
    )
  }
  if (statusFilter.value) list = list.filter(a => a.status === statusFilter.value)
  list.sort((a, b) => {
    const d = new Date(b.applied_date) - new Date(a.applied_date)
    return sortBy.value === 'newest' ? d : -d
  })
  return list
})

const highestSalary = computed(() => {
  const s = store.placements.map(p => p.salary).filter(Boolean)
  return s.length ? fmtSalary(Math.max(...s)) : 'N/A'
})

// ── Cross-tab ─────────────────────────────────────────────────
function placementForApp(appId) {
  return store.placements.find(p => p.application_id === appId)
}
async function jumpToPlacement(appId) {
  activeTab.value = 'placements'
  await nextTick()
  document.getElementById(`placement-${appId}`)
    ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
}
async function jumpToApplication(appId) {
  activeTab.value = 'applications'
  await nextTick()
  const el = document.getElementById(`app-${appId}`)
  if (el) {
    el.scrollIntoView({ behavior: 'smooth', block: 'center' })
    el.classList.add('highlight-flash')
    setTimeout(() => el.classList.remove('highlight-flash'), 1500)
  }
}

// ── Interview ─────────────────────────────────────────────────
async function toggleInterview(appId) {
  if (expandedInterview.value === appId) { expandedInterview.value = null; return }
  expandedInterview.value = appId
  if (interviewData[appId] !== undefined) return
  interviewLoading[appId] = true
  interviewError[appId]   = null
  try {
    interviewData[appId] = await store.fetchInterview(userStore.studentId, appId) ?? null
  } catch (e) {
    interviewError[appId] = e?.message ?? 'Failed to load interview details'
  } finally {
    interviewLoading[appId] = false
  }
}

// ── Actions ───────────────────────────────────────────────────
async function startExport() {
  try { await store.startCSVExport(userStore.studentId) }
  catch (e) { alert(e.message ?? 'Export failed') }
}
async function withdraw(appId) {
  if (!confirm('Withdraw this application?')) return
  rowBusy[appId] = true
  try { await store.withdrawApplication(userStore.studentId, appId) }
  catch (e) { alert(e?.message ?? 'Failed to withdraw') }
  finally { rowBusy[appId] = false }
}
async function handleAccept(id) {
  if (!confirm('Accept this offer?')) return
  offerBusy[id] = 'accept'
  try { await store.acceptOffer(userStore.studentId, id) }
  catch (e) { alert(e?.message ?? 'Failed.') }
  finally { offerBusy[id] = false }
}
async function handleDecline(id) {
  if (!confirm('Decline this offer? Cannot be undone.')) return
  offerBusy[id] = 'decline'
  try { await store.declineOffer(userStore.studentId, id) }
  catch (e) { alert(e?.message ?? 'Failed.') }
  finally { offerBusy[id] = false }
}
async function viewOffer(p) {
  dlBusy[p.id] = true
  try {
    const filename = p.offer_letter_filename ?? p.offer_letter_url?.split('/').pop()
    if (!filename) throw new Error('Filename missing.')
    const res = await fetch(`${apiBase}/uploads/offers/${filename}`, {
      headers: { 'Authentication-Token': localStorage.getItem('token') },
    })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const url = URL.createObjectURL(new Blob([await res.blob()], { type: 'application/pdf' }))
    window.open(url, '_blank')
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (e) { alert(e?.message ?? 'Failed to open offer letter.') }
  finally { dlBusy[p.id] = false }
}

// ── Helpers ───────────────────────────────────────────────────
function fmt(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
}
function fmtDT(d) {
  return d ? new Date(d).toLocaleString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
}
function fmtSalary(s, currency = 'INR') {
  if (!s) return 'Not disclosed'
  const sym = currency === 'INR' ? '₹' : (currency ?? '₹')
  return s >= 100_000 ? `${sym}${(s / 100_000).toFixed(1)} LPA` : `${sym}${s.toLocaleString('en-IN')}`
}
function appStatusClass(s) {
  return { Applied: 'bg-primary', Shortlisted: 'bg-info text-dark', Selected: 'bg-success', Rejected: 'bg-danger' }[s] ?? 'bg-secondary'
}
function appStatusIcon(s) {
  return { Applied: 'bi-send', Shortlisted: 'bi-star', Selected: 'bi-trophy', Rejected: 'bi-x-circle' }[s] ?? 'bi-circle'
}
function pStatusBadge(s) {
  return { Offered: 'bg-warning text-dark', Joined: 'bg-success', Declined: 'bg-danger' }[s] ?? 'bg-secondary'
}
function pStatusIcon(s) {
  return { Offered: 'bi-envelope-open', Joined: 'bi-trophy', Declined: 'bi-x-circle' }[s] ?? 'bi-circle'
}
function ivStatusBadge(s) {
  return { Scheduled: 'bg-info text-dark', Completed: 'bg-success', Cancelled: 'bg-danger', Rescheduled: 'bg-warning text-dark' }[s] ?? 'bg-secondary'
}

onMounted(async () => {
  await Promise.all([
    store.fetchProfile(userStore.studentId),
    store.fetchApplications(userStore.studentId),
    store.fetchPlacements(userStore.studentId),
  ])
})
</script>

<style scoped>
.app-card, .placement-card { transition: transform .15s; }
.app-card:hover, .placement-card:hover { transform: translateY(-2px); }
.nav-link { border: none; background: none; cursor: pointer; }
.nav-link.active { border-bottom: 3px solid currentColor; }
.feedback-box {
  background: linear-gradient(135deg, #f0f7ff, #e8f4fd);
  border: 1px solid #c8e1f7;
}
.feedback-box-success {
  background: linear-gradient(135deg, #f0fff4, #e6f9ed);
  border: 1px solid #b8e8c8;
}
.interview-panel {
  background: linear-gradient(135deg, #f0fbff, #e6f7fd);
  border: 1px solid #b8e8f7;
}
.iv-icon {
  width: 36px; height: 36px; border-radius: 50%;
  background: rgba(13,202,240,.12);
  display: flex; align-items: center; justify-content: center;
}
.iv-instructions { background: rgba(255,255,255,.7); border: 1px solid #d0edf7; line-height: 1.5; }
@keyframes highlight-flash {
  0%   { box-shadow: 0 0 0 4px rgba(13,110,253,.45); }
  100% { box-shadow: none; }
}
.highlight-flash { animation: highlight-flash 1.5s ease-out; }
.slide-enter-active, .slide-leave-active { transition: all .25s ease; overflow: hidden; }
.slide-enter-from, .slide-leave-to { opacity: 0; max-height: 0; transform: translateY(-6px); }
.slide-enter-to, .slide-leave-from { opacity: 1; max-height: 600px; }
</style>