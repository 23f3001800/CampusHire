<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

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
      <template v-else-if="company">

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

        <!-- Top bar -->
        <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
          <button class="btn btn-outline-secondary btn-sm" @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
          <div class="d-flex align-items-center gap-2">
            <span class="badge fs-6 px-3 py-2"
                  :class="approvalBadge(company.approval_status)">
              {{ company.approval_status ?? 'Unknown' }}
            </span>
            <span class="badge fs-6 px-3 py-2"
                  :class="company.active ? 'bg-success' : 'bg-secondary'">
              {{ company.active ? 'Active' : 'Blocked' }}
            </span>
          </div>
        </div>

        <!-- Main layout -->
        <div class="row g-4">

          <!-- LEFT -->
          <div class="col-lg-8 d-flex flex-column gap-4">

            <!-- Identity card -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <div class="d-flex align-items-center gap-3 mb-4">
                  <img v-if="company.logo_url"
                       :src="company.logo_url"
                       class="rounded-3 border"
                       style="width:64px;height:64px;object-fit:cover"
                       @error="company.logo_url = null" />
                  <div v-else class="company-avatar-lg">
                    {{ initials(company.company_name) }}
                  </div>
                  <div>
                    <h2 class="fw-bold mb-1">{{ company.company_name || '—' }}</h2>
                    <p class="text-muted mb-0 small">
                      <i class="bi bi-briefcase me-1"></i>
                      {{ company.industry || 'Industry not set' }}
                      <span v-if="company.location" class="ms-2">
                        <i class="bi bi-geo-alt me-1"></i>{{ company.location }}
                      </span>
                    </p>
                    <a v-if="company.website" :href="company.website" target="_blank"
                       class="small text-primary text-decoration-none">
                      <i class="bi bi-link-45deg me-1"></i>{{ company.website }}
                    </a>
                  </div>
                </div>

                <div class="row g-3">
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Recruiter Name</small>
                      <strong>{{ company.recruiter_name || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Recruiter Email</small>
                      <a :href="`mailto:${company.recruiter_email}`"
                         class="text-primary text-decoration-none">
                        {{ company.recruiter_email || '—' }}
                      </a>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Company Size</small>
                      <strong>{{ company.company_size || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Founded Year</small>
                      <strong>{{ company.founded_year || '—' }}</strong>
                    </div>
                  </div>
                  <div v-if="company.description" class="col-12">
                    <div class="info-block">
                      <small class="text-muted d-block mb-1">About Company</small>
                      <p class="mb-0 small" style="white-space:pre-wrap">
                        {{ company.description }}
                      </p>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Registered On</small>
                      <strong>{{ fmtDate(company.created_at) }}</strong>
                    </div>
                  </div>
                  <div v-if="company.verified_at" class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Approved On</small>
                      <strong>{{ fmtDate(company.verified_at) }}</strong>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Drives table -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3
                          d-flex justify-content-between align-items-center">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-briefcase me-2 text-primary"></i>
                  Placement Drives ({{ drives.length }})
                </h6>
                <div class="d-flex gap-2 align-items-center">
                  <span class="badge bg-success">{{ openCount }} Open</span>
                  <span class="badge bg-secondary">{{ closedCount }} Closed</span>
                  <button class="btn btn-sm btn-outline-secondary"
                          :disabled="loadingDrives"
                          @click="store.fetchCompanyDrives(companyId, true)">
                    <span v-if="loadingDrives"
                          class="spinner-border spinner-border-sm"></span>
                    <i v-else class="bi bi-arrow-clockwise"></i>
                  </button>
                </div>
              </div>
              <div class="card-body p-0">

                <div v-if="loadingDrives" class="text-center py-4">
                  <div class="spinner-border spinner-border-sm text-primary"></div>
                </div>

                <div v-else-if="!drives.length"
                     class="text-center py-4 text-muted small">
                  <i class="bi bi-folder-x d-block mb-1 fs-4"></i>
                  No drives posted yet.
                </div>

                <div v-else class="table-responsive">
                  <table class="table table-hover mb-0 align-middle">
                    <thead class="table-light">
                      <tr>
                        <th>Title</th><th>Type</th><th>Status</th>
                        <th>Approval</th><th>Deadline</th>
                        <th class="text-end">Applicants</th>
                        <th class="text-end">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="d in drives" :key="d.id">
                        <td>
                          <router-link :to="`/admin/drives/${d.id}`"
                                       class="fw-semibold text-decoration-none">
                            {{ d.title }}
                          </router-link>
                          <div v-if="d.location" class="small text-muted">
                            <i class="bi bi-geo-alt me-1"></i>{{ d.location }}
                          </div>
                        </td>
                        <td><small>{{ d.job_type || '—' }}</small></td>
                        <td>
                          <span class="badge" :class="statusBadge(d.status)">
                            {{ d.status }}
                          </span>
                        </td>
                        <td>
                          <span class="badge" :class="approvalBadge(d.admin_approval_status)">
                            {{ d.admin_approval_status || 'Pending' }}
                          </span>
                        </td>
                        <td>
                          <span :class="{
                            'text-danger fw-semibold': isUrgent(d.application_deadline)
                          }">{{ fmtDate(d.application_deadline) }}</span>
                        </td>
                        <td class="text-end">
                          <span class="badge bg-light text-dark">
                            {{ d.total_applications ?? 0 }}
                          </span>
                        </td>
                        <td class="text-end">
                          <div class="d-flex gap-1 justify-content-end">
                            <button v-if="d.admin_approval_status !== 'Approved'"
                                    class="btn btn-xs btn-success"
                                    :disabled="driveBusy[d.id]"
                                    @click="handleDrivePatch(d, { admin_approval_status: 'Approved' })">
                              <i class="bi bi-check"></i>
                            </button>
                            <button v-if="d.admin_approval_status !== 'Rejected'"
                                    class="btn btn-xs btn-outline-danger"
                                    :disabled="driveBusy[d.id]"
                                    @click="handleDrivePatch(d, { admin_approval_status: 'Rejected' })">
                              <i class="bi bi-x"></i>
                            </button>
                            <button class="btn btn-xs btn-outline-secondary"
                                    :disabled="driveBusy[d.id]"
                                    :title="d.status === 'Open' ? 'Close drive' : 'Open drive'"
                                    @click="handleDrivePatch(d, {
                                      status: d.status === 'Open' ? 'Closed' : 'Open'
                                    })">
                              <span v-if="driveBusy[d.id]"
                                    class="spinner-border spinner-border-sm"></span>
                              <i v-else class="bi"
                                 :class="d.status === 'Open' ? 'bi-lock' : 'bi-unlock'"></i>
                            </button>
                          </div>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

          </div>

          <!-- RIGHT -->
          <div class="col-lg-4 d-flex flex-column gap-3">

            <!-- Admin actions -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-shield-check me-2 text-primary"></i>
                  Admin Actions
                </h6>
              </div>
              <div class="card-body d-grid gap-2">

                <button v-if="company.approval_status !== 'Approved'"
                        class="btn btn-success btn-sm"
                        :disabled="busy"
                        @click="handleCompanyPatch({ approval_status: 'Approved' })">
                  <span v-if="busy"
                        class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-check-circle me-1"></i>
                  {{ company.approval_status === 'Rejected' ? 'Approve Now' : 'Approve Company' }}
                </button>

                <button v-if="company.approval_status !== 'Rejected'"
                        class="btn btn-outline-danger btn-sm"
                        :disabled="busy"
                        @click="handleCompanyPatch({ approval_status: 'Rejected' })">
                  <i class="bi bi-x-circle me-1"></i>
                  {{ company.approval_status === 'Approved' ? 'Revoke Approval' : 'Reject Company' }}
                </button>

                <hr class="my-1" />

                <button class="btn btn-sm"
                        :class="company.active ? 'btn-outline-danger' : 'btn-outline-success'"
                        :disabled="busy"
                        @click="handleCompanyPatch({ active: !company.active })">
                  <span v-if="busy"
                        class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi me-1"
                     :class="company.active ? 'bi-slash-circle' : 'bi-check-circle'"></i>
                  {{ company.active ? 'Block Company' : 'Unblock Company' }}
                </button>
                <button class="btn btn-danger" @click="handleCompanyDelete">
                  <i class="bi bi-trash me-1"></i>
                  Delete company
                </button>
              </div>
            </div>

            <!-- Drive stats -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-bar-chart me-2 text-success"></i>
                  Drive Stats
                </h6>
              </div>
              <div class="card-body p-0">
                <ul class="list-group list-group-flush">
                  <li class="list-group-item d-flex justify-content-between">
                    <span class="text-muted small">Total Drives</span>
                    <strong>{{ drives.length }}</strong>
                  </li>
                  <li class="list-group-item d-flex justify-content-between">
                    <span class="text-muted small">Open Drives</span>
                    <span class="badge bg-success">{{ openCount }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between">
                    <span class="text-muted small">Closed / Completed</span>
                    <span class="badge bg-secondary">{{ closedCount + completedCount }}</span>
                  </li>
                  <li class="list-group-item d-flex justify-content-between">
                    <span class="text-muted small">Total Applicants</span>
                    <strong>{{ totalApplicants }}</strong>
                  </li>
                  <li class="list-group-item d-flex justify-content-between">
                    <span class="text-muted small">Pending Approvals</span>
                    <span class="badge"
                          :class="pendingDriveCount > 0 ? 'bg-warning text-dark' : 'bg-success'">
                      {{ pendingDriveCount }}
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Recruiter contact -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-person me-2 text-info"></i>
                  Recruiter Contact
                </h6>
              </div>
              <div class="card-body">
                <div class="d-flex align-items-center gap-3">
                  <div class="recruiter-avatar">
                    {{ initials(company.recruiter_name) }}
                  </div>
                  <div>
                    <div class="fw-semibold small">{{ company.recruiter_name || '—' }}</div>
                    <a v-if="company.recruiter_email"
                       :href="`mailto:${company.recruiter_email}`"
                       class="small text-primary text-decoration-none d-block">
                      {{ company.recruiter_email }}
                    </a>
                    <a v-if="company.phone" :href="`tel:${company.phone}`"
                       class="small text-muted text-decoration-none">
                      <i class="bi bi-telephone me-1"></i>{{ company.phone }}
                    </a>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter, useRoute }                from 'vue-router'
import { useAdminStore }                      from '@/stores/adminStore'

export default {
  name: 'AdminCompanyDetail',

  setup() {
    const router    = useRouter()
    const route     = useRoute()
    const store     = useAdminStore()
    const companyId = route.params.companyId

    // ── UI-only state (not data) ───────────────────────────────────────────
    const busy      = ref(false)
    const driveBusy = reactive({})
    const error     = ref('')
    const toast     = reactive({ show: false, type: 'success', message: '' })

    // ── All data reads from store — no local copies ────────────────────────
    const company      = computed(() => store.companyDetail[companyId] ?? null)
    const drives       = computed(() => store.companyDrives[companyId] ?? [])
    const loading      = computed(() => !!store.loadingCompanyDetail[companyId])
    const loadingDrives = computed(() => !!store.loadingCompanyDrives[companyId])

    // ── Drive computed stats (derived from store-backed drives) ────────────
    const openCount      = computed(() => drives.value.filter(d => d.status === 'Open').length)
    const closedCount    = computed(() => drives.value.filter(d => d.status === 'Closed').length)
    const completedCount = computed(() => drives.value.filter(d => d.status === 'Completed').length)
    const totalApplicants = computed(() =>
      drives.value.reduce((sum, d) => sum + (d.total_applications ?? 0), 0)
    )
    const pendingDriveCount = computed(() =>
      drives.value.filter(d => !d.admin_approval_status ||
                                d.admin_approval_status === 'Pending').length
    )

    // ── Initial load — delegates entirely to store ─────────────────────────
    async function init() {
      error.value = ''
      try {
        await store.fetchCompany(companyId)
        await store.fetchCompanyDrives(companyId)
      } catch (e) {
        error.value = e?.message ?? 'Failed to load company.'
      }
    }

    // ── PATCH /admin/companies/:id ─────────────────────────────────────────
    // approve → { approval_status: 'Approved' }
    // reject  → { approval_status: 'Rejected' }
    // block   → { active: false }
    // unblock → { active: true }
    async function handleCompanyPatch(payload) {
      busy.value = true
      try {
        await store.patchCompany(companyId, payload)
        // store.patchCompany already updates companyDetail — no manual sync needed
        const msg = 'approval_status' in payload
          ? `Company ${payload.approval_status === 'Approved' ? 'approved' : 'rejected'}.`
          : `Company ${payload.active ? 'unblocked' : 'blocked'}.`
        showToast('success', msg)
      } catch (e) {
        showToast('danger', e?.message ?? 'Action failed.')
      } finally {
        busy.value = false
      }
    }

    async function handleCompanyDelete() {
      if (!confirm('Are you sure you want to delete this company? This action cannot be undone.')) return
      busy.value = true
      try {
        await store.deleteCompany(companyId)
        showToast('success', 'Company deleted successfully.')
        router.back()
      } catch (e) {
        showToast('danger', e?.message ?? 'Failed to delete company.')
      } finally {
        busy.value = false
        router.back()
      }
    }
    // ── PATCH /company/:cid/drives/:did ────────────────────────────────────
    // approve drive → { admin_approval_status: 'Approved' }
    // reject  drive → { admin_approval_status: 'Rejected' }
    // toggle status → { status: 'Open' | 'Closed' }
    async function handleDrivePatch(drive, payload) {
      driveBusy[drive.id] = true
      try {
        // store.patchDrive updates companyDrives in place — UI reacts automatically
        await store.patchDrive(drive.id, payload, companyId)
        const msg = 'admin_approval_status' in payload
          ? `Drive ${payload.admin_approval_status === 'Approved' ? 'approved' : 'rejected'}.`
          : `Drive status changed to ${payload.status}.`
        showToast('success', msg)
      } catch (e) {
        showToast('danger', e?.message ?? 'Drive action failed.')
      } finally {
        driveBusy[drive.id] = false
      }
    }

    // ── Pure UI helpers ────────────────────────────────────────────────────
    function showToast(type, message, ms = 4000) {
      Object.assign(toast, { show: true, type, message })
      setTimeout(() => (toast.show = false), ms)
    }

    function fmtDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    }

    function initials(name) {
      return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    }

    function isUrgent(deadline) {
      if (!deadline) return false
      const diff = new Date(deadline) - new Date()
      return diff > 0 && diff < 3 * 86_400_000
    }

    function approvalBadge(s) {
      return { Pending: 'bg-warning text-dark', Approved: 'bg-success', Rejected: 'bg-danger' }[s]
        ?? 'bg-secondary'
    }

    function statusBadge(s) {
      return { Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-primary' }[s]
        ?? 'bg-secondary'
    }

    onMounted(init)

    return {
      store, router, companyId,
      company, drives, loading, loadingDrives,
      busy, driveBusy, error, toast,
      openCount, closedCount, completedCount,
      pendingDriveCount, totalApplicants,
      handleCompanyPatch, handleDrivePatch,
      fmtDate, initials, isUrgent, approvalBadge, statusBadge,
    }
  },
}
</script>

<style scoped>
.company-avatar-lg {
  width: 64px; height: 64px; border-radius: 12px;
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  color: #fff; display: flex; align-items: center;
  justify-content: center; font-size: 1.4rem; font-weight: 700; flex-shrink: 0;
}
.recruiter-avatar {
  width: 40px; height: 40px; border-radius: 50%;
  background: #e9ecef; color: #495057;
  display: flex; align-items: center; justify-content: center;
  font-size: .8rem; font-weight: 700; flex-shrink: 0;
}
.info-block {
  padding: .75rem; background: #f8f9fa; border-radius: 8px; height: 100%;
}
.btn-xs {
  padding: .15rem .4rem; font-size: .75rem; line-height: 1.4; border-radius: .25rem;
}
.table th {
  font-size: .8rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d; white-space: nowrap;
}
.card-header h6 { font-size: .9rem; }
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }
</style>
