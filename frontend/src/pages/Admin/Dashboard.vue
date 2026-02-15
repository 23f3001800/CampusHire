<template>
  <div class="dashboard bg-light min-vh-100 py-4">
    <div class="container-fluid px-4">

      <!-- Header -->
      <div class="d-flex justify-content-between align-items-center mb-4">
        <div>
          <h3 class="fw-bold mb-0">Admin Dashboard</h3>
          <small class="text-muted">Full platform overview</small>
        </div>
        <button class="btn btn-outline-secondary btn-sm" :disabled="adminStore.loading" @click="adminStore.fetchAll()">
          <span v-if="adminStore.loading" class="spinner-border spinner-border-sm me-1"></span>
          <i v-else class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>

      <!-- Error banner -->
      <div v-if="adminStore.error" class="alert alert-danger d-flex align-items-center mb-4">
        <i class="bi bi-exclamation-triangle-fill me-2"></i>{{ adminStore.error }}
        <button type="button" class="btn-close ms-auto" @click="adminStore.error = null"></button>
      </div>

      <!-- Stats row -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-lg-2" v-for="s in statCards" :key="s.label">
          <div class="stat-card text-white h-100" :class="s.bg">
            <i :class="`bi ${s.icon} fs-3 opacity-75`"></i>
            <div class="mt-1">
              <div class="fs-4 fw-bold lh-1">{{ s.value }}</div>
              <small class="opacity-90">{{ s.label }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-0 border-bottom">
        <li class="nav-item" v-for="t in tabs" :key="t.key">
          <a class="nav-link px-4 py-3" :class="{ active: activeTab === t.key }"
            @click.prevent="activeTab = t.key" href="#" role="tab">
            <i :class="`bi ${t.icon} me-1`"></i>{{ t.label }}
            <span v-if="t.badge" class="badge bg-danger rounded-pill ms-1">{{ t.badge }}</span>
          </a>
        </li>
      </ul>

      <div class="tab-content bg-white rounded-bottom shadow-sm p-4">

        <!-- ── PENDING APPROVALS ─────────────────────────────────────── -->
        <div v-show="activeTab === 'pending'">
          <div v-if="!adminStore.pendingCompanies.length" class="empty-state py-5">
            <i class="bi bi-check-circle-fill text-success fs-1 d-block mb-2"></i>
            <p class="text-muted mb-0">All companies reviewed — no pending approvals.</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Company</th><th>Recruiter</th><th>Industry</th>
                  <th>Location</th><th>Registered</th><th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in adminStore.pendingCompanies" :key="c.id">
                  <td>
                    <div class="d-flex align-items-center gap-2">
                      <img v-if="c.logo_url" :src="c.logo_url" class="rounded"
                        style="width:32px;height:32px;object-fit:cover" />
                      <div v-else class="company-avatar">{{ initials(c.company_name) }}</div>
                      <strong>{{ c.company_name || '—' }}</strong>
                    </div>
                  </td>
                  <td>
                    {{ c.recruiter_name }}<br>
                    <small class="text-muted">{{ c.recruiter_email }}</small>
                  </td>
                  <td>{{ c.industry || '—' }}</td>
                  <td>{{ c.location || '—' }}</td>
                  <td><small>{{ formatDate(c.created_at) }}</small></td>
                  <td class="text-end">
                    <button class="btn btn-success btn-sm me-1"
                      :disabled="rowBusy[c.id]" @click="approve(c.id)">
                      <span v-if="rowBusy[c.id]" class="spinner-border spinner-border-sm"></span>
                      <template v-else><i class="bi bi-check-lg me-1"></i>Approve</template>
                    </button>
                    <button class="btn btn-outline-danger btn-sm"
                      :disabled="rowBusy[c.id]" @click="reject(c.id)">
                      <i class="bi bi-x-lg me-1"></i>Reject
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── ALL COMPANIES ────────────────────────────────────────── -->
        <div v-show="activeTab === 'companies'">
          <div class="d-flex gap-2 mb-3">
            <div class="input-group" style="max-width:300px">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input v-model="companySearch" type="text"
                class="form-control border-start-0" placeholder="Search companies…" />
            </div>
            <select v-model="companyFilter" class="form-select" style="max-width:170px">
              <option value="">All Statuses</option>
              <option value="Pending">Pending</option>
              <option value="Approved">Approved</option>
              <option value="Rejected">Rejected</option>
            </select>
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Company</th><th>Recruiter</th><th>Industry</th>
                  <th>Drives</th><th>Status</th><th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredCompanies.length">
                  <td colspan="6" class="text-center text-muted py-4">No companies found</td>
                </tr>
                <tr v-for="c in filteredCompanies" :key="c.id">
                  <td>
                    <strong>{{ c.company_name || '—' }}</strong><br>
                    <small class="text-muted">{{ c.website || '' }}</small>
                  </td>
                  <td>
                    {{ c.recruiter_name }}<br>
                    <small class="text-muted">{{ c.recruiter_email }}</small>
                  </td>
                  <td>{{ c.industry || '—' }}</td>
                  <td>
                    <span class="badge bg-light text-dark">
                      {{ drivesForCompany(c.id) }}
                    </span>
                  </td>
                  <td>
                    <span class="badge" :class="approvalBadge(c.approval_status)">
                      {{ c.approval_status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button v-if="c.approval_status === 'Pending'"
                      class="btn btn-success btn-sm me-1" :disabled="rowBusy[c.id]"
                      @click="approve(c.id)">
                      <i class="bi bi-check-lg"></i>
                    </button>
                    <button v-if="c.approval_status === 'Pending'"
                      class="btn btn-outline-danger btn-sm" :disabled="rowBusy[c.id]"
                      @click="reject(c.id)">
                      <i class="bi bi-x-lg"></i>
                    </button>
                    <span v-if="c.approval_status !== 'Pending'" class="text-muted small">—</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── STUDENTS ──────────────────────────────────────────────── -->
        <div v-show="activeTab === 'students'">
          <div class="d-flex gap-2 mb-3">
            <div class="input-group" style="max-width:300px">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input v-model="studentSearch" type="text"
                class="form-control border-start-0" placeholder="Search students…" />
            </div>
            <select v-model="studentFilter" class="form-select" style="max-width:170px">
              <option value="">All Students</option>
              <option value="active">Active</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Student</th><th>Roll No.</th><th>Branch</th>
                  <th>CGPA</th><th>Grad Year</th><th>Status</th><th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredStudents.length">
                  <td colspan="7" class="text-center text-muted py-4">No students found</td>
                </tr>
                <tr v-for="s in filteredStudents" :key="s.id">
                  <td>
                    <strong>{{ s.name }}</strong><br>
                    <small class="text-muted">{{ s.email }}</small>
                  </td>
                  <td>{{ s.roll_number || '—' }}</td>
                  <td>{{ s.branch || '—' }}</td>
                  <td>
                    <span v-if="s.cgpa" class="badge"
                      :class="s.cgpa >= 8 ? 'bg-success' : s.cgpa >= 6 ? 'bg-warning text-dark' : 'bg-danger'">
                      {{ s.cgpa }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>{{ s.graduation_year || '—' }}</td>
                  <td>
                    <span class="badge" :class="s.active !== false ? 'bg-success' : 'bg-secondary'">
                      {{ s.active !== false ? 'Active' : 'Blocked' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button v-if="s.active !== false"
                      class="btn btn-warning btn-sm" :disabled="rowBusy[s.user_id]"
                      @click="blockStudent(s.user_id)">
                      <i class="bi bi-slash-circle me-1"></i>Block
                    </button>
                    <button v-else
                      class="btn btn-success btn-sm" :disabled="rowBusy[s.user_id]"
                      @click="unblockStudent(s.user_id)">
                      <i class="bi bi-check-circle me-1"></i>Unblock
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── PLACEMENT DRIVES ──────────────────────────────────────── -->
        <div v-show="activeTab === 'drives'">
          <div class="d-flex gap-2 mb-3">
            <div class="input-group" style="max-width:300px">
              <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
              <input v-model="driveSearch" type="text"
                class="form-control border-start-0" placeholder="Search drives…" />
            </div>
            <select v-model="driveFilter" class="form-select" style="max-width:170px">
              <option value="">All Statuses</option>
              <option value="Open">Open</option>
              <option value="Closed">Closed</option>
              <option value="Completed">Completed</option>
            </select>
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Title</th><th>Company</th><th>Type</th>
                  <th>Drive Date</th><th>Deadline</th><th>Applicants</th>
                  <th>Status</th><th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="!filteredDrives.length">
                  <td colspan="8" class="text-center text-muted py-4">No drives found</td>
                </tr>
                <tr v-for="d in filteredDrives" :key="d.id">
                  <td><strong>{{ d.title }}</strong></td>
                  <td>{{ d.company_name }}</td>
                  <td>
                    <span class="badge bg-light text-dark">{{ d.job_type || '—' }}</span>
                  </td>
                  <td><small>{{ formatDate(d.drive_date) }}</small></td>
                  <td>
                    <small :class="isUrgent(d.application_deadline) ? 'text-danger fw-bold' : ''">
                      {{ formatDate(d.application_deadline) }}
                    </small>
                  </td>
                  <td>
                    <span class="badge bg-primary">{{ d.total_applications }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="driveBadge(d.status)">{{ d.status }}</span>
                  </td>
                  <td class="text-end">
                    <button class="btn btn-outline-warning btn-sm me-1"
                      :disabled="rowBusy[d.id]"
                      :title="d.status === 'Open' ? 'Close drive' : 'Reopen drive'"
                      @click="toggleDrive(d.id)">
                      <i class="bi" :class="d.status === 'Open' ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
                    </button>
                    <button class="btn btn-outline-danger btn-sm"
                      :disabled="rowBusy[d.id]"
                      title="Delete drive permanently"
                      @click="deleteDrive(d.id)">
                      <i class="bi bi-trash"></i>
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- ── PLACEMENTS ──────────────────────────────────────────────── -->
        <div v-show="activeTab === 'placements'">
          <!-- Summary chips -->
          <div class="d-flex flex-wrap gap-2 mb-4">
            <span class="badge fs-6 bg-primary px-3 py-2">
              Total: {{ adminStore.dashboardStats.total_placements ?? 0 }}
            </span>
            <span class="badge fs-6 bg-warning text-dark px-3 py-2">
              Offered: {{ adminStore.dashboardStats.placements_offered ?? 0 }}
            </span>
            <span class="badge fs-6 bg-success px-3 py-2">
              Joined: {{ adminStore.dashboardStats.placements_joined ?? 0 }}
            </span>
            <span class="badge fs-6 bg-danger px-3 py-2">
              Declined: {{ adminStore.dashboardStats.placements_declined ?? 0 }}
            </span>
          </div>

          <div v-if="!adminStore.placements.length" class="empty-state py-5">
            <i class="bi bi-trophy fs-1 text-muted d-block mb-2"></i>
            <p class="text-muted">No placements recorded yet</p>
          </div>
          <div v-else class="table-responsive">
            <table class="table table-hover align-middle mb-0">
              <thead class="table-light">
                <tr>
                  <th>Student</th><th>Company</th><th>Role</th>
                  <th>Package</th><th>Status</th><th>Joining Date</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in adminStore.placements" :key="p.id">
                  <td>
                    <strong>{{ p.student_name }}</strong>
                  </td>
                  <td>{{ p.company_name }}</td>
                  <td>{{ p.position_title }}</td>
                  <td>
                    <span v-if="p.salary" class="text-success fw-bold">
                      {{ formatSalary(p.salary, p.currency) }}
                    </span>
                    <span v-else class="text-muted">—</span>
                  </td>
                  <td>
                    <span class="badge"
                      :class="{ Offered: 'bg-warning text-dark', Joined: 'bg-success', Declined: 'bg-danger' }[p.status] || 'bg-secondary'">
                      {{ p.status }}
                    </span>
                  </td>
                  <td><small>{{ p.joining_date ? formatDate(p.joining_date) : '—' }}</small></td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div><!-- /tab-content -->
    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/adminStore'

export default {
  name: 'AdminDashboard',

  setup() {
    return { adminStore: useAdminStore() }
  },

  data: () => ({
    activeTab:     'pending',
    rowBusy:       {},          // { [id]: true } — per-row loading spinners

    companySearch: '',
    companyFilter: '',

    studentSearch: '',
    studentFilter: '',

    driveSearch:   '',
    driveFilter:   '',
  }),

  computed: {
    tabs() {
      const s = this.adminStore.dashboardStats
      return [
        { key: 'pending',    icon: 'bi-hourglass-split', label: 'Pending Approvals',
          badge: s.pending_companies || null },
        { key: 'companies',  icon: 'bi-building',  label: 'Companies' },
        { key: 'students',   icon: 'bi-people',    label: 'Students' },
        { key: 'drives',     icon: 'bi-briefcase', label: 'Placement Drives' },
        { key: 'placements', icon: 'bi-trophy',    label: 'Placements' },
      ]
    },

    statCards() {
      const s = this.adminStore.dashboardStats
      return [
        { label: 'Students',          value: s.total_students    ?? 0, bg: 'bg-primary',   icon: 'bi-mortarboard-fill' },
        { label: 'Companies',         value: s.total_companies   ?? 0, bg: 'bg-success',   icon: 'bi-building' },
        { label: 'Pending Approvals', value: s.pending_companies ?? 0, bg: 'bg-warning',   icon: 'bi-hourglass-split' },
        { label: 'Open Drives',       value: s.open_drives       ?? 0, bg: 'bg-info',      icon: 'bi-briefcase-fill' },
        { label: 'Placed Students',   value: s.total_placements  ?? 0, bg: 'bg-success',   icon: 'bi-trophy-fill' },
        { label: 'Applications',      value: s.total_applications?? 0, bg: 'bg-secondary', icon: 'bi-file-earmark-text-fill' },
      ]
    },

    filteredCompanies() {
      return this.adminStore.companies.filter(c => {
        const q = this.companySearch.toLowerCase()
        const matchSearch = !q ||
          c.company_name?.toLowerCase().includes(q) ||
          c.recruiter_name?.toLowerCase().includes(q) ||
          c.recruiter_email?.toLowerCase().includes(q)
        const matchFilter = !this.companyFilter || c.approval_status === this.companyFilter
        return matchSearch && matchFilter
      })
    },

    filteredStudents() {
      return this.adminStore.students.filter(s => {
        const q = this.studentSearch.toLowerCase()
        const matchSearch = !q ||
          s.name?.toLowerCase().includes(q) ||
          s.email?.toLowerCase().includes(q) ||
          s.roll_number?.toLowerCase().includes(q) ||
          s.branch?.toLowerCase().includes(q)
        const matchFilter =
          !this.studentFilter ||
          (this.studentFilter === 'active'  && s.active !== false) ||
          (this.studentFilter === 'blocked' && s.active === false)
        return matchSearch && matchFilter
      })
    },

    filteredDrives() {
      return this.adminStore.drives.filter(d => {
        const q = this.driveSearch.toLowerCase()
        const matchSearch = !q ||
          d.title?.toLowerCase().includes(q) ||
          d.company_name?.toLowerCase().includes(q)
        const matchFilter = !this.driveFilter || d.status === this.driveFilter
        return matchSearch && matchFilter
      })
    },
  },

  async mounted() {
    await this.adminStore.fetchAll()
  },

  methods: {
    // ── Company actions ───────────────────────────────────────────────────
    async approve(companyId) {
      this.rowBusy[companyId] = true
      try   { await this.adminStore.approveCompany(companyId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[companyId] = false }
    },

    async reject(companyId) {
      if (!confirm('Reject this company? They will be notified.')) return
      this.rowBusy[companyId] = true
      try   { await this.adminStore.rejectCompany(companyId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[companyId] = false }
    },

    // ── Student actions ───────────────────────────────────────────────────
    async blockStudent(userId) {
      if (!confirm('Block this student? They will not be able to login.')) return
      this.rowBusy[userId] = true
      try   { await this.adminStore.blockStudent(userId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[userId] = false }
    },

    async unblockStudent(userId) {
      this.rowBusy[userId] = true
      try   { await this.adminStore.unblockStudent(userId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[userId] = false }
    },

    // ── Drive actions ─────────────────────────────────────────────────────
    async toggleDrive(driveId) {
      this.rowBusy[driveId] = true
      try   { await this.adminStore.toggleDriveStatus(driveId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[driveId] = false }
    },

    async deleteDrive(driveId) {
      if (!confirm('Permanently delete this drive? This cannot be undone.')) return
      this.rowBusy[driveId] = true
      try   { await this.adminStore.deleteDrive(driveId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[driveId] = false }
    },

    // ── Utilities ─────────────────────────────────────────────────────────
    drivesForCompany(companyId) {
      return this.adminStore.drives.filter(d => d.company_id === companyId).length
    },

    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },

    isUrgent(deadline) {
      if (!deadline) return false
      const diff = new Date(deadline) - new Date()
      return diff > 0 && diff < 3 * 86400000
    },

    initials(name) {
      return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },

    approvalBadge(s) {
      return { Pending: 'bg-warning text-dark', Approved: 'bg-success', Rejected: 'bg-danger' }[s] || 'bg-secondary'
    },

    driveBadge(s) {
      return { Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-primary' }[s] || 'bg-secondary'
    },

    formatSalary(salary, currency = 'INR') {
      if (!salary) return '—'
      const sym = currency === 'INR' ? '₹' : currency
      return salary >= 100000
        ? `${sym}${(salary / 100000).toFixed(1)} LPA`
        : `${sym}${salary.toLocaleString('en-IN')}`
    },
  },
}
</script>

<style scoped>
.stat-card {
  padding: 1.1rem 1.25rem;
  border-radius: 10px;
  display: flex;
  flex-direction: column;
  gap: .4rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.12);
}
.company-avatar {
  width: 32px; height: 32px; border-radius: 6px;
  background: #e9ecef; color: #495057;
  display: flex; align-items: center; justify-content: center;
  font-size: .7rem; font-weight: 700; flex-shrink: 0;
}
.tab-content { border: 1px solid #dee2e6; border-top: none; }
.empty-state { text-align: center; }
.nav-tabs .nav-link         { color: #6c757d; border: none; border-bottom: 3px solid transparent; padding: .75rem 1.25rem; }
.nav-tabs .nav-link.active  { color: #0d6efd; border-bottom-color: #0d6efd; background: none; font-weight: 600; }
.nav-tabs .nav-link:hover   { color: #0d6efd; background: #f8f9fa; }
.table th { font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; color: #6c757d; }
</style>