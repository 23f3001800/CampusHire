import { defineStore } from 'pinia'
import { useUserStore } from './userStore'
import api from '@/utils/api'

const CACHE_TTL = 5 * 60 * 1000

export const useCompanyStore = defineStore('company', {
  state: () => ({
    profile:    null,
    drives:     [],
    applicants: {},   // { [driveId]: Application[] }
    loading:        false,
    loadingProfile: false,
    loadingDrives:  false,
    error:          null,
    _ts: {},
  }),

  getters: {
    // ── Profile completion (delegates to userStore) ──────────────────────
    isProfileComplete(state) {
      return useUserStore().isProfileComplete(state.profile, 'company')
    },
    profileCompletionDetails(state) {
      return useUserStore().getProfileCompletionDetails(state.profile, 'company')
    },
    missingFieldsWithLabels(state) {
      return useUserStore().getMissingFieldsWithLabels(state.profile, 'company')
    },

    companyName:     s => s.profile?.company_name || '',
    approvalStatus:  s => s.profile?.approval_status || 'Pending',
    isApproved:      s => s.profile?.approval_status === 'Approved',

    activeDrives:    s => s.drives.filter(d => d.status === 'Open'),
    closedDrives:    s => s.drives.filter(d => d.status === 'Closed'),
    completedDrives: s => s.drives.filter(d => d.status === 'Completed'),

    getDriveById:    s => id => s.drives.find(d => d.id === id) || null,

    totalApplicants: s => Object.values(s.applicants)
                              .reduce((sum, arr) => sum + arr.length, 0),

    getApplicantsForDrive: s => driveId => s.applicants[driveId] || [],

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

    recentApplicants: s => Object.values(s.applicants)
                               .flat()
                               .sort((a, b) => new Date(b.applied_date) - new Date(a.applied_date))
                               .slice(0, 10),
  },

  actions: {
    _fresh(key) {
      return this._ts[key] && Date.now() - this._ts[key] < CACHE_TTL
    },

    async fetchProfile(companyId, force = false) {
      if (!force && this._fresh('profile') && this.profile) return
      this.loadingProfile = true
      try {
        this.profile     = await api.get(`/company/${companyId}`)
        this._ts.profile = Date.now()
      } catch (e) { this.error = e.message }
      finally { this.loadingProfile = false }
    },

    async updateProfile(companyId, data) {
      this.loadingProfile = true
      try {
        this.profile = await api.put(`/company/${companyId}`, data)
      } catch (e) { this.error = e.message; throw e }
      finally { this.loadingProfile = false }
    },

    async fetchDrives(companyId, force = false) {
      if (!force && this._fresh('drives') && this.drives.length) return
      this.loadingDrives = true
      try {
        this.drives     = await api.get(`/company/${companyId}/drives`)
        this._ts.drives = Date.now()
      } catch (e) { this.error = e.message }
      finally { this.loadingDrives = false }
    },

    async createDrive(companyId, data) {
      const drive = await api.post(`/company/${companyId}/drives`, data)
      this.drives.unshift(drive)
      return drive
    },

    async updateDrive(companyId, driveId, data) {
      const updated = await api.put(`/company/${companyId}/drives/${driveId}`, data)
      const i = this.drives.findIndex(d => d.id === driveId)
      if (i !== -1) this.drives[i] = updated
      return updated
    },

    async toggleDriveStatus(companyId, driveId) {
      const updated = await api.patch(`/company/${companyId}/drives/${driveId}`)
      const i = this.drives.findIndex(d => d.id === driveId)
      if (i !== -1) this.drives[i] = updated
      return updated
    },

    async deleteDrive(companyId, driveId) {
      await api.delete(`/company/${companyId}/drives/${driveId}`)
      this.drives = this.drives.filter(d => d.id !== driveId)
    },

    async fetchApplicants(companyId, driveId, force = false) {
      const key = `apps_${driveId}`
      if (!force && this._fresh(key) && this.applicants[driveId]) return
      try {
        this.applicants[driveId] = await api.get(`/company/${companyId}/drives/${driveId}/applicants`)
        this._ts[key] = Date.now()
      } catch (e) { this.error = e.message }
    },

    async updateApplicationStatus(companyId, driveId, applicationId, status, notes = null) {
      const updated = await api.put(
        `/company/${companyId}/drives/${driveId}/applicants/${applicationId}`,
        { status, notes }
      )
      if (this.applicants[driveId]) {
        const i = this.applicants[driveId].findIndex(a => a.id === applicationId)
        if (i !== -1) this.applicants[driveId][i] = updated
      }
      return updated
    },
  },
})