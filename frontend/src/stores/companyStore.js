import { defineStore }   from 'pinia'
import { useUserStore }  from './userStore'
import api               from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useCompanyStore = defineStore('company', {

  // ─── State ────────────────────────────────────────────────────────────────
  state: () => ({
    profile:        null,
    drives:         [],
    applicants:     {},   // { [driveId]: Application[] }
    interviews:     {},   // { [applicationId]: Interview }
    loadingProfile: false,
    loadingDrives:  false,
    loadingApps:    false,
    error:          null,
    _ts:            {},
  }),

  // ─── Getters ──────────────────────────────────────────────────────────────
  getters: {

    // Profile completion — delegates to userStore
    isProfileComplete(state) {
      return useUserStore().isProfileComplete(state.profile, 'company')
    },
    profileCompletionDetails(state) {
      return useUserStore().getProfileCompletionDetails(
        state.profile, 'company'
      )
    },
    missingFieldsWithLabels(state) {
      return useUserStore().getMissingFieldsWithLabels(
        state.profile, 'company'
      )
    },

    // Profile shortcuts
    companyName:    s => s.profile?.company_name   || '',
    approvalStatus: s => s.profile?.approval_status || 'Pending',
    isApproved:     s => s.profile?.approval_status === 'Approved',
    logoUrl:        s => s.profile?.logo_url        || null,

    // Drive filters
    activeDrives:    s => s.drives.filter(d => d.status === 'Open'),
    closedDrives:    s => s.drives.filter(d => d.status === 'Closed'),
    completedDrives: s => s.drives.filter(d => d.status === 'Completed'),
    pendingDrives:   s => s.drives.filter(
      d => d.admin_approval_status === 'Pending'
    ),

    getDriveById: s => id => s.drives.find(d => d.id === id) || null,

    // Applicant helpers
    totalApplicants: s =>
      Object.values(s.applicants)
            .reduce((sum, arr) => sum + arr.length, 0),

    getApplicantsForDrive: s => driveId =>
      s.applicants[driveId] || [],

    // Per-drive pipeline stats — reads from in-memory cache
    getDriveStats: s => driveId => {
      const apps = s.applicants[driveId] || []
      return {
        total:       apps.length,
        applied:     apps.filter(a => a.status === 'Applied').length,
        shortlisted: apps.filter(a => a.status === 'Shortlisted').length,
        selected:    apps.filter(a => a.status === 'Selected').length,
        rejected:    apps.filter(a => a.status === 'Rejected').length,
      }
    },

    // 10 most recent applicants across all drives
    recentApplicants: s =>
      Object.values(s.applicants)
            .flat()
            .sort((a, b) =>
              new Date(b.applied_date) - new Date(a.applied_date)
            )
            .slice(0, 10),

    getInterviewForApp: s => applicationId =>
      s.interviews[applicationId] || null,
  },

  // ─── Actions ──────────────────────────────────────────────────────────────
  actions: {

    // ── Cache helpers ───────────────────────────────────────────────────────
    _fresh(key) {
      return this._ts[key] &&
             Date.now() - this._ts[key] < CACHE_TTL
    },
    _clearError() { this.error = null },

    // ── Profile ─────────────────────────────────────────────────────────────
    // GET /company/:id   → returns company_fields directly (no .data wrapper)
    async fetchProfile(companyId, force = false) {
      if (!force && this._fresh('profile') && this.profile) return
      this.loadingProfile = true
      this._clearError()
      try {
        this.profile     = await api.get(`/company/${companyId}`)
        this._ts.profile = Date.now()
      } catch (e) {
        this.error = e?.message ?? 'Failed to load profile.'
        throw e
      } finally {
        this.loadingProfile = false
      }
    },

    // PUT /company/:id   → returns updated company_fields directly
    async updateProfile(companyId, data) {
      this.loadingProfile = true
      this._clearError()
      try {
        this.profile = await api.put(`/company/${companyId}`, data)
        this._ts.profile = Date.now()
        return this.profile
      } catch (e) {
        this.error = e?.message ?? 'Failed to update profile.'
        throw e
      } finally {
        this.loadingProfile = false
      }
    },

    // ── Drives ──────────────────────────────────────────────────────────────
    // GET /company/:id/drives  → returns drive_fields[] directly
    async fetchDrives(companyId, force = false) {
      if (!force && this._fresh('drives') && this.drives.length) return
      this.loadingDrives = true
      this._clearError()
      try {
        const res       = await api.get(`/company/${companyId}/drives`)
        this.drives     = Array.isArray(res) ? res : []
        this._ts.drives = Date.now()
      } catch (e) {
        this.error = e?.message ?? 'Failed to load drives.'
        throw e
      } finally {
        this.loadingDrives = false
      }
    },

    // POST /company/:id/drives → returns new drive_fields directly
    async createDrive(companyId, data) {
      const drive = await api.post(`/company/${companyId}/drives`, data)
      this.drives.unshift(drive)
      return drive
    },

    // PUT /company/:id/drives/:did → returns updated drive_fields directly
    async updateDrive(companyId, driveId, data) {
      const updated = await api.put(
        `/company/${companyId}/drives/${driveId}`, data
      )
      const i = this.drives.findIndex(d => d.id === driveId)
      if (i !== -1) this.drives[i] = updated
      return updated
    },

    // PATCH /company/:id/drives/:did → returns updated drive_fields directly
    async toggleDriveStatus(companyId, driveId) {
      const updated = await api.patch(
        `/company/${companyId}/drives/${driveId}`
      )
      const i = this.drives.findIndex(d => d.id === driveId)
      if (i !== -1) this.drives[i] = updated
      return updated
    },

    // DELETE /company/:id/drives/:did
    async deleteDrive(companyId, driveId) {
      await api.delete(`/company/${companyId}/drives/${driveId}`)
      this.drives = this.drives.filter(d => d.id !== driveId)
      delete this.applicants[driveId]
    },

    // ── Applicants ──────────────────────────────────────────────────────────
    // GET /company/:id/drives/:did/applicants → returns application_fields[]
    async fetchApplicants(companyId, driveId, force = false) {
      const key = `apps_${driveId}`
      if (!force && this._fresh(key) && this.applicants[driveId]) return
      this.loadingApps = true
      this._clearError()
      try {
        const res = await api.get(
          `/company/${companyId}/drives/${driveId}/applicants`
        )
        this.applicants = {
          ...this.applicants,
          [driveId]: Array.isArray(res) ? res : [],
        }
        this._ts[key] = Date.now()
      } catch (e) {
        this.error = e?.message ?? 'Failed to load applicants.'
        throw e
      } finally {
        this.loadingApps = false
      }
    },

    // PUT /company/:id/drives/:did/applicants/:aid
    // Body: { status, notes? }   → returns updated application_fields
    async updateApplicationStatus(
      companyId, driveId, applicationId, status, notes = null
    ) {
      const updated = await api.put(
        `/company/${companyId}/drives/${driveId}/applicants/${applicationId}`,
        { status, ...(notes !== null && { notes }) }
      )
      this._patchApplicant(driveId, applicationId, updated)
      return updated
    },

    // ── Interview ────────────────────────────────────────────────────────────

    // GET /company/:id/applications/:aid/interview
    // Called on page load so the interview card shows even on a fresh visit.
    // A 404 means no interview is scheduled yet — that is not an error,
    // we just leave interviews[applicationId] unset (falsy).
    async fetchInterviewForApplication(companyId, applicationId) {
      try {
        const res = await api.get(
          `/company/${companyId}/applications/${applicationId}/interview`
        )
        this.interviews = { ...this.interviews, [applicationId]: res }
        return res
      } catch (e) {
        // 404 = no interview scheduled yet — silently ignore
        const status = e?.response?.status ?? e?.status
        if (status === 404) return null
        // Any other error is real — bubble up so the caller can decide
        throw e
      }
    },

    // POST /company/:id/applications/:aid/interview
    // Body: { interview_type, interview_mode, interview_date (ISO),
    //         interview_link?, interviewer?, instructions? }
    // — Backend auto-sets application.status = 'Shortlisted' if was 'Applied'
    async scheduleInterview(companyId, applicationId, data) {
      const res = await api.post(
        `/company/${companyId}/applications/${applicationId}/interview`,
        data
      )
      // Store interview in cache
      this.interviews = {
        ...this.interviews,
        [applicationId]: res,
      }
      // Reflect status change — backend promotes Applied → Shortlisted
      for (const driveId of Object.keys(this.applicants)) {
        const arr = this.applicants[driveId]
        const i   = arr?.findIndex(a => a.id === applicationId)
        if (i !== undefined && i !== -1) {
          const app = arr[i]
          if (app.status === 'Applied') {
            this.applicants[driveId][i] = {
              ...app, status: 'Shortlisted',
            }
          }
        }
      }
      return res
    },

    async cancelInterview(companyId, applicationId) {
      await api.delete(
        `/company/${companyId}/applications/${applicationId}/interview`
      )
      // Remove from interviews cache
      const updated = { ...this.interviews }
      delete updated[applicationId]
      this.interviews = updated
    },

    // PUT /company/:id/applications/:aid/selection
    // Body: { status: 'Selected'|'Rejected', salary?, joining_date?, notes? }
    // — Backend creates Placement record automatically when status=Selected
    async finalizeSelection(companyId, applicationId, data) {
      const res = await api.put(
        `/company/${companyId}/applications/${applicationId}/selection`,
        data
      )
      // Patch in-memory applicant list
      for (const driveId of Object.keys(this.applicants)) {
        const arr = this.applicants[driveId]
        const i   = arr?.findIndex(a => a.id === applicationId)
        if (i !== undefined && i !== -1) {
          this.applicants[driveId][i] = {
            ...arr[i], status: data.status,
          }
        }
      }
      return res
    },

    // ── Student profile (for company viewing applicant) ───────────────────
    // GET /student/:id   (roles_accepted: company, admin)
    async fetchStudentProfile(studentId) {
      try {
        return await api.get(`/student/${studentId}`)
      } catch (e) {
        this.error = e?.message ?? 'Student not found.'
        throw e
      }
    },

    // POST /company/:id/applications/:aid/offer-letter/generate
    // Body: offerFields object
    // Returns: { offer_letter_url, offer_letter_filename, offer_letter_generated_date }
    async generateOfferLetter(companyId, applicationId, offerData) {
      try {
        // api utility already unwraps the response — use res directly, not res.data
        const res = await api.post(
          `/company/${companyId}/applications/${applicationId}/offer-letter/generate`,
          offerData
        )
        // Patch in-memory placement so the download URL is immediately available
        for (const applicants of Object.values(this.applicants)) {
          const app = applicants.find(a => a.id === applicationId)
          if (app?.placement) {
            app.placement.offer_letter_filename       = res.offer_letter_filename
            app.placement.offer_letter_url            = res.offer_letter_url
            app.placement.offer_letter_generated_date = res.offer_letter_generated_date
          }
        }
        return res   // { offer_letter_url, offer_letter_filename, offer_letter_generated_date }
      } catch (e) {
        throw new Error(e?.response?.data?.error ?? e?.message ?? 'Failed to generate offer letter')
      }
    },

    // GET /api/uploads/offers/<filename>  (OfferLetterDownloadResource)
    // filename comes from the generate response — passed in by the caller.
    async downloadOfferLetter(companyId, applicationId, filename = 'offer-letter.pdf') {
      try {
        const token = localStorage.getItem('token')
        const base  = import.meta.env.VITE_API_BASE_URL ?? ''
        const res   = await fetch(
          `${base}/api/uploads/offers/${filename}`,
          { headers: { 'Authentication-Token': token } }
        )
        if (!res.ok) throw new Error(`Download failed (${res.status})`)
        const blob = await res.blob()
        const url  = URL.createObjectURL(blob)
        const a    = document.createElement('a')
        a.href     = url
        a.download = filename
        a.click()
        URL.revokeObjectURL(url)
      } catch (e) {
        throw new Error(e?.message ?? 'Failed to download offer letter')
      }
    },

    // ── Internal patch helper ────────────────────────────────────────────────
    _patchApplicant(driveId, applicationId, updated) {
      const arr = this.applicants[driveId]
      if (!arr) return
      const i = arr.findIndex(a => a.id === applicationId)
      if (i !== -1) this.applicants[driveId][i] = updated
    },

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

    // ── Reset (on logout) ────────────────────────────────────────────────────
    $reset() {
      this.profile    = null
      this.drives     = []
      this.applicants = {}
      this.interviews = {}
      this.error      = null
      this._ts        = {}
    },
  },
})