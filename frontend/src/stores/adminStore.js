import { defineStore } from 'pinia'
import api             from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useAdminStore = defineStore('admin', {
  state: () => ({
    students:            [],
    companies:           [],
    drives:              [],
    placements:          [],
    stats:               null,

    // Per-entity detail caches
    driveApplicants:     {},   // { [drive_id]:   [...] }
    studentDetail:       {},   // { [student_id]: {...} }
    studentApplications: {},   // { [student_id]: [...] }

    // Granular loading flags — no single-boolean race condition
    loading:              false,
    loadingStudents:      false,
    loadingCompanies:     false,
    loadingDrives:        false,
    loadingPlacements:    false,
    loadingDriveApps:     {},   // { [drive_id]:   bool }
    loadingStudentDetail: {},   // { [student_id]: bool }
    exportLoading:        false,

    error: null,
    ts:    {},
  }),

  getters: {
    // Company filters
    pendingCompanies:  s => s.companies.filter(c => c.approval_status === 'Pending'),
    approvedCompanies: s => s.companies.filter(c => c.approval_status === 'Approved'),
    rejectedCompanies: s => s.companies.filter(c => c.approval_status === 'Rejected'),

    // Student filters
    activeStudents:  s => s.students.filter(st => st.active !== false),
    blockedStudents: s => s.students.filter(st => st.active === false),

    // Drive filters
    openDrives:      s => s.drives.filter(d => d.status === 'Open'),
    closedDrives:    s => s.drives.filter(d => d.status === 'Closed'),
    completedDrives: s => s.drives.filter(d => d.status === 'Completed'),

    // ── Dashboard stat cards ────────────────────────────────────────────────
    // All keys match AdminStatsResource snake_case exactly.
    // Falls back to derived counts when stats not yet loaded.
    dashboardStats(s) {
      if (s.stats) return s.stats
      return {
        total_students:      s.students.length,
        total_companies:     s.companies.length,
        pending_companies:   s.companies.filter(c => c.approval_status === 'Pending').length,
        approved_companies:  s.companies.filter(c => c.approval_status === 'Approved').length,
        total_drives:        s.drives.length,
        open_drives:         s.drives.filter(d => d.status === 'Open').length,
        total_applications:  0,
        total_placements:    s.placements.length,
        placements_offered:  s.placements.filter(p => p.status === 'Offered').length,
        placements_joined:   s.placements.filter(p => p.status === 'Joined').length,
        placements_declined: s.placements.filter(p => p.status === 'Declined').length,
      }
    },

    // Drive count per company — used in AdminCompanies table
    driveCountByCompany(s) {
      const map = {}
      s.drives.forEach(d => { map[d.company_id] = (map[d.company_id] ?? 0) + 1 })
      return map
    },

    // Applicant status breakdown per drive
    // Replaces the wrong companyStore.getDriveStats call in AdminDashboard
    getDriveApplicantStats: s => driveId => {
      const apps = s.driveApplicants[driveId] ?? []
      return {
        total:       apps.length,
        Applied:     apps.filter(a => a.status === 'Applied').length,
        Shortlisted: apps.filter(a => a.status === 'Shortlisted').length,
        Selected:    apps.filter(a => a.status === 'Selected').length,
        Rejected:    apps.filter(a => a.status === 'Rejected').length,
      }
    },

    placementStats(s) {
      return {
        total:    s.placements.length,
        offered:  s.placements.filter(p => p.status === 'Offered').length,
        joined:   s.placements.filter(p => p.status === 'Joined').length,
        declined: s.placements.filter(p => p.status === 'Declined').length,
      }
    },

    // For charts — students grouped by branch
    studentsByBranch(s) {
      const map = {}
      s.students.forEach(st => {
        const b = st.branch || 'Unknown'
        map[b] = (map[b] ?? 0) + 1
      })
      return map
    },

    // Top 10 companies by placement count
    topCompaniesByPlacements(s) {
      const map = {}
      s.placements.forEach(p => {
        const n = p.company_name || 'Unknown'
        map[n] = (map[n] ?? 0) + 1
      })
      return Object.entries(map)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 10)
    },

    // Application status distribution — for pie/doughnut chart
    applicationStatusDistribution(s) {
      const apps = s.drives.reduce((acc, d) => {
        const driveApps = s.driveApplicants[d.id] ?? []
        return acc.concat(driveApps)
      }, [])
      return {
        Applied:     apps.filter(a => a.status === 'Applied').length,
        Shortlisted: apps.filter(a => a.status === 'Shortlisted').length,
        Selected:    apps.filter(a => a.status === 'Selected').length,
        Rejected:    apps.filter(a => a.status === 'Rejected').length,
      }
    },
    // adminStore.js → inside getters: {}

    driveStatusCounts(state) {
      const counts = { Open: 0, Closed: 0, Completed: 0 }
      for (const d of state.drives || []) {
        if (d.status in counts) counts[d.status]++
      }
      return counts
    },

    companyApprovalCounts(state) {
      const counts = { Approved: 0, Pending: 0, Rejected: 0 }
      for (const c of state.companies || []) {
        if (c.approval_status in counts) counts[c.approval_status]++
      }
      return counts
    },

    studentsByBranch(state) {
      const map = {}
      for (const s of state.students || []) {
        const b = s.branch || 'Unknown'
        map[b] = (map[b] || 0) + 1
      }
      return map
    },

    placementsByCompany(state) {
      const map = {}
      for (const p of state.placements || []) {
        const name = p.company_name || `#${p.company_id}`
        map[name] = (map[name] || 0) + 1
      }
      return Object.entries(map)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 8)
    },

    // for chart 5 — application status
    applicationStatusCounts(state) {
      const counts = { Applied: 0, Shortlisted: 0, Selected: 0, Rejected: 0 }
      for (const a of state.applications || []) {
        if (a.status in counts) counts[a.status]++
      }
      return counts
    },

  },

  actions: {
    _fresh(key) {
      return !!(this.ts[key] && (Date.now() - this.ts[key]) < CACHE_TTL)
    },

    // ── Bulk fetch ────────────────────────────────────────────────────────
    async fetchAll(force = false) {
      this.loading = true
      this.error   = null
      try {
        await Promise.all([
          this.fetchStats(force),
          this.fetchStudents(force),
          this.fetchCompanies(force),
          this.fetchDrives(force),
          this.fetchPlacements(force),
        ])
      } finally {
        this.loading = false
      }
    },

    // ── GET /admin/stats ──────────────────────────────────────────────────
    async fetchStats(force = false) {
      if (!force && this._fresh('stats') && this.stats) return
      try {
        this.stats    = await api.get('/admin/stats')
        this.ts.stats = Date.now()
      } catch (e) { this.error = e.message }
    },

    // ── GET /admin/students ───────────────────────────────────────────────
    async fetchStudents(force = false) {
      if (!force && this._fresh('students') && this.students.length) return
      this.loadingStudents = true; this.error = null
      try {
        this.students      = await api.get('/admin/students')
        this.ts.students   = Date.now()
      } catch (e) { this.error = e.message }
      finally      { this.loadingStudents = false }
    },

    // ── GET /admin/students/:id ───────────────────────────────────────────
    async fetchStudent(studentId, force = false) {
      const key = `student_${studentId}`
      if (!force && this._fresh(key) && this.studentDetail[studentId]) return
      this.loadingStudentDetail[studentId] = true
      try {
        this.studentDetail[studentId] = await api.get(`student/${studentId}`)
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loadingStudentDetail[studentId] = false
      }
    },

    // ── GET /admin/students/:id/applications ──────────────────────────────
    async fetchStudentApplications(studentId, force = false) {
      const key = `studentApps_${studentId}`
      if (!force && this._fresh(key) && this.studentApplications[studentId]) return
      try {
        this.studentApplications[studentId] =
          await api.get(`student/${studentId}/applications`)
        this.ts[key] = Date.now()
      } catch (e) { this.error = e.message }
    },

    // ── GET /admin/companies ──────────────────────────────────────────────
    async fetchCompanies(force = false) {
      if (!force && this._fresh('companies') && this.companies.length) return
      this.loadingCompanies = true; this.error = null
      try {
        this.companies      = await api.get('/admin/companies')
        this.ts.companies   = Date.now()
      } catch (e) { this.error = e.message }
      finally       { this.loadingCompanies = false }
    },

    // ── GET /drives (public — returns all statuses) ───────────────────────
    async fetchDrives(force = false) {
      if (!force && this._fresh('drives') && this.drives.length) return
      this.loadingDrives = true; this.error = null
      try {
        this.drives      = await api.get('/drives')
        this.ts.drives   = Date.now()
      } catch (e) { this.error = e.message }
      finally      { this.loadingDrives = false }
    },

    // ── GET /drives/:id ───────────────────────────────────────────────────
    async fetchDrive(driveId) {
      try { return await api.get(`/drives/${driveId}`) }
      catch (e) { this.error = e.message; return null }
    },

    // ── GET /admin/drives/:id/applicants ──────────────────────────────────
    async fetchDriveApplicants(driveId, force = false) {
      const key = `driveApps_${driveId}`
      if (!force && this._fresh(key) && this.driveApplicants[driveId]) return
      this.loadingDriveApps[driveId] = true
      try {
        this.driveApplicants[driveId] =
          await api.get(`/admin/drives/${driveId}/applicants`)
        this.ts[key] = Date.now()
      } catch (e) { this.error = e.message }
      finally      { this.loadingDriveApps[driveId] = false }
    },

    // ── GET /admin/placements ─────────────────────────────────────────────
    async fetchPlacements(force = false) {
      if (!force && this._fresh('placements') && this.placements.length) return
      this.loadingPlacements = true; this.error = null
      try {
        this.placements      = await api.get('/admin/placements')
        this.ts.placements   = Date.now()
      } catch (e) { this.error = e.message }
      finally       { this.loadingPlacements = false }
    },

    // ── PUT /admin/companies/:id/approval ─────────────────────────────────
    async approveCompany(companyId) {
      await api.put(`/admin/companies/${companyId}/approval`, { status: 'Approved' })
      this._patch('companies', companyId, { approval_status: 'Approved' })
      this._decrementStat('pending_companies')
    },

    async rejectCompany(companyId) {
      await api.put(`/admin/companies/${companyId}/approval`, { status: 'Rejected' })
      this._patch('companies', companyId, { approval_status: 'Rejected' })
      this._decrementStat('pending_companies')
    },

    // ── PUT /admin/drives/:id/approval ────────────────────────────────────
    async approveDrive(driveId) {
      const updated = await api.put(`/admin/drives/${driveId}/approval`, { status: 'Approved' })
      this._patch('drives', driveId, { admin_approval_status: 'Approved' })
      return updated
    },

    async rejectDrive(driveId) {
      const updated = await api.put(`/admin/drives/${driveId}/approval`, { status: 'Rejected' })
      this._patch('drives', driveId, { admin_approval_status: 'Rejected' })
      return updated
    },

    // ── PATCH /admin/drives/:id ───────────────────────────────────────────
    async toggleDriveStatus(driveId) {
      const updated = await api.patch(`/admin/drives/${driveId}`)
      this._patch('drives', driveId, { status: updated.status })
      if (this.stats)
        this.stats.open_drives = this.drives.filter(d => d.status === 'Open').length
      return updated
    },

    // ── DELETE /admin/drives/:id ──────────────────────────────────────────
    async deleteDrive(driveId) {
      await api.delete(`/admin/drives/${driveId}`)
      this.drives = this.drives.filter(d => d.id !== driveId)
      delete this.driveApplicants[driveId]
      if (this.stats) this.stats.total_drives = this.drives.length
    },

    // ── PUT /admin/users/:userId/active ───────────────────────────────────
    async blockStudent(userId) {
      await api.put(`/admin/users/${userId}/active`, { active: false })
      this._patchByUserId(userId, { active: false })
    },

    async unblockStudent(userId) {
      await api.put(`/admin/users/${userId}/active`, { active: true })
      this._patchByUserId(userId, { active: true })
    },

    // Unified toggle — used by AdminStudentDetail
    async toggleStudentActive(userId, newActive) {
      await api.put(`/admin/users/${userId}/active`, { active: newActive })
      this._patchByUserId(userId, { active: newActive })
      // Also patch cached detail object
      const detail = Object.values(this.studentDetail)
        .find(s => s.user_id === userId)
      if (detail) detail.is_active = newActive
    },

    // ── GET /admin/export?type=... (CSV blob download) ─────────────────────
    // AdminExportDataResource — streams CSV response
    async exportData(type = 'students') {
      this.exportLoading = true
      try {
        const token = localStorage.getItem('token')
        const base  = import.meta.env.VITE_API_BASE_URL ?? ''
        const res   = await fetch(
          `${base}/admin/export?type=${type}`,
          { headers: { 'Authentication-Token': token } }
        )
        if (!res.ok) throw new Error(`Export failed (${res.status})`)
        const blob = await res.blob()
        const url  = URL.createObjectURL(blob)
        const a    = document.createElement('a')
        a.href     = url
        a.download = `${type}-${new Date().toISOString().slice(0, 10)}.csv`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.exportLoading = false
      }
    },

    // ── Internal helpers ──────────────────────────────────────────────────
    _patch(listKey, id, patch) {
      const item = this[listKey].find(x => x.id === id)
      if (item) Object.assign(item, patch)
    },
    _patchByUserId(userId, patch) {
      const s = this.students.find(s => s.user_id === userId)
      if (s) Object.assign(s, patch)
    },
    _decrementStat(key) {
      if (this.stats?.[key] != null)
        this.stats[key] = Math.max(0, this.stats[key] - 1)
    },
  },
})
