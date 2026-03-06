import { defineStore }  from 'pinia'
import { useUserStore } from './userStore'
import api              from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useStudentStore = defineStore('student', {
  state: () => ({
    // Profile
    profile:        null,
    loadingProfile: false,

    // Drives
    eligibleDrives: [],
    savedDrives:    [],
    loadingDrives:  false,

    // Applications
    applications: [],
    loadingApps:  false,

    // Placements
    placements:        [],
    loadingPlacements: false,

    // Interviews — keyed by application_id
    interviews:       {},
    loadingInterview: false,

    // CSV Export
    csvExport: {
      status:      null,   // null | 'PENDING' | 'SUCCESS' | 'FAILURE'
      taskId:      null,
      downloadUrl: null,
      filename:    null,
      error:       null,
      _pollTimer:  null,
    },

    // Company profile cache — keyed by company_id
    companyCache:      {},
    companyDriveCache: {},

    // Filters
    filters: {
      search:  '',
      jobType: '',
      sortBy:  'application_deadline',
    },

    error: null,
    ts:    {},
  }),

  // ── Getters ──────────────────────────────────────────────────────────────
  getters: {
    // Profile completion — delegates to userStore
    isProfileComplete:      s => useUserStore().isProfileComplete(s.profile, 'student'),
    profileCompletionDetails: s => useUserStore().getProfileCompletionDetails(s.profile, 'student'),
    missingFieldsWithLabels:  s => useUserStore().getMissingFieldsWithLabels(s.profile, 'student'),

    hasResume: s => !!s.profile?.resume_link,

    // Applied drives set
    appliedDriveIds: s => new Set(s.applications.map(a => a.drive_id)),
    hasApplied:      s => driveId => new Set(s.applications.map(a => a.drive_id)).has(driveId),
    isDriveSaved:    s => driveId => s.savedDrives.some(d => d.id === driveId),

    // Filtered eligible drives
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
        application_deadline: (a, b) =>
          new Date(a.application_deadline) - new Date(b.application_deadline),
        salary_max:  (a, b) => (b.salary_max || 0) - (a.salary_max || 0),
        posted_date: (a, b) =>
          new Date(b.posted_date) - new Date(a.posted_date),
      }
      if (sorts[sortBy]) list.sort(sorts[sortBy])
      return list
    },

    urgentDrives: s => s.eligibleDrives.filter(d => {
      if (!d.application_deadline) return false
      const diff = new Date(d.application_deadline) - new Date()
      return diff > 0 && diff <= 3 * 86_400_000
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

    hasActivePlacement: s =>
      s.placements.some(p => p.status === 'Offered' || p.status === 'Joined'),
  },

  // ── Actions ───────────────────────────────────────────────────────────────
  actions: {
    _fresh(key) {
      return this.ts[key] && (Date.now() - this.ts[key]) < CACHE_TTL
    },

    // ── Profile ─────────────────────────────────────────────────────────────
    async fetchProfile(studentId, force = false) {
      if (!force && this._fresh('profile') && this.profile) return
      this.loadingProfile = true
      try {
        this.profile     = await api.get(`/student/${studentId}`)
        this.ts.profile  = Date.now()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loadingProfile = false
      }
    },

    async updateProfile(studentId, data) {
      this.loadingProfile = true
      try {
        this.profile = await api.put(`/student/${studentId}`, data)
        this.ts.profile = Date.now()
      } catch (e) {
        this.error = e.message
        throw e
      } finally {
        this.loadingProfile = false
      }
    },

    // ── Resume ───────────────────────────────────────────────────────────────
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

    // ── Eligible Drives ──────────────────────────────────────────────────────
    async fetchEligibleDrives(studentId, force = false) {
      if (!force && this._fresh('drives') && this.eligibleDrives.length) return

      this.loadingDrives = true

      try {
        const drives = await api.get(`/drives?student_id=${studentId}`)

        this.eligibleDrives = drives.filter(
          d => d.admin_approval_status === 'Approved'
        )

        this.ts.drives = Date.now()
      } 
      catch (e) {
        this.error = e.message
      } 
      finally {
        this.loadingDrives = false
      }
    },

    // Single drive — public endpoint
    async fetchDrive(companyId, driveId) {
      try {
        const drive = await api.get(`/company/${companyId}/drives/${driveId}`)

        if (drive.admin_approval_status !== 'Approved') {
          return null
        }

        return drive
      } catch (e) {
        this.error = e.message
        return null
      }
    },

    // ── Applications ─────────────────────────────────────────────────────────
    async fetchApplications(studentId, force = false) {
      if (!force && this._fresh('apps') && this.applications.length) return
      this.loadingApps = true
      try {
        this.applications = await api.get(`/student/${studentId}/applications`)
        this.ts.apps      = Date.now()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loadingApps = false
      }
    },

    async applyToDrive(studentId, driveId, coverLetter = null) {
      const app = await api.post(
        `/student/${studentId}/apply/${driveId}`,
        { cover_letter: coverLetter }
      )
      this.applications.unshift(app)
      return app
    },

    async withdrawApplication(studentId, applicationId) {
      await api.delete(`/student/${studentId}/applications/${applicationId}`)
      this.applications = this.applications.filter(a => a.id !== applicationId)
    },

    // ── Interview ────────────────────────────────────────────────────────────
    async fetchInterview(companyId, studentId, applicationId, force = false) {
      const key = `interview_${applicationId}`
      if (!force && this._fresh(key) && this.interviews[applicationId]) return
      this.loadingInterview = true
      console.log(`Fetching interview details for application ${applicationId}...`)
      console.log(`API endpoint: /company/${companyId}/applications/${applicationId}/interview?student_id=${studentId}`)
      console.log(`Student ID: ${studentId}, Application ID: ${applicationId}, Company ID: ${companyId}`)
      try {
        this.interviews[applicationId] = await api.get(
          `/company/${companyId}/applications/${applicationId}/interview?student_id=${studentId}`
        )
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loadingInterview = false
      }
    },

    // ── Placements ───────────────────────────────────────────────────────────
    async fetchPlacements(studentId, force = false) {
      if (!force && this._fresh('placements') && this.placements.length) return
      this.loadingPlacements = true
      try {
        this.placements      = await api.get(`/student/${studentId}/placements`)
        this.ts.placements   = Date.now()
      } catch (e) {
        this.error = e.message
      } finally {
        this.loadingPlacements = false
      }
    },

    // ── CSV Export ───────────────────────────────────────────────────────────
    async startCSVExport(studentId) {
      this.csvExport.status      = 'PENDING'
      this.csvExport.taskId      = null
      this.csvExport.downloadUrl = null
      this.csvExport.error       = null

      try {
        const res = await api.post(`/student/${studentId}/export-csv`)
        this.csvExport.taskId = res.task_id
        this._pollCSVStatus(studentId, res.task_id)
      } catch (e) {
        this.csvExport.status = 'FAILURE'
        this.csvExport.error  = e.message
        throw e
      }
    },

    _pollCSVStatus(studentId, taskId) {
      if (this.csvExport._pollTimer)
        clearTimeout(this.csvExport._pollTimer)

      const poll = async () => {
        try {
          const res = await api.get(
            `/student/${studentId}/export-csv/${taskId}/status`
          )
          if (res.status === 'SUCCESS') {
            this.csvExport.status      = 'SUCCESS'
            this.csvExport.downloadUrl = res.download_url
            this.csvExport.filename    = res.filename
          } else if (res.status === 'FAILURE') {
            this.csvExport.status = 'FAILURE'
            this.csvExport.error  = res.error
          } else {
            // Still PENDING — poll again in 2s
            this.csvExport._pollTimer = setTimeout(poll, 2000)
          }
        } catch (e) {
          this.csvExport.status = 'FAILURE'
          this.csvExport.error  = e.message
        }
      }

      this.csvExport._pollTimer = setTimeout(poll, 2000)
    },

    resetCSVExport() {
      if (this.csvExport._pollTimer)
        clearTimeout(this.csvExport._pollTimer)
      this.csvExport = {
        status: null, taskId: null,
        downloadUrl: null, filename: null,
        error: null, _pollTimer: null,
      }
    },

    // ── Company (student-readable) ────────────────────────────────────────────
    async fetchCompanyProfile(companyId, force = false) {
      const key = `company_${companyId}`
      if (!force && this._fresh(key) && this.companyCache[companyId]) return
      try {
        this.companyCache[companyId] = await api.get(`/company/${companyId}`)
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message
      }
    },

    async fetchCompanyDrives(companyId, force = false) {
      const key = `companyDrives_${companyId}`
      if (!force && this._fresh(key) && this.companyDriveCache[companyId]) return
      try {
        this.companyDriveCache[companyId] = await api.get(`/company/${companyId}/drives`)
        this.ts[key] = Date.now()
      } catch (e) {
        this.error = e.message
      }
    },

    // ── Filters ───────────────────────────────────────────────────────────────
    setFilters(filters)  { Object.assign(this.filters, filters) },
    clearFilters()       { this.filters = { search: '', jobType: '', sortBy: 'application_deadline' } },

    // ── Saved Drives ──────────────────────────────────────────────────────────
    saveDrive(drive)     { if (!this.isDriveSaved(drive.id)) this.savedDrives.push(drive) },
    unsaveDrive(id)      { this.savedDrives = this.savedDrives.filter(d => d.id !== id) },
  },
})
