import { defineStore } from 'pinia'
import api from '@/utils/api'

// ── Profile completion rules ─────────────────────────────────────────────────
const RULES = {
  student: {
    required:    ['phone', 'gender', 'graduation_year', 'branch'],
    recommended: ['cgpa', 'skills', 'resume_link', 'linkedin_url'],
  },
  company: {
    required:    ['company_name', 'hr_contact', 'industry', 'location'],
    recommended: ['website', 'description', 'company_size', 'logo_url'],
  },
}

const LABELS = {
  phone:        'Phone Number',
  gender:       'Gender',
  graduation_year: 'Graduation Year',
  branch:       'Branch / Department',
  cgpa:         'CGPA',
  skills:       'Skills',
  resume_link:  'Resume',
  linkedin_url: 'LinkedIn URL',
  company_name: 'Company Name',
  hr_contact:   'HR Contact',
  industry:     'Industry',
  location:     'Location',
  website:      'Website',
  description:  'Company Description',
  company_size: 'Company Size',
  logo_url:     'Company Logo',
}

function isFilled(v) {
  return v !== null && v !== undefined && String(v).trim() !== ''
}

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user:  JSON.parse(localStorage.getItem('user') || 'null'),
  }),

  getters: {
    isAuthenticated: s => !!s.token,
    role:            s => s.user?.role || null,
    id:              s => s.user?.id   || null,
    studentId:       s => s.user?.student_id || null,
    companyId:       s => s.user?.company_id || null,
    userName:        s => s.user?.name  || '',
    userEmail:       s => s.user?.email || '',
    isStudent:       s => s.user?.role === 'student',
    isCompany:       s => s.user?.role === 'company',
    isAdmin:         s => s.user?.role === 'admin',
    isInitialized:   s => s.user !== null || s.token === null,
  },

  actions: {
    // ── Auth ────────────────────────────────────────────────────────────────
    async loginWithCredentials(endpoint, credentials) {
      const res = await api.post(endpoint, credentials)
      this._persist(res.token, res.user)
      return res
    },

    async logout() {
      try { await api.post('/auth/logout') } catch (_) { /* ignore */ }
      this._clear()
      if (window.$router) window.$router.push('/login')
    },

    async initialize() {
      if (!this.token) return
      try {
        const res = await api.get('/auth/me')
        this._persist(this.token, res.user)
      } catch (_) {
        this._clear()
      }
    },

    _persist(token, user) {
      this.token = token
      this.user  = user
      localStorage.setItem('token', token)
      localStorage.setItem('user',  JSON.stringify(user))
    },

    _clear() {
      this.token = null
      this.user  = null
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    },

    // ── Profile Completion (shared by student & company stores) ─────────────
    isProfileComplete(profile, role) {
      if (!profile || !RULES[role]) return false
      return RULES[role].required.every(f => isFilled(profile[f]))
    },

    getProfileCompletionDetails(profile, role) {
      if (!profile || !RULES[role]) {
        return { percentage: 0, missingRequired: [], missingRecommended: [], filledRequired: [], filledRecommended: [] }
      }
      const { required, recommended } = RULES[role]
      const missingRequired    = required.filter(f    => !isFilled(profile[f]))
      const filledRequired     = required.filter(f    => isFilled(profile[f]))
      const missingRecommended = recommended.filter(f => !isFilled(profile[f]))
      const filledRecommended  = recommended.filter(f => isFilled(profile[f]))

      const reqPct  = required.length    ? (filledRequired.length    / required.length)    * 70 : 70
      const recPct  = recommended.length ? (filledRecommended.length / recommended.length) * 30 : 30
      const percentage = Math.round(reqPct + recPct)

      return { percentage, missingRequired, missingRecommended, filledRequired, filledRecommended }
    },

    getMissingFieldsWithLabels(profile, role) {
      const details = this.getProfileCompletionDetails(profile, role)
      return {
        required:    details.missingRequired.map(k    => ({ key: k, label: LABELS[k] || k })),
        recommended: details.missingRecommended.map(k => ({ key: k, label: LABELS[k] || k })),
      }
    },
  },
})