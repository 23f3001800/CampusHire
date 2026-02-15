import { defineStore } from 'pinia'
import api from '@/utils/api'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    students:   [],
    companies:  [],
    drives:     [],
    placements: [],
    stats:      null,   // populated from /api/admin/stats
    loading:    false,
    error:      null,
  }),

  getters: {
    // ── Derived lists ────────────────────────────────────────────────────────
    pendingCompanies:  s => s.companies.filter(c => c.approval_status === 'Pending'),
    approvedCompanies: s => s.companies.filter(c => c.approval_status === 'Approved'),
    rejectedCompanies: s => s.companies.filter(c => c.approval_status === 'Rejected'),
    activeStudents:    s => s.students.filter(st => st.active !== false),
    blockedStudents:   s => s.students.filter(st => st.active === false),
    openDrives:        s => s.drives.filter(d => d.status === 'Open'),

    // ── Dashboard stat cards (use server stats if loaded, fallback to counts) 
    dashboardStats: s => s.stats ?? {
      total_students:      s.students.length,
      total_companies:     s.companies.length,
      pending_companies:   s.companies.filter(c => c.approval_status === 'Pending').length,
      open_drives:         s.drives.filter(d => d.status === 'Open').length,
      total_placements:    s.placements.length,
      total_applications:  0,
    },
  },

  actions: {
    // ── Bulk fetch ───────────────────────────────────────────────────────────
    async fetchAll() {
      await Promise.all([
        this.fetchStats(),
        this.fetchStudents(),
        this.fetchCompanies(),
        this.fetchDrives(),
        this.fetchPlacements(),
      ])
    },

    // ── Individual fetches ───────────────────────────────────────────────────
    async fetchStats() {
      try { this.stats = await api.get('/admin/stats') }
      catch (e) { this.error = e.message }
    },

    async fetchStudents() {
      this.loading = true; this.error = null
      try   { this.students  = await api.get('/admin/students') }
      catch (e) { this.error = e.message }
      finally   { this.loading = false }
    },

    async fetchCompanies() {
      this.loading = true; this.error = null
      try   { this.companies = await api.get('/admin/companies') }
      catch (e) { this.error = e.message }
      finally   { this.loading = false }
    },

    async fetchDrives() {
      this.loading = true; this.error = null
      try   { this.drives = await api.get('/drives') }
      catch (e) { this.error = e.message }
      finally   { this.loading = false }
    },

    async fetchPlacements() {
      this.loading = true; this.error = null
      try   { this.placements = await api.get('/admin/placements') }
      catch (e) { this.error = e.message }
      finally   { this.loading = false }
    },

    // ── Company approval ─────────────────────────────────────────────────────
    async approveCompany(companyId) {
      await api.put(`/admin/companies/${companyId}/approval`, { status: 'Approved' })
      this._patch('companies', companyId, { approval_status: 'Approved' })
      if (this.stats) this.stats.pending_companies = Math.max(0, (this.stats.pending_companies || 1) - 1)
    },

    async rejectCompany(companyId) {
      await api.put(`/admin/companies/${companyId}/approval`, { status: 'Rejected' })
      this._patch('companies', companyId, { approval_status: 'Rejected' })
      if (this.stats) this.stats.pending_companies = Math.max(0, (this.stats.pending_companies || 1) - 1)
    },

    // ── Student block / unblock ──────────────────────────────────────────────
    async blockStudent(userId) {
      await api.put(`/admin/users/${userId}/active`, { active: false })
      this._patchByUserId(userId, { active: false })
    },

    async unblockStudent(userId) {
      await api.put(`/admin/users/${userId}/active`, { active: true })
      this._patchByUserId(userId, { active: true })
    },

    // ── Drive management ─────────────────────────────────────────────────────
    async toggleDriveStatus(driveId) {
      const updated = await api.patch(`/admin/drives/${driveId}`)
      this._patch('drives', driveId, { status: updated.status })
      if (this.stats) this.stats.open_drives = this.drives.filter(d => d.status === 'Open').length
    },

    async deleteDrive(driveId) {
      await api.delete(`/admin/drives/${driveId}`)
      this.drives = this.drives.filter(d => d.id !== driveId)
      if (this.stats) this.stats.total_drives = this.drives.length
    },

    // ── Internal helpers ─────────────────────────────────────────────────────
    _patch(list, id, patch) {
      const item = this[list].find(x => x.id === id)
      if (item) Object.assign(item, patch)
    },

    _patchByUserId(userId, patch) {
      const s = this.students.find(s => s.user_id === userId)
      if (s) Object.assign(s, patch)
    },
  },
})