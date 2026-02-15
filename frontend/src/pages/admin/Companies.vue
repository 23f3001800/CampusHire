<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container-fluid px-4">

      <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <router-link :to="`/admin/${userStore.id}`" class="btn btn-outline-secondary btn-sm mb-2">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
          <h3 class="fw-bold mb-0">Companies</h3>
          <small class="text-muted">{{ filtered.length }} of {{ store.companies.length }} shown</small>
        </div>
        <button class="btn btn-outline-primary btn-sm" @click="store.fetchCompanies()">
          <i class="bi bi-arrow-clockwise me-1"></i>Refresh
        </button>
      </div>

      <!-- Summary chips -->
      <div class="d-flex flex-wrap gap-3 mb-4">
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-building text-primary me-2"></i>
          <strong>{{ store.companies.length }}</strong> Total
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-hourglass-split text-warning me-2"></i>
          <strong>{{ store.pendingCompanies.length }}</strong> Pending
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-check-circle-fill text-success me-2"></i>
          <strong>{{ store.approvedCompanies.length }}</strong> Approved
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-x-circle-fill text-danger me-2"></i>
          <strong>{{ store.rejectedCompanies.length }}</strong> Rejected
        </div>
      </div>

      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body d-flex flex-wrap gap-2">
          <div class="input-group" style="max-width:300px">
            <span class="input-group-text bg-white"><i class="bi bi-search"></i></span>
            <input v-model="search" class="form-control border-start-0" placeholder="Company name, recruiter, email…" />
          </div>
          <select v-model="statusFilter" class="form-select" style="max-width:160px">
            <option value="">All Statuses</option>
            <option value="Pending">Pending</option>
            <option value="Approved">Approved</option>
            <option value="Rejected">Rejected</option>
          </select>
          <select v-model="industryFilter" class="form-select" style="max-width:200px">
            <option value="">All Industries</option>
            <option v-for="i in industries" :key="i" :value="i">{{ i }}</option>
          </select>
        </div>
      </div>

      <div v-if="store.loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="!filtered.length" class="text-center py-5 text-muted">
        <i class="bi bi-building fs-1 d-block mb-2"></i>No companies match your filters.
      </div>

      <div v-else class="card border-0 shadow-sm">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Company</th>
                <th>Recruiter</th>
                <th>Industry</th>
                <th>Location</th>
                <th>Drives</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in filtered" :key="c.id">
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <img v-if="c.logo_url" :src="c.logo_url" class="rounded"
                      style="width:34px;height:34px;object-fit:cover"
                      @error="c.logo_url = null" />
                    <div v-else class="avatar-sm">{{ initials(c.company_name) }}</div>
                    <div>
                      <div class="fw-semibold">{{ c.company_name || '—' }}</div>
                      <small class="text-muted">{{ c.website || '' }}</small>
                    </div>
                  </div>
                </td>
                <td>
                  <div>{{ c.recruiter_name }}</div>
                  <small class="text-muted">{{ c.recruiter_email }}</small>
                </td>
                <td>{{ c.industry || '—' }}</td>
                <td>{{ c.location || '—' }}</td>
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
                  <div class="btn-group btn-group-sm">
                    <button
                      v-if="c.approval_status !== 'Approved'"
                      class="btn btn-outline-success"
                      :disabled="rowBusy[c.id]"
                      title="Approve"
                      @click="approve(c.id)">
                      <span v-if="rowBusy[c.id]" class="spinner-border spinner-border-sm"></span>
                      <i v-else class="bi bi-check-lg"></i>
                    </button>
                    <button
                      v-if="c.approval_status !== 'Rejected'"
                      class="btn btn-outline-danger"
                      :disabled="rowBusy[c.id]"
                      title="Reject"
                      @click="reject(c.id)">
                      <i class="bi bi-x-lg"></i>
                    </button>
                    <button
                      v-if="c.approval_status === 'Approved'"
                      class="btn btn-outline-secondary"
                      title="View drives"
                      @click="$router.push(`/admin/${userStore.id}`)">
                      <i class="bi bi-briefcase"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer bg-white text-muted small text-end">
          Showing {{ filtered.length }} of {{ store.companies.length }} companies
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/adminStore'
import { useUserStore }  from '@/stores/userStore'

export default {
  name: 'AdminCompanies',

  setup() {
    return { store: useAdminStore(), userStore: useUserStore() }
  },

  data: () => ({
    search:         '',
    statusFilter:   '',
    industryFilter: '',
    rowBusy:        {},
  }),

  computed: {
    industries() {
      return [...new Set(this.store.companies.map(c => c.industry).filter(Boolean))].sort()
    },

    filtered() {
      return this.store.companies.filter(c => {
        const q = this.search.toLowerCase()
        const matchSearch = !q ||
          c.company_name?.toLowerCase().includes(q) ||
          c.recruiter_name?.toLowerCase().includes(q) ||
          c.recruiter_email?.toLowerCase().includes(q) ||
          c.location?.toLowerCase().includes(q)
        const matchStatus   = !this.statusFilter   || c.approval_status === this.statusFilter
        const matchIndustry = !this.industryFilter || c.industry === this.industryFilter
        return matchSearch && matchStatus && matchIndustry
      })
    },
  },

  async mounted() {
    await Promise.all([
      this.store.companies.length  ? null : this.store.fetchCompanies(),
      this.store.drives.length     ? null : this.store.fetchDrives(),
    ])
  },

  methods: {
    async approve(companyId) {
      this.rowBusy[companyId] = true
      try   { await this.store.approveCompany(companyId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[companyId] = false }
    },

    async reject(companyId) {
      if (!confirm('Reject this company?')) return
      this.rowBusy[companyId] = true
      try   { await this.store.rejectCompany(companyId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[companyId] = false }
    },

    drivesForCompany(companyId) {
      return this.store.drives.filter(d => d.company_id === companyId).length
    },

    approvalBadge(s) {
      return { Pending: 'bg-warning text-dark', Approved: 'bg-success', Rejected: 'bg-danger' }[s] || 'bg-secondary'
    },

    initials(name) {
      return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },
  },
}
</script>

<style scoped>
.summary-chip {
  display: flex; align-items: center;
  padding: .5rem 1rem; border-radius: 8px; font-size: .9rem;
}
.avatar-sm {
  width: 34px; height: 34px; border-radius: 8px;
  background: #e9ecef; color: #495057;
  display: flex; align-items: center; justify-content: center;
  font-size: .7rem; font-weight: 700; flex-shrink: 0;
}
.table th { font-size: .8rem; text-transform: uppercase; letter-spacing: .04em; color: #6c757d; }
</style>