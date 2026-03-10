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
        <p class="text-muted small">Loading companies…</p>
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
            <h5 class="fw-bold mb-0 lh-1">Companies</h5>
            <small class="text-muted">
              {{ filtered.length }} of {{ store.companies.length }} shown
            </small>
          </div>
        </div>

        <!-- Summary chips -->
        <div class="d-flex gap-2 flex-wrap align-items-center">
          <div class="summary-chip">
            <i class="bi bi-building text-primary me-1"></i>
            <strong>{{ store.companies.length }}</strong>
            <span class="chip-label ms-1">Total</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-hourglass-split text-warning me-1"></i>
            <strong class="text-warning">
              {{ store.pendingCompanies?.length ?? pendingCount }}
            </strong>
            <span class="chip-label ms-1">Pending</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-check-circle-fill text-success me-1"></i>
            <strong>{{ store.approvedCompanies?.length ?? approvedCount }}</strong>
            <span class="chip-label ms-1">Approved</span>
          </div>
          <div class="summary-chip">
            <i class="bi bi-x-circle-fill text-danger me-1"></i>
            <strong>{{ store.rejectedCompanies?.length ?? rejectedCount }}</strong>
            <span class="chip-label ms-1">Rejected</span>
          </div>
          <button class="btn btn-outline-primary btn-sm ms-2"
                  :disabled="store.loadingCompanies"
                  @click="store.fetchCompanies(true)">
            <span v-if="store.loadingCompanies"
                  class="spinner-border spinner-border-sm"></span>
            <i v-else class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- ── Master-Detail ──────────────────────────────────── -->
      <div class="master-detail">

        <!-- ════ LEFT — Company list ════ -->
        <div class="list-panel">

          <!-- Filters -->
          <div class="p-2 border-bottom bg-white sticky-top">
            <div class="input-group input-group-sm mb-2">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input class="form-control border-start-0 ps-0"
                     v-model="search"
                     placeholder="Company, recruiter, email…" />
              <button v-if="search" class="btn btn-outline-secondary"
                      @click="search = ''">
                <i class="bi bi-x"></i>
              </button>
            </div>
            <div class="d-flex gap-1 mb-1">
              <select class="form-select form-select-sm" v-model="statusFilter">
                <option value="">All Status</option>
                <option>Pending</option>
                <option>Approved</option>
                <option>Rejected</option>
              </select>
              <select class="form-select form-select-sm" v-model="industryFilter">
                <option value="">All Industries</option>
                <option v-for="i in industries" :key="i" :value="i">{{ i }}</option>
              </select>
            </div>
            <div class="d-flex align-items-center justify-content-between">
              <small class="text-muted">{{ filtered.length }} companies</small>
              <button v-if="search || statusFilter || industryFilter"
                      class="btn btn-outline-secondary btn-sm"
                      @click="search=''; statusFilter=''; industryFilter=''">
                <i class="bi bi-x me-1"></i>Clear
              </button>
            </div>
          </div>

          <!-- Empty -->
          <div v-if="!filtered.length"
               class="text-center py-5 px-3 text-muted">
            <i class="bi bi-building fs-1 d-block mb-2 opacity-25"></i>
            <small>No companies match filters</small>
          </div>

          <!-- Company rows -->
          <button v-for="c in filtered" :key="c.id"
                  class="applicant-row"
                  :class="{ 'row-active': selectedId === c.id }"
                  @click="selectCompany(c)">
            <div class="row-logo">
              <img v-if="c.logo_url" :src="c.logo_url"
                   class="w-100 h-100 rounded-2"
                   style="object-fit:cover"
                   @error="c.logo_url = null" />
              <span v-else class="fw-bold" style="font-size:.7rem">
                {{ initials(c.company_name) }}
              </span>
            </div>
            <div class="row-info">
              <div class="d-flex align-items-center justify-content-between gap-1 mb-1">
                <span class="fw-semibold small text-truncate" style="max-width:120px">
                  {{ c.company_name || '—' }}
                </span>
                <span class="badge flex-shrink-0"
                      style="font-size:.6rem"
                      :class="approvalBadge(c.approval_status)">
                  {{ c.approval_status }}
                </span>
                <!-- FIX: was company.active (detail ref) inside v-for="c" loop → always undefined -->
                <!-- isActive() normalises "True"/"False" strings from Python _attr serialisation -->
                <span class="badge flex-shrink-0"
                      style="font-size:.6rem"
                      :class="isActive(c.active) ? 'bg-success' : 'bg-danger'">
                  {{ isActive(c.active) ? 'Active' : 'Blocked' }}
                </span>
              </div>
              <small class="text-muted text-truncate d-block" style="max-width:160px">
                {{ c.recruiter_name || c.recruiter_email || '—' }}
              </small>
              <div class="d-flex align-items-center justify-content-between mt-1">
                <small class="text-muted">{{ c.industry || '—' }}</small>
                <small class="text-muted flex-shrink-0">
                  {{ store.driveCountByCompany?.[c.id] ?? 0 }}
                  <i class="bi bi-briefcase ms-1"></i>
                </small>
              </div>
            </div>
          </button>

        </div>

        <!-- ════ RIGHT — Company detail ════ -->
        <div class="detail-panel bg-light">

          <!-- Empty state -->
          <div v-if="!selectedId"
               class="h-100 d-flex flex-column align-items-center
                      justify-content-center text-center p-4">
            <div class="empty-illustration mb-4">
              <i class="bi bi-building"></i>
            </div>
            <h5 class="fw-bold text-muted mb-1">Select a company</h5>
            <p class="text-muted small mb-0">
              Click any row to view the company profile, manage drives,
              and take admin actions.
            </p>
          </div>

          <!-- Detail loading -->
          <div v-else-if="detailLoading"
               class="h-100 d-flex align-items-center justify-content-center">
            <div class="text-center">
              <div class="spinner-border text-primary mb-2"></div>
              <p class="text-muted small">Loading company…</p>
            </div>
          </div>

          <!-- Company loaded -->
          <div v-else-if="company" class="detail-scroll">

            <!-- ── Profile header ────────────────────────── -->
            <div class="detail-header bg-white border-bottom p-4">
              <div class="d-flex align-items-center
                          justify-content-between flex-wrap gap-3">
                <div class="d-flex align-items-center gap-3">
                  <img v-if="company.logo_url"
                       :src="company.logo_url"
                       class="rounded-3 border"
                       style="width:60px;height:60px;object-fit:cover"
                       @error="company.logo_url = null" />
                  <div v-else class="company-avatar">
                    {{ initials(company.company_name) }}
                  </div>
                  <div>
                    <h5 class="fw-bold mb-1">
                      {{ company.company_name || '—' }}
                    </h5>
                    <p class="text-muted small mb-1">
                      <i class="bi bi-briefcase me-1"></i>
                      {{ company.industry || 'Industry not set' }}
                      <span v-if="company.location" class="ms-2">
                        <i class="bi bi-geo-alt me-1"></i>{{ company.location }}
                      </span>
                    </p>
                    <a v-if="company.website"
                       :href="company.website" target="_blank"
                       class="small text-primary text-decoration-none">
                      <i class="bi bi-link-45deg me-1"></i>{{ company.website }}
                    </a>
                  </div>
                </div>
                <div class="d-flex gap-2">
                  <span class="badge fs-6 px-3 py-2"
                        :class="approvalBadge(company.approval_status)">
                    {{ company.approval_status ?? 'Unknown' }}
                  </span>
                  <!-- isActive() handles "True"/"False" string from backend -->
                  <span class="badge fs-6 px-3 py-2"
                        :class="isActive(company.active) ? 'bg-success' : 'bg-danger'">
                    {{ isActive(company.active) ? 'Active' : 'Blocked' }}
                  </span>
                </div>
              </div>
            </div>

            <!-- ── Two-column body ───────────────────────── -->
            <div class="row g-0">

              <!-- Left: identity + drives table -->
              <div class="col-lg-7 p-4 d-flex flex-column gap-4">

                <!-- Identity card -->
                <div class="card border-0 shadow-sm">
                  <div class="card-body p-4">
                    <h6 class="section-label">Company Details</h6>
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
                             class="text-primary text-decoration-none small">
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
                      <div class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">Registered</small>
                          <strong>{{ fmtDate(company.created_at) }}</strong>
                        </div>
                      </div>
                      <div v-if="company.verified_at" class="col-md-6">
                        <div class="info-block">
                          <small class="text-muted d-block">Approved On</small>
                          <strong>{{ fmtDate(company.verified_at) }}</strong>
                        </div>
                      </div>
                      <div v-if="company.description" class="col-12">
                        <div class="info-block">
                          <small class="text-muted d-block mb-1">About</small>
                          <p class="mb-0 small" style="white-space:pre-wrap">
                            {{ company.description }}
                          </p>
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
                      Placement Drives
                      <span class="badge bg-primary bg-opacity-10 text-primary ms-1">
                        {{ drives.length }}
                      </span>
                    </h6>
                    <div class="d-flex gap-2 align-items-center">
                      <span class="badge bg-success">{{ openCount }} Open</span>
                      <span class="badge bg-secondary">{{ closedCount + completedCount }} Closed</span>
                      <button class="btn btn-sm btn-outline-secondary"
                              :disabled="loadingDrives"
                              @click="store.fetchCompanyDrives(selectedId, true)">
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
                      <i class="bi bi-folder-x d-block mb-1 fs-4 opacity-25"></i>
                      No drives posted yet.
                    </div>
                    <div v-else class="table-responsive">
                      <table class="table table-hover mb-0 align-middle">
                        <thead class="table-light">
                          <tr>
                            <th>Title</th>
                            <th>Status</th>
                            <th>Approval</th>
                            <th>Deadline</th>
                            <th class="text-end">Apps</th>
                            <th class="text-end">Actions</th>
                          </tr>
                        </thead>
                        <tbody>
                          <tr v-for="d in drives" :key="d.id">
                            <td>
                              <router-link :to="`/admin/${d.company_id}/drives/${d.id}`"
                                           class="fw-semibold text-decoration-none small">
                                {{ d.title }}
                              </router-link>
                              <div v-if="d.location" class="small text-muted">
                                <i class="bi bi-geo-alt me-1"></i>{{ d.location }}
                              </div>
                            </td>
                            <td>
                              <span class="badge" :class="statusBadge(d.status)">
                                {{ d.status }}
                              </span>
                            </td>
                            <td>
                              <span class="badge"
                                    :class="approvalBadge(d.admin_approval_status || 'Pending')">
                                {{ d.admin_approval_status || 'Pending' }}
                              </span>
                            </td>
                            <td>
                              <span :class="{
                                'text-danger fw-semibold': isUrgent(d.application_deadline)
                              }" class="small">
                                {{ fmtDate(d.application_deadline) }}
                              </span>
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
                                        title="Approve drive"
                                        @click="handleDrivePatch(d, { admin_approval_status: 'Approved' })">
                                  <i class="bi bi-check"></i>
                                </button>
                                <button v-if="d.admin_approval_status !== 'Rejected'"
                                        class="btn btn-xs btn-outline-danger"
                                        :disabled="driveBusy[d.id]"
                                        title="Reject drive"
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

              <!-- Right: admin actions + stats + recruiter -->
              <div class="col-lg-5 p-4 d-flex flex-column gap-3 border-start-lg">

                <!-- Admin Actions -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-shield-check me-2 text-primary"></i>
                      Admin Actions
                    </h6>
                  </div>
                  <div class="card-body p-3 d-flex flex-column gap-2">

                    <p class="action-group-label">Approval</p>

                    <button v-if="company.approval_status !== 'Approved'"
                            class="btn btn-success btn-sm"
                            :disabled="busy"
                            @click="handleCompanyPatch({ approval_status: 'Approved' })">
                      <span v-if="busy"
                            class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-check-circle me-1"></i>
                      {{ company.approval_status === 'Rejected'
                          ? 'Approve Now' : 'Approve Company' }}
                    </button>

                    <button v-if="company.approval_status !== 'Rejected'"
                            class="btn btn-outline-danger btn-sm"
                            :disabled="busy"
                            @click="handleCompanyPatch({ approval_status: 'Rejected' })">
                      <i class="bi bi-x-circle me-1"></i>
                      {{ company.approval_status === 'Approved'
                          ? 'Revoke Approval' : 'Reject Company' }}
                    </button>

                    <p class="action-group-label mt-2">Account</p>

                    <!-- FIX: !isActive(company.active) sends a proper JS boolean true/false
                         instead of !string which was always false for "False" strings -->
                    <button class="btn btn-sm"
                            :class="isActive(company.active) ? 'btn-outline-danger' : 'btn-outline-success'"
                            :disabled="busy"
                            @click="handleCompanyPatch({ active: !isActive(company.active) })">
                      <span v-if="busy"
                            class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi me-1"
                         :class="isActive(company.active) ? 'bi-slash-circle' : 'bi-check-circle'"></i>
                      {{ isActive(company.active) ? 'Block Company' : 'Unblock Company' }}
                    </button>

                    <p class="action-group-label mt-2">Danger Zone</p>

                    <button class="btn btn-danger btn-sm"
                            :disabled="busy"
                            @click="handleCompanyDelete">
                      <i class="bi bi-trash me-1"></i>
                      Delete Company
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
                  <ul class="list-group list-group-flush">
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Total Drives</span>
                      <strong>{{ drives.length }}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Open</span>
                      <span class="badge bg-success">{{ openCount }}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Closed / Completed</span>
                      <span class="badge bg-secondary">{{ closedCount + completedCount }}</span>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Total Applicants</span>
                      <strong>{{ totalApplicants }}</strong>
                    </li>
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                      <span class="text-muted small">Pending Drive Approvals</span>
                      <span class="badge"
                            :class="pendingDriveCount > 0 ? 'bg-warning text-dark' : 'bg-success'">
                        {{ pendingDriveCount }}
                      </span>
                    </li>
                  </ul>
                </div>

                <!-- Recruiter contact -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-person me-2 text-info"></i>
                      Recruiter Contact
                    </h6>
                  </div>
                  <div class="card-body p-3">
                    <div class="d-flex align-items-center gap-3">
                      <div class="recruiter-avatar">
                        {{ initials(company.recruiter_name) }}
                      </div>
                      <div>
                        <div class="fw-semibold small">
                          {{ company.recruiter_name || '—' }}
                        </div>
                        <a v-if="company.recruiter_email"
                           :href="`mailto:${company.recruiter_email}`"
                           class="small text-primary text-decoration-none d-block">
                          {{ company.recruiter_email }}
                        </a>
                        <a v-if="company.phone"
                           :href="`tel:${company.phone}`"
                           class="small text-muted text-decoration-none">
                          <i class="bi bi-telephone me-1"></i>{{ company.phone }}
                        </a>
                      </div>
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
import { useRouter }      from 'vue-router'
import { useAdminStore }  from '@/stores/adminStore'
import { useUserStore }   from '@/stores/userStore'

const router    = useRouter()
const store     = useAdminStore()
const userStore = useUserStore()

// ── Page state ────────────────────────────────────────────────
const pageLoading = ref(true)
const toast       = reactive({ show: false, type: 'success', message: '' })

// ── List filters ──────────────────────────────────────────────
const search         = ref('')
const statusFilter   = ref('')
const industryFilter = ref('')

// ── Selected company ──────────────────────────────────────────
const selectedId    = ref(null)
const detailLoading = ref(false)
const busy          = ref(false)
const driveBusy     = reactive({})

const company       = computed(() => store.companyDetail?.[selectedId.value] ?? null)
const drives        = computed(() => store.companyDrives?.[selectedId.value] ?? [])
const loadingDrives = computed(() => !!store.loadingCompanyDrives?.[selectedId.value])

// ── Drive stats ───────────────────────────────────────────────
const openCount       = computed(() => drives.value.filter(d => d.status === 'Open').length)
const closedCount     = computed(() => drives.value.filter(d => d.status === 'Closed').length)
const completedCount  = computed(() => drives.value.filter(d => d.status === 'Completed').length)
const totalApplicants = computed(() =>
  drives.value.reduce((sum, d) => sum + (d.total_applications ?? 0), 0)
)
const pendingDriveCount = computed(() =>
  drives.value.filter(d => !d.admin_approval_status ||
                            d.admin_approval_status === 'Pending').length
)

// ── Summary counts ────────────────────────────────────────────
const pendingCount  = computed(() => store.companies.filter(c => c.approval_status === 'Pending').length)
const approvedCount = computed(() => store.companies.filter(c => c.approval_status === 'Approved').length)
const rejectedCount = computed(() => store.companies.filter(c => c.approval_status === 'Rejected').length)

// ── Industries for filter ─────────────────────────────────────
const industries = computed(() =>
  [...new Set(store.companies.map(c => c.industry).filter(Boolean))].sort()
)

// ── Filtered list ─────────────────────────────────────────────
const filtered = computed(() =>
  store.companies.filter(c => {
    const q = search.value.toLowerCase()
    const matchSearch =
      !q ||
      c.company_name?.toLowerCase().includes(q)    ||
      c.recruiter_name?.toLowerCase().includes(q)  ||
      c.recruiter_email?.toLowerCase().includes(q) ||
      c.location?.toLowerCase().includes(q)
    const matchStatus   = !statusFilter.value   || c.approval_status === statusFilter.value
    const matchIndustry = !industryFilter.value || c.industry === industryFilter.value
    return matchSearch && matchStatus && matchIndustry
  })
)

// ── Load ──────────────────────────────────────────────────────
onMounted(async () => {
  try {
    await Promise.all([
      store.companies.length ? null : store.fetchCompanies(),
      store.drives?.length   ? null : store.fetchDrives?.(),
    ])
  } finally { pageLoading.value = false }
})

async function selectCompany(c) {
  selectedId.value    = c.id
  detailLoading.value = true
  try {
    await Promise.all([
      store.fetchCompany(c.id),
      store.fetchCompanyDrives(c.id),
    ])
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to load company.')
  } finally { detailLoading.value = false }
}

// ── Admin actions ─────────────────────────────────────────────
async function handleCompanyPatch(payload) {
  busy.value = true
  try {
    await store.patchCompany(selectedId.value, payload)
    // FIX: determine toast message using isActive() for the active field
    // so "True"/"False" strings are handled correctly, not raw payload.active
    let msg
    if ('approval_status' in payload) {
      msg = `Company ${payload.approval_status === 'Approved' ? 'approved' : 'rejected'}.`
    } else if ('active' in payload) {
      msg = `Company ${payload.active ? 'unblocked' : 'blocked'}.`
    } else {
      msg = 'Company updated.'
    }
    showToast('success', msg)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally { busy.value = false }
}

async function handleCompanyDelete() {
  if (!confirm('Delete this company? This cannot be undone.')) return
  busy.value = true
  try {
    await store.deleteCompany(selectedId.value)
    showToast('success', 'Company deleted.')
    selectedId.value = null
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to delete company.')
  } finally { busy.value = false }
}

async function handleDrivePatch(drive, payload) {
  driveBusy[drive.id] = true
  try {
    await store.patchDrive(drive.id, payload, selectedId.value)
    const msg = 'admin_approval_status' in payload
      ? `Drive ${payload.admin_approval_status === 'Approved' ? 'approved' : 'rejected'}.`
      : `Drive status changed to ${payload.status}.`
    showToast('success', msg)
  } catch (e) {
    showToast('danger', e?.message ?? 'Drive action failed.')
  } finally { driveBusy[drive.id] = false }
}

// ── Helpers ───────────────────────────────────────────────────

// FIX: Python _attr serialises bool as the string "True"/"False".
// In JS every non-empty string is truthy → !"False" === false → always Active.
// isActive() normalises all shapes: boolean true/false, integer 1/0, string "True"/"False".
function isActive(val) {
  if (val === null || val === undefined) return true
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
.row-logo {
  width:38px; height:38px; border-radius:8px; flex-shrink:0;
  background:#e9ecef; color:#495057;
  display:flex; align-items:center; justify-content:center;
  overflow:hidden;
}

.company-avatar {
  width:60px; height:60px; border-radius:12px; flex-shrink:0;
  background:linear-gradient(135deg,#0d6efd,#0a58ca);
  color:#fff; display:flex; align-items:center;
  justify-content:center; font-size:1.3rem; font-weight:700;
}
.recruiter-avatar {
  width:40px; height:40px; border-radius:50%;
  background:#e9ecef; color:#495057;
  display:flex; align-items:center; justify-content:center;
  font-size:.8rem; font-weight:700; flex-shrink:0;
}

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
.action-group-label {
  font-size:.65rem; font-weight:700;
  text-transform:uppercase; letter-spacing:.07em;
  color:#6c757d; margin-bottom:0;
}
@media (min-width:992px) { .border-start-lg { border-left:1px solid #dee2e6; } }

.btn-xs { padding:.15rem .4rem; font-size:.75rem; line-height:1.4; border-radius:.25rem; }
.table th {
  font-size:.75rem; text-transform:uppercase;
  letter-spacing:.04em; color:#6c757d; white-space:nowrap;
}

.toast-fixed {
  position:fixed; top:1rem; right:1rem; z-index:2000;
  min-width:280px; border-radius:10px;
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