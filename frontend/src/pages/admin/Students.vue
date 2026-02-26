<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container-fluid px-4">

      <div class="d-flex align-items-center
                  justify-content-between mb-4 flex-wrap gap-2">
        <div>
          <router-link to="/admin"
                       class="btn btn-outline-secondary btn-sm mb-2">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
          <h3 class="fw-bold mb-0">Students</h3>
          <small class="text-muted">
            {{ filtered.length }} of {{ store.students.length }} shown
          </small>
        </div>
        <div class="d-flex gap-2">
          <button class="btn btn-success btn-sm"
                  :disabled="store.exportLoading"
                  @click="exportStudents">
            <span v-if="store.exportLoading"
                  class="spinner-border spinner-border-sm me-1">
            </span>
            <i v-else class="bi bi-download me-1"></i>
            Export CSV
          </button>
          <button class="btn btn-outline-primary btn-sm"
                  :disabled="store.loadingStudents"
                  @click="store.fetchStudents(true)">
            <span v-if="store.loadingStudents"
                  class="spinner-border spinner-border-sm me-1">
            </span>
            <i v-else class="bi bi-arrow-clockwise me-1"></i>
            Refresh
          </button>
        </div>
      </div>

      <!-- Summary chips -->
      <div class="d-flex flex-wrap gap-3 mb-4">
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-people-fill text-primary me-2"></i>
          <strong>{{ store.students.length }}</strong>
          <span class="ms-1 text-muted">Total</span>
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-check-circle-fill text-success me-2"></i>
          <strong>{{ store.activeStudents.length }}</strong>
          <span class="ms-1 text-muted">Active</span>
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-slash-circle-fill text-danger me-2"></i>
          <strong>{{ store.blockedStudents.length }}</strong>
          <span class="ms-1 text-muted">Blocked</span>
        </div>
        <div class="summary-chip bg-white shadow-sm">
          <i class="bi bi-file-earmark-text text-info me-2"></i>
          <strong>{{ studentsWithResume }}</strong>
          <span class="ms-1 text-muted">With Resume</span>
        </div>
      </div>

      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body d-flex flex-wrap gap-2">
          <div class="input-group" style="max-width:300px">
            <span class="input-group-text bg-white">
              <i class="bi bi-search"></i>
            </span>
            <input v-model="search"
                   class="form-control border-start-0"
                   placeholder="Name, email, roll, branch…" />
          </div>
          <select v-model="branchFilter"
                  class="form-select" style="max-width:160px">
            <option value="">All Branches</option>
            <option v-for="b in branches" :key="b" :value="b">
              {{ b }}
            </option>
          </select>
          <select v-model="yearFilter"
                  class="form-select" style="max-width:140px">
            <option value="">All Years</option>
            <option v-for="y in gradYears" :key="y" :value="y">
              {{ y }}
            </option>
          </select>
          <select v-model="statusFilter"
                  class="form-select" style="max-width:140px">
            <option value="">All Status</option>
            <option value="active">Active</option>
            <option value="blocked">Blocked</option>
          </select>
          <button v-if="search || branchFilter ||
                        yearFilter || statusFilter"
                  class="btn btn-outline-secondary btn-sm"
                  @click="search=''; branchFilter='';
                          yearFilter=''; statusFilter=''">
            <i class="bi bi-x me-1"></i>Clear
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="store.loadingStudents" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="!filtered.length"
           class="text-center py-5 text-muted">
        <i class="bi bi-search fs-1 d-block mb-2"></i>
        No students match your filters.
      </div>

      <!-- Table -->
      <div v-else class="card border-0 shadow-sm">
        <div class="table-responsive">
          <table class="table table-hover align-middle mb-0">
            <thead class="table-light">
              <tr>
                <th>Student</th><th>Roll No.</th>
                <th>Branch</th><th>CGPA</th>
                <th>Grad Year</th><th>Resume</th>
                <th>Status</th>
                <th class="text-end">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in filtered" :key="s.id">
                <td>
                  <div class="d-flex align-items-center gap-2">
                    <div class="avatar-sm">{{ initials(s.name) }}</div>
                    <div>
                      <router-link
                        :to="`/admin/students/${s.id}`"
                        class="fw-semibold text-decoration-none
                               text-dark">
                        {{ s.name }}
                      </router-link>
                      <div class="small text-muted">{{ s.email }}</div>
                    </div>
                  </div>
                </td>
                <td>{{ s.roll_number || '—' }}</td>
                <td>{{ s.branch      || '—' }}</td>
                <td>
                  <span v-if="s.cgpa" class="badge"
                        :class="cgpaBadge(s.cgpa)">
                    {{ s.cgpa }}
                  </span>
                  <span v-else class="text-muted">—</span>
                </td>
                <td>{{ s.graduation_year || '—' }}</td>
                <td>
                  <a v-if="s.resume_link"
                     :href="`${apiBase}/api/uploads/resumes/${s.resume_filename}`"
                     target="_blank"
                     class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-file-earmark-pdf"></i>
                  </a>
                  <span v-else class="text-muted small">None</span>
                </td>
                <td>
                  <span class="badge"
                        :class="s.active !== false
                          ? 'bg-success' : 'bg-secondary'">
                    {{ s.active !== false ? 'Active' : 'Blocked' }}
                  </span>
                </td>
                <td class="text-end">
                  <div class="btn-group btn-group-sm">
                    <router-link
                      :to="`/admin/students/${s.id}`"
                      class="btn btn-outline-primary"
                      title="View profile">
                      <i class="bi bi-eye"></i>
                    </router-link>
                    <button
                      v-if="s.active !== false"
                      class="btn btn-warning"
                      :disabled="rowBusy[s.user_id]"
                      title="Block student"
                      @click="block(s.user_id)">
                      <span v-if="rowBusy[s.user_id]"
                            class="spinner-border
                                   spinner-border-sm"></span>
                      <i v-else class="bi bi-slash-circle"></i>
                    </button>
                    <button
                      v-else
                      class="btn btn-success"
                      :disabled="rowBusy[s.user_id]"
                      title="Unblock student"
                      @click="unblock(s.user_id)">
                      <span v-if="rowBusy[s.user_id]"
                            class="spinner-border
                                   spinner-border-sm"></span>
                      <i v-else class="bi bi-check-circle"></i>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="card-footer bg-white text-muted small text-end">
          Showing {{ filtered.length }} of
          {{ store.students.length }} students
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/adminStore'
import { useUserStore }  from '@/stores/userStore'

export default {
  name: 'AdminStudents',
  setup() {
    return { store: useAdminStore(), userStore: useUserStore() }
  },
  data: () => ({
    search: '', branchFilter: '',
    yearFilter: '', statusFilter: '',
    rowBusy: {},
  }),
  computed: {
    apiBase() {
      return import.meta.env.VITE_API_BASE_URL ?? ''
    },
    branches() {
      return [
        ...new Set(
          this.store.students.map(s => s.branch).filter(Boolean)
        ),
      ].sort()
    },
    gradYears() {
      return [
        ...new Set(
          this.store.students
            .map(s => s.graduation_year).filter(Boolean)
        ),
      ].sort()
    },
    studentsWithResume() {
      return this.store.students.filter(s => s.resume_link).length
    },
    filtered() {
      return this.store.students.filter(s => {
        const q = this.search.toLowerCase()
        const matchSearch = !q ||
          s.name?.toLowerCase().includes(q) ||
          s.email?.toLowerCase().includes(q) ||
          s.roll_number?.toLowerCase().includes(q) ||
          s.branch?.toLowerCase().includes(q)
        const matchBranch =
          !this.branchFilter || s.branch === this.branchFilter
        const matchYear =
          !this.yearFilter ||
          String(s.graduation_year) === String(this.yearFilter)
        const matchStatus =
          !this.statusFilter ||
          (this.statusFilter === 'active'  && s.active !== false) ||
          (this.statusFilter === 'blocked' && s.active === false)
        return matchSearch && matchBranch && matchYear && matchStatus
      })
    },
  },
  async mounted() {
    if (!this.store.students.length)
      await this.store.fetchStudents()
  },
  methods: {
    async block(userId) {
      if (!confirm('Block this student?')) return
      this.rowBusy[userId] = true
      try   { await this.store.blockStudent(userId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[userId] = false }
    },
    async unblock(userId) {
      this.rowBusy[userId] = true
      try   { await this.store.unblockStudent(userId) }
      catch (e) { alert(e.message) }
      finally   { this.rowBusy[userId] = false }
    },
    async exportStudents() {
      try { await this.store.exportData('students') }
      catch (e) { alert(e.message ?? 'Export failed') }
    },
    cgpaBadge(cgpa) {
      return cgpa >= 8
        ? 'bg-success' : cgpa >= 6
        ? 'bg-warning text-dark' : 'bg-danger'
    },
    initials(name) {
      return (name || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
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
.table th {
  font-size: .8rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d;
}
</style>
