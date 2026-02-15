import { defineStore } from 'pinia'
import { useUserStore } from './userStore'
import api from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useStudentStore = defineStore('student', {
  state: () => ({
    profile:      null,
    eligibleDrives: [],
    applications: [],
    savedDrives:  [],
    filters: { search: '', jobType: '', sortBy: 'application_deadline' },
    loading:         false,
    loadingProfile:  false,
    loadingDrives:   false,
    loadingApps:     false,
    error:           null,
    _ts: {},
  }),

  getters: {
    // ── Profile completion (delegates to userStore) ──────────────────────
    isProfileComplete(state) {
      return useUserStore().isProfileComplete(state.profile, 'student')
    },
    profileCompletionDetails(state) {
      return useUserStore().getProfileCompletionDetails(state.profile, 'student')
    },
    missingFieldsWithLabels(state) {
      return useUserStore().getMissingFieldsWithLabels(state.profile, 'student')
    },
    hasResume: s => !!(s.profile?.resume_link),

    // ── Applied drives set ───────────────────────────────────────────────
    appliedDriveIds: s => new Set(s.applications.map(a => a.drive_id)),
    hasApplied:      s => driveId => new Set(s.applications.map(a => a.drive_id)).has(driveId),
    isDriveSaved:    s => driveId => s.savedDrives.some(d => d.id === driveId),

    // ── Filtered drives ──────────────────────────────────────────────────
    filteredEligibleDrives(state) {
      const { search, jobType, sortBy } = state.filters
      let list = [...state.eligibleDrives]

      if (search) {
        const q = search.toLowerCase()
        list = list.filter(d =>
          d.title?.toLowerCase().includes(q) ||
          d.company_name?.toLowerCase().includes(q) ||
          d.description?.toLowerCase().includes(q)
        )
      }
      if (jobType) list = list.filter(d => d.job_type === jobType)

      const sorts = {
        application_deadline: (a, b) => new Date(a.application_deadline) - new Date(b.application_deadline),
        salary_max:           (a, b) => (b.salary_max || 0) - (a.salary_max || 0),
        posted_date:          (a, b) => new Date(b.posted_date) - new Date(a.posted_date),
      }
      if (sorts[sortBy]) list.sort(sorts[sortBy])
      return list
    },

    urgentDrives: s => s.eligibleDrives.filter(d => {
      if (!d.application_deadline) return false
      const diff = new Date(d.application_deadline) - new Date()
      return diff > 0 && diff <= 3 * 86400000
    }),

    recommendedDrives(state) {
      if (!state.profile?.branch) return []
      const b = state.profile.branch.toLowerCase()
      return state.eligibleDrives.filter(d =>
        d.eligible_branches?.toLowerCase().includes(b)
      )
    },

    applicationStats: s => ({
      total:       s.applications.length,
      applied:     s.applications.filter(a => a.status === 'Applied').length,
      shortlisted: s.applications.filter(a => a.status === 'Shortlisted').length,
      selected:    s.applications.filter(a => a.status === 'Selected').length,
      rejected:    s.applications.filter(a => a.status === 'Rejected').length,
    }),

    recentApplications: s => [...s.applications].slice(0, 5),
  },

  actions: {
    _fresh(key) {
      return this._ts[key] && Date.now() - this._ts[key] < CACHE_TTL
    },

    async fetchProfile(studentId, force = false) {
      if (!force && this._fresh('profile') && this.profile) return
      this.loadingProfile = true
      try {
        this.profile   = await api.get(`/student/${studentId}`)
        this._ts.profile = Date.now()
      } catch (e) { this.error = e.message }
      finally { this.loadingProfile = false }
    },

    async updateProfile(studentId, data) {
      this.loadingProfile = true
      try {
        this.profile = await api.put(`/student/${studentId}`, data)
      } catch (e) { this.error = e.message; throw e }
      finally { this.loadingProfile = false }
    },

    async fetchEligibleDrives(studentId, force = false) {
      if (!force && this._fresh('drives') && this.eligibleDrives.length) return
      this.loadingDrives = true
      try {
        this.eligibleDrives = await api.get(`/student/${studentId}/eligible-drives`)
        this._ts.drives = Date.now()
      } catch (e) { this.error = e.message }
      finally { this.loadingDrives = false }
    },

    async fetchApplications(studentId, force = false) {
      if (!force && this._fresh('apps') && this.applications.length) return
      this.loadingApps = true
      try {
        this.applications = await api.get(`/student/${studentId}/applications`)
        this._ts.apps = Date.now()
      } catch (e) { this.error = e.message }
      finally { this.loadingApps = false }
    },

    async applyToDrive(studentId, driveId, coverLetter = null) {
      const app = await api.post(`/student/${studentId}/apply/${driveId}`, { cover_letter: coverLetter })
      this.applications.unshift(app)
      return app
    },

    async withdrawApplication(studentId, applicationId) {
      await api.delete(`/student/${studentId}/applications/${applicationId}`)
      this.applications = this.applications.filter(a => a.id !== applicationId)
    },

    async uploadResume(studentId, file) {
      const res = await api.upload(`/student/${studentId}/resume`, { resume: file })
      if (this.profile) {
        this.profile.resume_link     = res.resume_link
        this.profile.resume_filename = res.resume_filename
      }
      return res
    },

    async deleteResume(studentId) {
      await api.delete(`/student/${studentId}/resume`)
      if (this.profile) {
        this.profile.resume_link     = null
        this.profile.resume_filename = null
      }
    },

    setFilters(filters) { Object.assign(this.filters, filters) },
    clearFilters()      { this.filters = { search: '', jobType: '', sortBy: 'application_deadline' } },

    saveDrive(drive)   { if (!this.isDriveSaved(drive.id)) this.savedDrives.push(drive) },
    unsaveDrive(id)    { this.savedDrives = this.savedDrives.filter(d => d.id !== id) },
  },
})