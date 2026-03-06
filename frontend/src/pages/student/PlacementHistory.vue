<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Placement History</h3>
          <small class="text-muted">Your successful placements and offers</small>
        </div>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <div v-if="store.loadingPlacements" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="!store.placements.length" class="text-center py-5">
        <i class="bi bi-trophy fs-1 text-muted d-block mb-3"></i>
        <h5 class="text-muted">No Placements Yet</h5>
        <p class="text-muted small">When you get selected, offers will appear here.</p>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-primary mt-2">
          <i class="bi bi-briefcase me-2"></i>Browse Open Drives
        </router-link>
      </div>

      <div v-else>

        <!-- Stats strip -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-primary">
                {{ store.placements.length }}
              </div>
              <small class="text-muted">Total Offers</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-success">
                {{ countByStatus('Joined') }}
              </div>
              <small class="text-muted">Joined</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-warning">
                {{ countByStatus('Offered') }}
              </div>
              <small class="text-muted">Pending</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-info">
                {{ highestSalary }}
              </div>
              <small class="text-muted">Best Package</small>
            </div>
          </div>
        </div>

        <!-- Active offer banner -->
        <div v-if="store.hasActivePlacement"
             class="alert alert-success d-flex
                    align-items-center gap-2 mb-4">
          <i class="bi bi-trophy-fill fs-4"></i>
          <div>
            <strong>Congratulations!</strong>
            You have an active placement offer waiting for your response.
          </div>
        </div>

        <!-- Placement Cards -->
        <div class="d-flex flex-column gap-3">
          <div v-for="p in store.placements" :key="p.id"
               class="card border-0 shadow-sm placement-card"
               :class="{
                 'border-start border-4 border-success': p.status === 'Joined',
                 'border-start border-4 border-warning': p.status === 'Offered',
                 'border-start border-4 border-danger':  p.status === 'Declined',
               }">
            <div class="card-body p-4">

              <!-- Header -->
              <div class="d-flex justify-content-between
                          align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="fw-bold mb-1">{{ p.position_title }}</h5>
                  <p class="text-muted mb-0 small">
                    <i class="bi bi-building me-1"></i>{{ p.company_name }}
                  </p>
                </div>
                <span class="badge fs-6 px-3 py-2"
                      :class="statusBadge(p.status)">
                  <i class="bi me-1" :class="statusIcon(p.status)"></i>
                  {{ p.status }}
                </span>
              </div>

              <!-- Info row -->
              <div class="row g-3 mt-2">
                <div class="col-md-4">
                  <small class="text-muted d-block">Package</small>
                  <strong class="text-success">
                    {{ formatSalary(p.salary, p.currency) }}
                  </strong>
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

              <!-- ── Offer Letter ──────────────────────────────────────────
                   Each placement is linked to a unique application_id, so
                   offer_letter_filename is per-application — no mix-ups even
                   if a student has multiple placements.
                   The backend serves via /api/uploads/offers/:filename
                   (OfferLetterDownloadResource) with auth token.
              ─────────────────────────────────────────────────────────── -->
              <div v-if="p.offer_letter_filename || p.offer_letter_url"
                   class="mt-3">
                <button class="btn btn-outline-primary btn-sm"
                        :disabled="downloadBusy[p.id]"
                        @click="viewOfferLetter(p)">
                  <span v-if="downloadBusy[p.id]"
                        class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-file-earmark-pdf me-1"></i>
                  {{ downloadBusy[p.id] ? 'Opening…' : 'View Offer Letter' }}
                </button>
              </div>

              <!-- Company Feedback -->
              <div v-if="p.feedback" class="mt-3">
                <div class="feedback-box rounded-3 p-3">
                  <div class="d-flex align-items-center gap-2 mb-1">
                    <i class="bi bi-chat-quote-fill text-success"></i>
                    <span class="fw-semibold small text-success">
                      Company Feedback
                    </span>
                  </div>
                  <p class="mb-0 small text-secondary fst-italic">
                    "{{ p.feedback }}"
                  </p>
                </div>
              </div>

              <!-- Accept / Decline (Offered status only) -->
              <div v-if="p.status === 'Offered'"
                   class="mt-3 pt-3 border-top">
                <p class="small text-muted mb-2">
                  <i class="bi bi-exclamation-circle me-1 text-warning"></i>
                  Please respond to this offer. Your decision helps the
                  placement team with records.
                </p>
                <div class="d-flex gap-2 flex-wrap">
                  <button class="btn btn-success btn-sm"
                          :disabled="offerBusy[p.id]"
                          @click="handleAccept(p.id)">
                    <span v-if="offerBusy[p.id] === 'accept'"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-check-circle me-1"></i>
                    Accept Offer
                  </button>
                  <button class="btn btn-outline-danger btn-sm"
                          :disabled="offerBusy[p.id]"
                          @click="handleDecline(p.id)">
                    <span v-if="offerBusy[p.id] === 'decline'"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-x-circle me-1"></i>
                    Decline Offer
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
import { computed, reactive, onMounted } from 'vue'
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

const offerBusy    = reactive({})
const downloadBusy = reactive({})

const countByStatus = status =>
  store.placements.filter(p => p.status === status).length

const highestSalary = computed(() => {
  const salaries = store.placements.map(p => p.salary).filter(Boolean)
  if (!salaries.length) return 'N/A'
  return formatSalary(Math.max(...salaries))
})

onMounted(() => store.fetchPlacements(userStore.studentId))

// ── View Offer Letter ─────────────────────────────────────────────────────────
// Each placement has its own offer_letter_filename keyed to its application_id,
// so even if a student has multiple placements there is no filename collision.
// We fetch with the auth token (plain <a> would get a 401) and open in a new
// tab so the browser renders the PDF natively.
async function viewOfferLetter(placement) {
  downloadBusy[placement.id] = true
  try {
    const token = localStorage.getItem('token')
    const base  = import.meta.env.VITE_API_BASE_URL ?? ''

    // Prefer the explicit filename; fall back to extracting it from the URL
    const filename = placement.offer_letter_filename
                  ?? placement.offer_letter_url?.split('/').pop()
    if (!filename) throw new Error('Offer letter filename is missing.')

    const res = await fetch(`${base}/uploads/offers/${filename}`, {
      headers: { 'Authentication-Token': token },
    })
    if (!res.ok) throw new Error(`Failed to load offer letter (${res.status})`)

    const blob   = await res.blob()
    const pdfBlob = new Blob([blob], { type: 'application/pdf' })
    const url    = URL.createObjectURL(pdfBlob)

    // Open in new tab — browser renders PDF inline
    window.open(url, '_blank')

    // Revoke after 60 s (browser will have loaded it by then)
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (e) {
    alert(e?.message ?? 'Failed to open offer letter.')
  } finally {
    downloadBusy[placement.id] = false
  }
}

// ── Accept offer ──────────────────────────────────────────────────────────────
async function handleAccept(placementId) {
  if (!confirm('Accept this offer? This will mark you as Joined.')) return
  offerBusy[placementId] = 'accept'
  try {
    await store.acceptOffer(userStore.studentId, placementId)
  } catch (e) {
    alert(e?.message ?? 'Failed to accept offer. Please try again.')
  } finally {
    offerBusy[placementId] = false
  }
}

// ── Decline offer ─────────────────────────────────────────────────────────────
async function handleDecline(placementId) {
  if (!confirm('Decline this offer? This action cannot be undone.')) return
  offerBusy[placementId] = 'decline'
  try {
    await store.declineOffer(userStore.studentId, placementId)
  } catch (e) {
    alert(e?.message ?? 'Failed to decline offer. Please try again.')
  } finally {
    offerBusy[placementId] = false
  }
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function formatSalary(s, currency = 'INR') {
  if (!s) return 'Not disclosed'
  const sym = currency === 'INR' ? '₹' : (currency ?? '₹')
  return s >= 100_000
    ? `${sym}${(s / 100_000).toFixed(1)} LPA`
    : `${sym}${s.toLocaleString('en-IN')}`
}

function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : '—'
}

function statusBadge(s) {
  return {
    Offered:  'bg-warning text-dark',
    Joined:   'bg-success',
    Declined: 'bg-danger',
  }[s] ?? 'bg-secondary'
}

function statusIcon(s) {
  return {
    Offered:  'bi-envelope-open',
    Joined:   'bi-trophy',
    Declined: 'bi-x-circle',
  }[s] ?? 'bi-circle'
}
</script>

<style scoped>
.placement-card { transition: transform .15s; }
.placement-card:hover { transform: translateY(-2px); }
.feedback-box {
  background: linear-gradient(135deg, #f0fff4 0%, #e6f9ed 100%);
  border: 1px solid #b8e8c8;
}
</style>