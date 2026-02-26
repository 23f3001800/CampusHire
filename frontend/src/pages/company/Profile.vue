<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:780px">

      <!-- Loading -->
      <div v-if="store.loadingProfile && !store.profile"
           class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <template v-else>

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="alert d-flex align-items-center
                      gap-2 shadow-sm mb-3"
               :class="`alert-${toast.type}`" role="alert">
            <i class="bi flex-shrink-0"
               :class="toast.type === 'success'
                 ? 'bi-check-circle-fill'
                 : 'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1">{{ toast.message }}</span>
            <button class="btn-close"
                    @click="toast.show = false"></button>
          </div>
        </Transition>

        <!-- Header -->
        <div class="d-flex align-items-center
                    justify-content-between mb-4">
          <div>
            <router-link to="/company"
                         class="btn btn-outline-secondary
                                btn-sm mb-2">
              <i class="bi bi-arrow-left me-1"></i>Dashboard
            </router-link>
            <h3 class="fw-bold mb-0">Company Profile</h3>
            <small class="text-muted">
              Manage your company details and recruiter info
            </small>
          </div>
          <!-- Approval badge -->
          <span class="badge fs-6 px-3 py-2"
                :class="approvalBadge(store.approvalStatus)">
            {{ store.approvalStatus }}
          </span>
        </div>

        <!-- Profile completion card -->
        <div v-if="!store.isProfileComplete"
             class="card border-warning shadow-sm mb-4">
          <div class="card-body py-3">
            <div class="d-flex align-items-center
                        justify-content-between mb-2">
              <span class="fw-semibold small text-warning">
                <i class="bi bi-exclamation-triangle
                           me-1"></i>Profile Incomplete
              </span>
              <span class="fw-bold">
                {{ store.profileCompletionDetails.percentage }}%
              </span>
            </div>
            <div class="progress mb-2" style="height:8px">
              <div class="progress-bar"
                   :class="progressClass(
                     store.profileCompletionDetails.percentage
                   )"
                   :style="{
                     width:
                       store.profileCompletionDetails.percentage
                       + '%'
                   }">
              </div>
            </div>
            <div class="d-flex flex-wrap gap-1">
              <span v-for="f in store.missingFieldsWithLabels
                                      .required"
                    :key="f.key"
                    class="badge bg-danger bg-opacity-15
                           text-danger small">
                {{ f.label }}
              </span>
            </div>
          </div>
        </div>

        <!-- Tabs -->
        <ul class="nav nav-tabs mb-4">
          <li class="nav-item" v-for="t in tabs" :key="t.key">
            <a class="nav-link"
               :class="{ active: activeTab === t.key }"
               @click.prevent="activeTab = t.key" href="#">
              <i :class="`bi ${t.icon} me-1`"></i>{{ t.label }}
            </a>
          </li>
        </ul>

        <form @submit.prevent="save" novalidate>

          <!-- ── Tab: Company Info ── -->
          <div v-if="activeTab === 'company'"
               class="card border-0 shadow-sm">
            <div class="card-body p-4">
              <h6 class="section-label">Company Information</h6>
              <div class="row g-3 mb-4">

                <!-- Logo preview -->
                <div class="col-12 d-flex
                            align-items-center gap-3 mb-1">
                  <img v-if="form.logo_url"
                       :src="form.logo_url"
                       class="rounded-3 border"
                       style="width:64px;height:64px;
                              object-fit:cover"
                       @error="form.logo_url = ''" />
                  <div v-else class="company-avatar-lg">
                    {{ initials(form.company_name) }}
                  </div>
                  <div>
                    <label class="form-label fw-semibold mb-1
                                  small">
                      Logo URL
                    </label>
                    <input class="form-control form-control-sm"
                           v-model.trim="form.logo_url"
                           placeholder="https://…/logo.png" />
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold">
                    Company Name
                    <span class="text-danger">*</span>
                  </label>
                  <input class="form-control"
                         :class="{'is-invalid': errors.company_name}"
                         v-model.trim="form.company_name"
                         maxlength="255" />
                  <div class="invalid-feedback">
                    {{ errors.company_name }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Industry <span class="text-danger">*</span>
                  </label>
                  <select class="form-select"
                          :class="{'is-invalid': errors.industry}"
                          v-model="form.industry">
                    <option value="">Select industry</option>
                    <option v-for="i in INDUSTRIES"
                            :key="i" :value="i">{{ i }}</option>
                  </select>
                  <div class="invalid-feedback">
                    {{ errors.industry }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Company Size
                  </label>
                  <select class="form-select"
                          v-model="form.company_size">
                    <option value="">Select size</option>
                    <option value="Startup">
                      Startup (&lt;10)
                    </option>
                    <option value="Small">Small (10–50)</option>
                    <option value="Medium">
                      Medium (50–500)
                    </option>
                    <option value="Large">Large (500+)</option>
                  </select>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Location <span class="text-danger">*</span>
                  </label>
                  <input class="form-control"
                         :class="{'is-invalid': errors.location}"
                         v-model.trim="form.location"
                         maxlength="255" />
                  <div class="invalid-feedback">
                    {{ errors.location }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Website
                  </label>
                  <input class="form-control"
                         :class="{'is-invalid': errors.website}"
                         v-model.trim="form.website"
                         type="url"
                         placeholder="https://yourcompany.com" />
                  <div class="invalid-feedback">
                    {{ errors.website }}
                  </div>
                </div>

                <div class="col-12">
                  <label class="form-label fw-semibold">
                    About Company
                  </label>
                  <textarea class="form-control"
                             v-model.trim="form.description"
                             rows="4"
                             maxlength="2000"
                             placeholder="Describe your company, culture, and values…">
                  </textarea>
                  <div class="form-text text-end">
                    {{ (form.description || '').length }}/2000
                  </div>
                </div>

              </div>
            </div>
          </div>

          <!-- ── Tab: Recruiter Info ── -->
          <div v-if="activeTab === 'recruiter'"
               class="card border-0 shadow-sm">
            <div class="card-body p-4">
              <h6 class="section-label">Recruiter / HR Details</h6>
              <div class="row g-3 mb-4">

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    HR Contact Name
                    <span class="text-danger">*</span>
                  </label>
                  <input class="form-control"
                         :class="{'is-invalid': errors.hr_contact}"
                         v-model.trim="form.hr_contact"
                         maxlength="120" />
                  <div class="invalid-feedback">
                    {{ errors.hr_contact }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    HR Email
                  </label>
                  <input class="form-control"
                         :class="{'is-invalid': errors.hr_email}"
                         v-model.trim="form.hr_email"
                         type="email" />
                  <div class="invalid-feedback">
                    {{ errors.hr_email }}
                  </div>
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Department
                  </label>
                  <input class="form-control"
                         v-model.trim="form.department"
                         maxlength="100"
                         placeholder="Human Resources" />
                </div>

                <div class="col-md-6">
                  <label class="form-label fw-semibold">
                    Designation
                  </label>
                  <input class="form-control"
                         v-model.trim="form.designation"
                         maxlength="100"
                         placeholder="Senior HR Manager" />
                </div>

              </div>
            </div>
          </div>

          <!-- Save button -->
          <div class="d-flex gap-2 justify-content-end mt-4">
            <button type="button"
                    class="btn btn-outline-secondary"
                    @click="resetForm">
              <i class="bi bi-arrow-counterclockwise me-1"></i>
              Reset
            </button>
            <button type="submit"
                    class="btn btn-primary px-5"
                    :disabled="store.loadingProfile">
              <span v-if="store.loadingProfile"
                    class="spinner-border
                           spinner-border-sm me-2"></span>
              <i v-else class="bi bi-floppy me-2"></i>
              {{ store.loadingProfile
                  ? 'Saving…' : 'Save Profile' }}
            </button>
          </div>

        </form>

      </template>
    </div>
  </div>
</template>

<script>
import { useCompanyStore } from '@/stores/companyStore'
import { useUserStore }    from '@/stores/userStore'

const INDUSTRIES = [
  'Technology', 'Finance', 'Healthcare', 'Manufacturing',
  'Retail', 'Education', 'Consulting', 'Media',
  'Telecommunications', 'Automotive', 'Other',
]

const EMPTY_FORM = p => ({
  company_name: p?.company_name  || '',
  industry:     p?.industry      || '',
  company_size: p?.company_size  || '',
  location:     p?.location      || '',
  website:      p?.website       || '',
  description:  p?.description   || '',
  logo_url:     p?.logo_url      || '',
  hr_contact:   p?.hr_contact    || '',
  hr_email:     p?.hr_email      || '',
  department:   p?.department    || '',
  designation:  p?.designation   || '',
})

export default {
  name: 'CompanyProfile',

  setup() {
    return {
      store:     useCompanyStore(),
      userStore: useUserStore(),
      INDUSTRIES,
    }
  },

  data() {
    return {
      activeTab: 'company',
      form:      EMPTY_FORM(null),
      errors:    {},
      toast:     { show: false, type: 'success', message: '' },
      tabs: [
        { key: 'company',   label: 'Company Info',   icon: 'bi-building'    },
        { key: 'recruiter', label: 'Recruiter Info',  icon: 'bi-person-badge'},
      ],
    }
  },

  async mounted() {
    const cid = this.userStore.companyId
    await this.store.fetchProfile(cid)
    this.resetForm()
  },

  methods: {
    resetForm() {
      this.form   = EMPTY_FORM(this.store.profile)
      this.errors = {}
    },

    validate() {
      const e = {}, f = this.form
      if (!f.company_name?.trim())
        e.company_name = 'Company name is required.'
      if (!f.industry)
        e.industry = 'Industry is required.'
      if (!f.location?.trim())
        e.location = 'Location is required.'
      if (!f.hr_contact?.trim())
        e.hr_contact = 'HR contact name is required.'
      if (f.hr_email && !/\S+@\S+\.\S+/.test(f.hr_email))
        e.hr_email = 'Enter a valid email.'
      if (f.website && !f.website.startsWith('http'))
        e.website = 'URL must start with http(s)://'
      this.errors = e
      return !Object.keys(e).length
    },

    // PUT /company/:id  → returns updated company_fields
    async save() {
      if (!this.validate()) {
        // Switch to the tab that has the first error
        if (this.errors.company_name ||
            this.errors.industry ||
            this.errors.location)
          this.activeTab = 'company'
        else
          this.activeTab = 'recruiter'
        return
      }
      try {
        const payload = { ...this.form }
        // Strip empty strings to avoid overwriting with ''
        Object.keys(payload).forEach(k => {
          if (payload[k] === '') delete payload[k]
        })
        await this.store.updateProfile(
          this.userStore.companyId, payload
        )
        this.showToast('success', 'Profile saved successfully.')
        this.errors = {}
      } catch (e) {
        this.showToast(
          'danger', e?.message ?? 'Failed to save profile.'
        )
      }
    },

    showToast(type, message, ms = 4000) {
      this.toast = { show: true, type, message }
      setTimeout(() => { this.toast.show = false }, ms)
    },

    progressClass(p) {
      return p < 30 ? 'bg-danger' : p < 70 ? 'bg-warning' : 'bg-success'
    },

    initials(name) {
      return (name || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },

    approvalBadge(s) {
      return {
        Pending:  'bg-warning text-dark',
        Approved: 'bg-success',
        Rejected: 'bg-danger',
      }[s] ?? 'bg-secondary'
    },
  },
}
</script>

<style scoped>
.company-avatar-lg {
  width: 64px; height: 64px; border-radius: 12px;
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  color: #fff; display: flex; align-items: center;
  justify-content: center;
  font-size: 1.4rem; font-weight: 700; flex-shrink: 0;
}
.section-label {
  font-size: .7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  color: #6c757d; padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
.nav-tabs .nav-link {
  color: #6c757d; border: none;
  border-bottom: 2px solid transparent;
}
.nav-tabs .nav-link.active {
  color: #0d6efd; border-bottom-color: #0d6efd; background: none;
}
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from, .fade-leave-to       { opacity: 0; }
</style>
