import { defineStore } from 'pinia'
import api from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useAdminStore = defineStore('admin', {
  state: () => ({
    students:            [],
    companies:           [],
    drives:              [],
    placements:          [],
    stats:               null,

    driveApplicants:     {},
    studentDetail:       {},
    studentApplications: {},
    companyDetail:       {},   // { [company_id]: {...} }
    companyDrives:       {},   // { [company_id]: [...] }

    loading:              false,
    loadingStudents:      false,
    loadingCompanies:     false,
    loadingDrives:        false,
    loadingPlacements:    false,
    loadingDriveApps:     {},
    loadingStudentDetail: {},
    loadingCompanyDetail: {},  // { [company_id]: bool }
    loadingCompanyDrives: {},  // { [company_id]: bool }
    exportLoading:        false,

    error: null,
    ts:    {},
  }),

  getters: {
    pendingCompanies:  s => s.companies.filter(c => c.approval_status === 'Pending'),
    approvedCompanies: s => s.companies.filter(c => c.approval_status === 'Approved'),
    rejectedCompanies: s => s.companies.filter(c => c.approval_status === 'Rejected'),

    companyApprovalCounts(s) {
      const counts = { Approved: 0, Pending: 0, Rejected: 0 }
      for (const c of s.companies)
        if (c.approval_status in counts) counts[c.approval_status]++
      return counts
    },

    activeStudents:  s => s.students.filter(st =>  st.active || st.active == null),
    blockedStudents: s => s.students.filter(st => !st.active),

    studentsByBranch(s) {
      const map = {}
      for (const st of s.students) {
        const b = st.branch || 'Unknown'
        map[b] = (map[b] || 0) + 1
      }
      return map
    },

    openDrives:      s => s.drives.filter(d => d.status === 'Open'),
    closedDrives:    s => s.drives.filter(d => d.status === 'Closed'),
    completedDrives: s => s.drives.filter(d => d.status === 'Completed'),

    driveStatusCounts(s) {
      const counts = { Open: 0, Closed: 0, Completed: 0 }
      for (const d of s.drives)
        if (d.status in counts) counts[d.status]++
      return counts
    },

    driveCountByCompany(s) {
      const map = {}
      s.drives.forEach(d => { map[d.company_id] = (map[d.company_id] ?? 0) + 1 })
      return map
    },

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

    applicationStatusDistribution(s) {
      const apps = s.drives.reduce(
        (acc, d) => acc.concat(s.driveApplicants[d.id] ?? []), []
      )
      return {
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

    placementsByCompany(s) {
      const map = {}
      for (const p of s.placements) {
        const name = p.company_name || `#${p.company_id}`
        map[name] = (map[name] || 0) + 1
      }
      return Object.entries(map).sort((a, b) => b[1] - a[1]).slice(0, 8)
    },

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
  },

  actions: {
    _fresh(key) {
      return !!(this.ts[key] && (Date.now() - this.ts[key]) < CACHE_TTL)
    },

    // Single universal patcher — coerces IDs, no string/number mismatch
    _patch(listKey, id, patch) {
      const item = this[listKey].find(x => String(x.id) === String(id))
      if (item) Object.assign(item, patch)
    },

    _decrementStat(key) {
      if (this.stats?.[key] != null)
        this.stats[key] = Math.max(0, this.stats[key] - 1)
    },

    // ── Bulk fetch ─────────────────────────────────────────────────────────
    async fetchAll(force = false) {
      this.loading = true; this.error = null
      try {
        await Promise.all([
          this.fetchStats(force),
          this.fetchStudents(force),
          this.fetchCompanies(force),
          this.fetchDrives(force),
          this.fetchPlacements(force),
        ])
      } finally { this.loading = false }
    },

    // ── GET /admin/stats ───────────────────────────────────────────────────
    async fetchStats(force = false) {
      if (!force && this._fresh('stats') && this.stats) return
      try {
        this.stats    = await api.get('/admin/stats')
        this.ts.stats = Date.now()
      } catch (e) { this.error = e.message }
    },

    // ── GET /admin/students ────────────────────────────────────────────────
    async fetchStudents(force = false) {
      if (!force && this._fresh('students') && this.students.length) return
      this.loadingStudents = true; this.error = null
      try {
        this.students    = await api.get('/admin/students')
        this.ts.students = Date.now()
      } catch (e) { this.error = e.message }
      finally      { this.loadingStudents = false }
    },

    // ── GET /admin/students/:id ────────────────────────────────────────────
    async fetchStudent(studentId, force = false) {
      const key = `student_${studentId}`
      if (!force && this._fresh(key) && this.studentDetail[studentId]) return
      this.loadingStudentDetail[studentId] = true
      try {
        this.studentDetail[studentId] = await api.get(`/student/${studentId}`)
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message; throw e
      } finally {
        this.loadingStudentDetail[studentId] = false
      }
    },

    async fetchresume(filename) {
      try {
        const res = await api.get(`/uploads/resumes/${filename}`, {
          responseType: "blob"
        })
        return res
      } catch (e) {
        this.error = e.message
        return null
      }
    },

    async fetchofferletter(filename) {
      try {
        const res = await api.get(`/uploads/offers/${filename}`, {
          responseType: "blob"
        })
        return res
      } catch (e) {
        this.error = e.message
        return null
      }
    },

    // ── GET /admin/students/:id/applications ───────────────────────────────
    async fetchStudentApplications(studentId, force = false) {
      const key = `studentApps_${studentId}`
      if (!force && this._fresh(key) && this.studentApplications[studentId]) return
      try {
        this.studentApplications[studentId] =
          await api.get(`student/${studentId}/applications`)
        this.ts[key] = Date.now()
      } catch (e) { this.error = e.message }
    },

    // ── GET /admin/companies ───────────────────────────────────────────────
    async fetchCompanies(force = false) {
      if (!force && this._fresh('companies') && this.companies.length) return
      this.loadingCompanies = true; this.error = null
      try {
        this.companies    = await api.get('/admin/companies')
        this.ts.companies = Date.now()
      } catch (e) { this.error = e.message }
      finally       { this.loadingCompanies = false }
    },

    // ── GET /admin/companies/:id ───────────────────────────────────────────
    async fetchCompany(companyId, force = false) {
      const key = `company_${companyId}`
      if (!force && this._fresh(key) && this.companyDetail[companyId]) return
      this.loadingCompanyDetail[companyId] = true; this.error = null
      try {
        this.companyDetail[companyId] = await api.get(`/company/${companyId}`)
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message; throw e
      } finally {
        this.loadingCompanyDetail[companyId] = false
      }
    },

    // ── GET /admin/companies/:id/drives ────────────────────────────────────
    async fetchCompanyDrives(companyId, force = false) {
      const key = `companyDrives_${companyId}`
      if (!force && this._fresh(key) && this.companyDrives[companyId]?.length) return
      this.loadingCompanyDrives[companyId] = true
      try {
        const res = await api.get(`/company/${companyId}/drives`)
        this.companyDrives[companyId] = Array.isArray(res) ? res : (res?.drives ?? [])
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loadingCompanyDrives[companyId] = false
      }
    },

    // ── GET /drives ────────────────────────────────────────────────────────
    async fetchDrives(force = false) {
      if (!force && this._fresh('drives') && this.drives.length) return
      this.loadingDrives = true; this.error = null
      try {
        this.drives    = await api.get('/drives')
        this.ts.drives = Date.now()
      } catch (e) { this.error = e.message }
      finally      { this.loadingDrives = false }
    },

    // ── GET /drives/:id ────────────────────────────────────────────────────
    async fetchDrive(driveId,companyId) {
      try {
        return await api.get(`/company/${companyId}/drives/${driveId}`)
      }
      catch (e) {
        this.error = e.message
        return null
      }
    },
    async fetchDriveApplicants(driveId, force = false) {
      if (!force && this.driveApplicants?.[driveId]) 
        return this.driveApplicants[driveId]
      
      const res = await api.get(`/admin/drives/${driveId}/applicants`)
      if (!this.driveApplicants) this.driveApplicants = {}
      this.driveApplicants[driveId] = res
      return res
    },

    // ── GET /admin/placements ──────────────────────────────────────────────
    async fetchPlacements(force = false) {
      if (!force && this._fresh('placements') && this.placements.length) return
      this.loadingPlacements = true; this.error = null
      try {
        this.placements    = await api.get('/admin/placements')
        console.log('Fetched placements:', this.placements)
        this.ts.placements = Date.now()
      } catch (e) { this.error = e.message }
      finally       { this.loadingPlacements = false }
    },

    // ═══════════════════════════════════════════════════════════════════════
    // PATCH /admin/companies/:id
    // approve → { approval_status: 'Approved' }
    // reject  → { approval_status: 'Rejected' }
    // block   → { active: false }
    // unblock → { active: true }
    // ═══════════════════════════════════════════════════════════════════════
    async patchCompany(companyId, payload) {
      await api.patch(`/company/${companyId}`, payload)
      // Sync both the list cache and the detail cache
      this._patch('companies', companyId, payload)
      const detail = this.companyDetail[companyId]
      if (detail) Object.assign(detail, payload)
      if ('approval_status' in payload) this._decrementStat('pending_companies')
      delete this.ts.companies
      delete this.ts[`company_${companyId}`]
    },
    async deleteCompany(companyId) {
      await api.delete(`/company/${companyId}`)
      this.companies = this.companies.filter(c => String(c.id) !== String(companyId))
      delete this.companyDetail[companyId]
      delete this.companyDrives[companyId]
      delete this.ts.companies
      this._decrementStat('approved_companies')
    },


    // ═══════════════════════════════════════════════════════════════════════
    // PATCH /admin/students/:id
    // block   → { active: false }
    // unblock → { active: true }
    // ═══════════════════════════════════════════════════════════════════════
    async adminstudentactions(studentId, payload) {
      await api.patch(`/student/${studentId}`, payload)
      this._patch('students', studentId, payload)
      const detail = this.studentDetail[studentId]
      if (detail) Object.assign(detail, payload)
      delete this.ts.students
      delete this.ts[`student_${studentId}`]
    },
  
    // ═══════════════════════════════════════════════════════════════════════
    // PATCH /company/:companyId/drives/:driveId
    // approve drive       → { admin_approval_status: 'Approved' }
    // reject  drive       → { admin_approval_status: 'Rejected' }
    // toggle drive status → { status: 'Open' | 'Closed' | 'Completed' }
    // ═══════════════════════════════════════════════════════════════════════
    async patchDrive(driveId, payload, companyId) {
      const updated = await api.patch(`/company/${companyId}/drives/${driveId}`, payload)
      const merged  = updated ?? payload

      // Sync the global drives list
      this._patch('drives', driveId, merged)

      // Sync the per-company drives cache
      const list = this.companyDrives[companyId]
      if (list) {
        const drive = list.find(d => String(d.id) === String(driveId))
        if (drive) Object.assign(drive, merged)
      }

      if (this.stats && 'status' in merged)
        this.stats.open_drives = this.drives.filter(d => d.status === 'Open').length

      delete this.ts.drives
      return updated
    },

    // ── DELETE /admin/drives/:id ───────────────────────────────────────────
    async deleteDrive(driveId, companyId = null) {
      const cid = companyId
        ?? this.drives.find(d => String(d.id) === String(driveId))?.company_id
      if (!cid) throw new Error(`company_id not found for drive ${driveId}`)

      await api.delete(`/company/${cid}/drives/${driveId}`)
      this.drives = this.drives.filter(d => String(d.id) !== String(driveId))
      delete this.driveApplicants[driveId]
      delete this.ts.drives
      if (this.stats) this.stats.total_drives = this.drives.length
    },

    // ── CSV export ─────────────────────────────────────────────────────────
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
        a.href = url
        a.download = `${type}-${new Date().toISOString().slice(0, 10)}.csv`
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        this.error = e.message; throw e
      } finally {
        this.exportLoading = false
      }
    },
  },
})
