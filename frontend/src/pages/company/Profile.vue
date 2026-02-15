<template>
  <div class="profile-page bg-light min-vh-100 py-4">
    <div class="container" style="max-width:860px">

      <!-- Header -->
      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">Company Profile</h3>
          <small class="text-muted">Complete your profile to start posting placement drives</small>
        </div>
        <router-link :to="`/company/${userStore.companyId}`" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <!-- Completion banner -->
      <div class="card shadow-sm border-0 mb-4 border-start border-4"
        :class="store.isProfileComplete ? 'border-success' : 'border-warning'">
        <div class="card-body py-3">
          <div class="d-flex align-items-center gap-3">
            <div class="flex-grow-1">
              <div class="d-flex justify-content-between mb-1">
                <small class="fw-bold">Profile Completion</small>
                <small class="fw-bold">{{ store.profileCompletionDetails.percentage }}%</small>
              </div>
              <div class="progress" style="height:8px">
                <div class="progress-bar"
                  :class="store.profileCompletionDetails.percentage >= 70 ? 'bg-success' : store.profileCompletionDetails.percentage >= 40 ? 'bg-warning' : 'bg-danger'"
                  :style="{ width: store.profileCompletionDetails.percentage + '%' }">
                </div>
              </div>
              <div v-if="store.missingFieldsWithLabels.required.length" class="mt-1">
                <small class="text-danger">
                  Required: {{ store.missingFieldsWithLabels.required.map(f => f.label).join(', ') }}
                </small>
              </div>
            </div>
            <span class="badge px-3 py-2" :class="approvalBadge">
              {{ store.approvalStatus }}
            </span>
          </div>
        </div>
      </div>

      <!-- Alerts -->
      <div v-if="successMsg" class="alert alert-success d-flex align-items-center">
        <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
        <button type="button" class="btn-close ms-auto" @click="successMsg = ''"></button>
      </div>
      <div v-if="errorMsg" class="alert alert-danger d-flex align-items-center">
        <i class="bi bi-exclamation-circle-fill me-2"></i>{{ errorMsg }}
        <button type="button" class="btn-close ms-auto" @click="errorMsg = ''"></button>
      </div>

      <!-- Tabs -->
      <ul class="nav nav-tabs mb-0">
        <li class="nav-item" v-for="t in tabs" :key="t.key">
          <a class="nav-link" :class="{ active: activeTab === t.key }"
            @click.prevent="activeTab = t.key" href="#">
            <i :class="`bi ${t.icon} me-1`"></i>{{ t.label }}
          </a>
        </li>
      </ul>

      <div class="card border-0 shadow-sm rounded-top-0">
        <div class="card-body p-4">

          <!-- ── COMPANY INFO ── -->
          <div v-show="activeTab === 'company'">
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label fw-semibold">Company Name <span class="text-danger">*</span></label>
                <input class="form-control form-control-lg" v-model="form.company_name"
                  placeholder="Tech Solutions Inc." />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Industry <span class="text-danger">*</span></label>
                <select class="form-select" v-model="form.industry">
                  <option value="">Select industry</option>
                  <option>Information Technology</option>
                  <option>Software Product</option>
                  <option>Banking & Finance</option>
                  <option>Consulting</option>
                  <option>E-Commerce</option>
                  <option>Manufacturing</option>
                  <option>Healthcare</option>
                  <option>Education</option>
                  <option>Other</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Company Size</label>
                <select class="form-select" v-model="form.company_size">
                  <option value="">Select size</option>
                  <option value="Startup">Startup (1–50)</option>
                  <option value="Small">Small (51–200)</option>
                  <option value="Medium">Medium (201–1000)</option>
                  <option value="Large">Large (1000+)</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Headquarters Location <span class="text-danger">*</span></label>
                <input class="form-control" v-model="form.location" placeholder="Bangalore, Karnataka" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Website</label>
                <input class="form-control" v-model="form.website" placeholder="https://company.com" />
              </div>

              <!-- Logo upload -->
              <div class="col-12">
                <label class="form-label fw-semibold">Company Logo URL</label>
                <div class="input-group">
                  <span class="input-group-text bg-white">
                    <img v-if="form.logo_url" :src="form.logo_url"
                      class="rounded" style="width:24px;height:24px;object-fit:cover"
                      @error="form.logo_url = ''" />
                    <i v-else class="bi bi-image text-muted"></i>
                  </span>
                  <input class="form-control" v-model="form.logo_url"
                    placeholder="https://company.com/logo.png" />
                </div>
              </div>

              <div class="col-12">
                <label class="form-label fw-semibold">Company Description</label>
                <textarea class="form-control" v-model="form.description" rows="4"
                  placeholder="Tell students about your company, culture, and what makes you a great place to work…"
                  maxlength="1000"></textarea>
                <small class="text-muted">{{ (form.description || '').length }}/1000</small>
              </div>
            </div>
          </div>

          <!-- ── HR CONTACT ── -->
          <div v-show="activeTab === 'hr'">
            <div class="row g-3">
              <div class="col-12">
                <div class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  These details are shown to students when they apply to your drives.
                </div>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Recruiter Name</label>
                <input class="form-control" :value="store.profile?.recruiter_name || ''" disabled />
                <small class="text-muted">Change via account settings</small>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Recruiter Email</label>
                <input class="form-control" :value="store.profile?.recruiter_email || ''" disabled />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">HR Contact Number <span class="text-danger">*</span></label>
                <input class="form-control" v-model="form.hr_contact" type="tel" placeholder="+91 98765 43210" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">HR Email</label>
                <input class="form-control" v-model="form.hr_email" type="email" placeholder="hr@company.com" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Department</label>
                <input class="form-control" v-model="form.department" placeholder="Human Resources" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Designation</label>
                <input class="form-control" v-model="form.designation" placeholder="HR Manager" />
              </div>
            </div>
          </div>

          <!-- Save button -->
          <div class="d-flex justify-content-end mt-4 pt-3 border-top">
            <button class="btn btn-primary px-5" @click="save" :disabled="store.loadingProfile">
              <span v-if="store.loadingProfile" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-check-lg me-2"></i>
              {{ store.loadingProfile ? 'Saving…' : 'Save Changes' }}
            </button>
          </div>

        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useCompanyStore } from '@/stores/companyStore'
import { useUserStore }    from '@/stores/userStore'

export default {
  name: 'CompanyProfile',
  setup() {
    return {
      store:     useCompanyStore(),
      userStore: useUserStore(),
    }
  },
  data: () => ({
    activeTab:  'company',
    form:       {},
    successMsg: '',
    errorMsg:   '',
  }),
  computed: {
    tabs: () => [
      { key: 'company', label: 'Company Info', icon: 'bi-building' },
      { key: 'hr',      label: 'HR Contact',   icon: 'bi-person-badge' },
    ],
    approvalBadge() {
      return {
        Pending:  'bg-warning text-dark',
        Approved: 'bg-success',
        Rejected: 'bg-danger',
      }[this.store.approvalStatus] || 'bg-secondary'
    },
  },
  async mounted() {
    await this.store.fetchProfile(this.userStore.companyId)
    this._resetForm()
  },
  methods: {
    _resetForm() {
      const p = this.store.profile || {}
      this.form = {
        company_name: p.company_name || '',
        industry:     p.industry     || '',
        company_size: p.company_size || '',
        location:     p.location     || '',
        website:      p.website      || '',
        description:  p.description  || '',
        logo_url:     p.logo_url     || '',
        hr_contact:   p.hr_contact   || '',
        hr_email:     p.hr_email     || '',
        department:   p.department   || '',
        designation:  p.designation  || '',
      }
    },

    async save() {
      this.successMsg = ''
      this.errorMsg   = ''
      const payload = Object.fromEntries(
        Object.entries(this.form).filter(([, v]) => v !== '' && v !== null)
      )
      try {
        await this.store.updateProfile(this.userStore.companyId, payload)
        this.successMsg = 'Profile saved successfully!'
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (e) {
        this.errorMsg = e.message || 'Failed to save profile'
      }
    },
  },
}
</script>

<style scoped>
.nav-tabs .nav-link        { color: #6c757d; border: none; border-bottom: 3px solid transparent; }
.nav-tabs .nav-link.active { color: #0d6efd; border-bottom-color: #0d6efd; background: none; font-weight: 600; }
.nav-tabs .nav-link:hover  { color: #0d6efd; }
</style>