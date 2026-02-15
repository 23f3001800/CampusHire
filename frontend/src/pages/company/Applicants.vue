<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container-fluid px-4" style="max-width:1100px">

      <!-- Header -->
      <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <button class="btn btn-outline-secondary btn-sm mb-1" @click="$router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
          <h4 class="fw-bold mb-0 mt-2">{{ drive?.title || 'Drive Applicants' }}</h4>
          <small class="text-muted">
            <i class="bi bi-building me-1"></i>{{ store.companyName }}
            <span v-if="drive" class="ms-2">
              <span class="badge" :class="{ Open: 'bg-success', Closed: 'bg-secondary' }[drive.status] || 'bg-info'">
                {{ drive.status }}
              </span>
            </span>
          </small>
        </div>
        <button class="btn btn-outline-primary btn-sm" @click="refresh">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>

      <!-- Stats strip -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3" v-for="s in statCards" :key="s.label">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-3" :class="s.color">{{ s.value }}</div>
            <small class="text-muted">{{ s.label }}</small>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body d-flex flex-wrap gap-2">
          <div class="input-group" style="max-width:280px">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input v-model="search" class="form-control border-start-0" placeholder="Search name, roll, branch…" />
          </div>
          <select v-model="statusFilter" class="form-select" style="max-width:160px">
            <option value="">All Statuses</option>
            <option value="Applied">Applied</option>
            <option value="Shortlisted">Shortlisted</option>
            <option value="Selected">Selected</option>
            <option value="Rejected">Rejected</option>
          </select>
          <select v-model="sortBy" class="form-select" style="max-width:180px">
            <option value="date_desc">Latest Applied</option>
            <option value="date_asc">Earliest Applied</option>
            <option value="cgpa_desc">Highest CGPA</option>
          </select>
          <div class="ms-auto d-flex gap-2">
            <button class="btn btn-outline-success btn-sm" @click="bulkAction('Shortlisted')"
              :disabled="!selectedIds.length">
              <i class="bi bi-star me-1"></i>Shortlist ({{ selectedIds.length }})
            </button>
            <button class="btn btn-outline-danger btn-sm" @click="bulkAction('Rejected')"
              :disabled="!selectedIds.length">
              <i class="bi bi-x-circle me-1"></i>Reject ({{ selectedIds.length }})
            </button>
          </div>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="!filtered.length" class="text-center py-5">
        <i class="bi bi-people fs-1 text-muted d-block mb-2"></i>
        <p class="text-muted">{{ search || statusFilter ? 'No applicants match your filters' : 'No applications yet' }}</p>
      </div>

      <!-- Table -->
      <div v-else class="card border-0 shadow-sm">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th style="width:40px">
                  <input type="checkbox" class="form-check-input"
                    :checked="allSelected" @change="toggleAll" />
                </th>
                <th>Applicant</th>
                <th>Branch</th>
                <th>CGPA</th>
                <th>Applied</th>
                <th>Status</th>
                <th>Resume</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in filtered" :key="app.id"
                :class="{ 'table-success bg-opacity-10': app.status === 'Selected' }">
                <td>
                  <input type="checkbox" class="form-check-input"
                    :value="app.id" v-model="selectedIds" />
                </td>
                <td>
                  <div class="fw-semibold">{{ app.student_name }}</div>
                  <small class="text-muted">{{ app.student_email }}</small>
                  <div v-if="app.student_roll" class="text-muted" style="font-size:.75rem">
                    Roll: {{ app.student_roll }}
                  </div>
                </td>
                <td>{{ app.student_branch || '—' }}</td>
                <td>
                  <span v-if="app.student_cgpa" class="badge"
                    :class="app.student_cgpa >= 8 ? 'bg-success' : app.student_cgpa >= 6 ? 'bg-warning text-dark' : 'bg-danger'">
                    {{ app.student_cgpa }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td><small>{{ formatDate(app.applied_date) }}</small></td>
                <td>
                  <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
                </td>
                <td>
                  <a v-if="app.resume_link" :href="app.resume_link" target="_blank"
                    class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </a>
                  <span v-else class="text-muted small">None</span>
                </td>
                <td class="text-end">
                  <div class="btn-group btn-group-sm">
                    <button class="btn btn-outline-info"
                      title="View cover letter" :disabled="!app.cover_letter"
                      @click="viewCoverLetter(app)">
                      <i class="bi bi-chat-left-text"></i>
                    </button>
                    <button class="btn btn-outline-success"
                      :disabled="rowBusy[app.id] || app.status === 'Selected'"
                      title="Select" @click="updateStatus(app.id, 'Selected')">
                      <i class="bi bi-trophy"></i>
                    </button>
                    <button class="btn btn-outline-warning text-dark"
                      :disabled="rowBusy[app.id] || app.status === 'Shortlisted'"
                      title="Shortlist" @click="updateStatus(app.id, 'Shortlisted')">
                      <i class="bi bi-star"></i>
                    </button>
                    <button class="btn btn-outline-danger"
                      :disabled="rowBusy[app.id] || app.status === 'Rejected'"
                      title="Reject" @click="updateStatus(app.id, 'Rejected')">
                      <i class="bi bi-x-lg"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Notes modal -->
      <div v-if="noteModal.show" class="modal-backdrop" @click.self="noteModal.show = false">
        <div class="modal-box card shadow-lg border-0 p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Add Note — {{ noteModal.appName }}</h5>
            <button class="btn-close" @click="noteModal.show = false"></button>
          </div>
          <label class="form-label">Internal note (not visible to student)</label>
          <textarea class="form-control mb-3" v-model="noteModal.text" rows="3"></textarea>
          <div class="d-flex gap-2 justify-content-end">
            <button class="btn btn-outline-secondary btn-sm" @click="noteModal.show = false">Cancel</button>
            <button class="btn btn-primary btn-sm" @click="submitNote">Save Note</button>
          </div>
        </div>
      </div>

      <!-- Cover letter modal -->
      <div v-if="coverModal.show" class="modal-backdrop" @click.self="coverModal.show = false">
        <div class="modal-box card shadow-lg border-0 p-4">
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="fw-bold mb-0">Cover Letter — {{ coverModal.appName }}</h5>
            <button class="btn-close" @click="coverModal.show = false"></button>
          </div>
          <p class="text-muted" style="white-space:pre-wrap">{{ coverModal.text || 'No cover letter submitted.' }}</p>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useCompanyStore } from '@/stores/companyStore'
import { useUserStore }    from '@/stores/userStore'

export default {
  name: 'DriveApplicants',

  setup() {
    return { store: useCompanyStore(), userStore: useUserStore() }
  },

  data: () => ({
    search:       '',
    statusFilter: '',
    sortBy:       'date_desc',
    selectedIds:  [],
    rowBusy:      {},
    loading:      false,
    noteModal:    { show: false, appId: null, appName: '', text: '' },
    coverModal:   { show: false, appName: '', text: '' },
  }),

  computed: {
    driveId() { return parseInt(this.$route.params.driveId) },

    drive() { return this.store.getDriveById(this.driveId) },

    applicants() { return this.store.getApplicantsForDrive(this.driveId) },

    stats() { return this.store.getDriveStats(this.driveId) },

    statCards() {
      const s = this.stats
      return [
        { label: 'Total',       value: s.total,       color: 'text-dark'    },
        { label: 'Shortlisted', value: s.shortlisted, color: 'text-info'    },
        { label: 'Selected',    value: s.selected,    color: 'text-success' },
        { label: 'Rejected',    value: s.rejected,    color: 'text-danger'  },
      ]
    },

    filtered() {
      let list = [...this.applicants]

      if (this.search) {
        const q = this.search.toLowerCase()
        list = list.filter(a =>
          a.student_name?.toLowerCase().includes(q) ||
          a.student_roll?.toLowerCase().includes(q) ||
          a.student_branch?.toLowerCase().includes(q) ||
          a.student_email?.toLowerCase().includes(q)
        )
      }
      if (this.statusFilter) list = list.filter(a => a.status === this.statusFilter)

      const sorts = {
        date_desc: (a, b) => new Date(b.applied_date) - new Date(a.applied_date),
        date_asc:  (a, b) => new Date(a.applied_date) - new Date(b.applied_date),
        cgpa_desc: (a, b) => (b.student_cgpa || 0) - (a.student_cgpa || 0),
      }
      list.sort(sorts[this.sortBy])
      return list
    },

    allSelected() {
      return this.filtered.length > 0 &&
        this.filtered.every(a => this.selectedIds.includes(a.id))
    },
  },

  async mounted() {
    this.loading = true
    await Promise.all([
      this.store.fetchDrives(this.userStore.companyId),
      this.store.fetchApplicants(this.userStore.companyId, this.driveId),
    ])
    this.loading = false
  },

  methods: {
    async refresh() {
      this.loading = true
      await this.store.fetchApplicants(this.userStore.companyId, this.driveId, true)
      this.loading = false
    },

    toggleAll(e) {
      this.selectedIds = e.target.checked ? this.filtered.map(a => a.id) : []
    },

    async updateStatus(appId, status, notes = null) {
      this.rowBusy[appId] = true
      try {
        await this.store.updateApplicationStatus(
          this.userStore.companyId, this.driveId, appId, status, notes
        )
      } catch (e) { alert(e.message) }
      finally { this.rowBusy[appId] = false }
    },

    async bulkAction(status) {
      if (!this.selectedIds.length) return
      if (!confirm(`${status} ${this.selectedIds.length} applicant(s)?`)) return
      await Promise.all(this.selectedIds.map(id => this.updateStatus(id, status)))
      this.selectedIds = []
    },

    viewCoverLetter(app) {
      this.coverModal = { show: true, appName: app.student_name, text: app.cover_letter }
    },

    submitNote() {
      if (this.noteModal.appId)
        this.updateStatus(this.noteModal.appId, null, this.noteModal.text)
      this.noteModal.show = false
    },

    formatDate(d) {
      return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
    },

    statusBadge(s) {
      return {
        Applied:     'bg-primary',
        Shortlisted: 'bg-info',
        Selected:    'bg-success',
        Rejected:    'bg-danger',
      }[s] || 'bg-secondary'
    },
  },
}
</script>

<style scoped>
.modal-backdrop {
  position: fixed; inset: 0; background: rgba(0,0,0,.5);
  display: flex; align-items: center; justify-content: center; z-index: 1050;
}
.modal-box { width: 100%; max-width: 540px; max-height: 80vh; overflow-y: auto; }
</style>