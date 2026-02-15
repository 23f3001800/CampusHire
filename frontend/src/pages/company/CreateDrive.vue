<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:780px">

      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">Post a Placement Drive</h3>
          <small class="text-muted">Fill in drive details to start accepting applications</small>
        </div>
        <router-link :to="`/company/${userStore.companyId}`" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <div v-if="successMsg" class="alert alert-success d-flex align-items-center">
        <i class="bi bi-check-circle-fill me-2"></i>{{ successMsg }}
      </div>
      <div v-if="errorMsg" class="alert alert-danger d-flex align-items-center">
        <i class="bi bi-exclamation-circle-fill me-2"></i>{{ errorMsg }}
        <button type="button" class="btn-close ms-auto" @click="errorMsg = ''"></button>
      </div>

      <div class="card border-0 shadow-sm">
        <div class="card-body p-4">

          <!-- Section: Basic Info -->
          <h6 class="section-label">Drive Information</h6>
          <div class="row g-3 mb-4">
            <div class="col-12">
              <label class="form-label fw-semibold">Role / Job Title <span class="text-danger">*</span></label>
              <input class="form-control" v-model="form.title" placeholder="e.g. Software Engineer – Full Stack" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Job Type <span class="text-danger">*</span></label>
              <select class="form-select" v-model="form.job_type">
                <option value="">Select type</option>
                <option>Full-time</option>
                <option>Internship</option>
                <option>Contract</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Location <span class="text-danger">*</span></label>
              <input class="form-control" v-model="form.location" placeholder="Bangalore / Remote" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Job Description</label>
              <textarea class="form-control" v-model="form.description" rows="4"
                placeholder="Describe the role, responsibilities, and what you're looking for…"></textarea>
            </div>
          </div>

          <!-- Section: Salary -->
          <h6 class="section-label">Compensation</h6>
          <div class="row g-3 mb-4">
            <div class="col-md-4">
              <label class="form-label fw-semibold">Currency</label>
              <select class="form-select" v-model="form.currency">
                <option value="INR">INR (₹)</option>
                <option value="USD">USD ($)</option>
                <option value="EUR">EUR (€)</option>
              </select>
            </div>
            <div class="col-md-4">
              <label class="form-label fw-semibold">Min CTC / Stipend</label>
              <input class="form-control" v-model.number="form.salary_min" type="number" min="0" placeholder="500000" />
            </div>
            <div class="col-md-4">
              <label class="form-label fw-semibold">Max CTC / Stipend</label>
              <input class="form-control" v-model.number="form.salary_max" type="number" min="0" placeholder="1200000" />
            </div>
            <div class="col-12">
              <small class="text-muted">
                Preview:
                <strong v-if="form.salary_min || form.salary_max" class="text-success">
                  {{ salaryPreview }}
                </strong>
                <span v-else class="text-muted">Enter salary above</span>
              </small>
            </div>
          </div>

          <!-- Section: Eligibility -->
          <h6 class="section-label">Eligibility Criteria</h6>
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label class="form-label fw-semibold">Minimum CGPA</label>
              <input class="form-control" v-model.number="form.min_cgpa" type="number"
                step="0.1" min="0" max="10" placeholder="0 = no minimum" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Graduation Year</label>
              <input class="form-control" v-model.number="form.eligible_graduation_year" type="number"
                placeholder="2025" min="2020" max="2030" />
              <small class="text-muted">Leave blank for all years</small>
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Eligible Branches</label>
              <div class="d-flex flex-wrap gap-2 p-3 border rounded bg-white">
                <div v-for="b in BRANCHES" :key="b.value" class="form-check mb-0">
                  <input class="form-check-input" type="checkbox"
                    :id="`branch-${b.value}`" :value="b.value" v-model="selectedBranches" />
                  <label class="form-check-label small" :for="`branch-${b.value}`">{{ b.label }}</label>
                </div>
              </div>
              <small class="text-muted">Leave all unchecked = all branches eligible</small>
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Skills Required</label>
              <input class="form-control" v-model="form.skills_required"
                placeholder="Python, Django, SQL (comma-separated)" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold">Experience Required</label>
              <input class="form-control" v-model="form.experience_required"
                placeholder="Freshers / 0-1 years" />
            </div>
          </div>

          <!-- Section: Schedule -->
          <h6 class="section-label">Drive Schedule</h6>
          <div class="row g-3 mb-4">
            <div class="col-md-6">
              <label class="form-label fw-semibold">Application Deadline <span class="text-danger">*</span></label>
              <input class="form-control" v-model="form.application_deadline" type="datetime-local" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold">Drive Date</label>
              <input class="form-control" v-model="form.drive_date" type="datetime-local" />
              <small class="text-muted">Date of interviews / selection</small>
            </div>
          </div>

          <!-- Actions -->
          <div class="d-flex gap-2 justify-content-end pt-3 border-top">
            <button class="btn btn-outline-secondary" @click="resetForm">
              <i class="bi bi-arrow-counterclockwise me-1"></i>Reset
            </button>
            <button class="btn btn-primary px-5" @click="submit" :disabled="loading">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              <i v-else class="bi bi-megaphone me-2"></i>
              {{ loading ? 'Posting…' : 'Post Drive' }}
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

const BRANCHES = [
  { value: 'CSE',   label: 'CSE' },
  { value: 'IT',    label: 'IT' },
  { value: 'ECE',   label: 'ECE' },
  { value: 'EE',    label: 'EE' },
  { value: 'ME',    label: 'ME' },
  { value: 'Civil', label: 'Civil' },
]

const EMPTY_FORM = () => ({
  title: '', job_type: '', location: '', description: '',
  currency: 'INR', salary_min: null, salary_max: null,
  min_cgpa: null, eligible_graduation_year: null,
  skills_required: '', experience_required: '',
  application_deadline: '', drive_date: '',
})

export default {
  name: 'CreateDrive',
  setup() {
    return { store: useCompanyStore(), userStore: useUserStore(), BRANCHES }
  },
  data: () => ({
    form:             EMPTY_FORM(),
    selectedBranches: [],
    loading:    false,
    successMsg: '',
    errorMsg:   '',
  }),
  computed: {
    salaryPreview() {
      const sym = this.form.currency === 'INR' ? '₹' : this.form.currency
      const fmt = v => v >= 100000
        ? `${sym}${(v / 100000).toFixed(1)} LPA`
        : `${sym}${v?.toLocaleString('en-IN')}`
      if (this.form.salary_min && this.form.salary_max)
        return `${fmt(this.form.salary_min)} – ${fmt(this.form.salary_max)}`
      return fmt(this.form.salary_min || this.form.salary_max)
    },
  },
  methods: {
    resetForm() {
      this.form             = EMPTY_FORM()
      this.selectedBranches = []
      this.errorMsg         = ''
      this.successMsg       = ''
    },

    async submit() {
      if (!this.form.title)                  { this.errorMsg = 'Title is required'; return }
      if (!this.form.job_type)               { this.errorMsg = 'Job type is required'; return }
      if (!this.form.location)               { this.errorMsg = 'Location is required'; return }
      if (!this.form.application_deadline)   { this.errorMsg = 'Application deadline is required'; return }

      this.loading    = true
      this.errorMsg   = ''
      this.successMsg = ''

      const payload = {
        ...this.form,
        eligible_branches: this.selectedBranches.join(',') || null,
        // Convert datetime-local strings to ISO
        application_deadline: this.form.application_deadline
          ? new Date(this.form.application_deadline).toISOString() : null,
        drive_date: this.form.drive_date
          ? new Date(this.form.drive_date).toISOString() : null,
      }
      // Strip nulls
      Object.keys(payload).forEach(k => (payload[k] === null || payload[k] === '') && delete payload[k])

      try {
        const drive = await this.store.createDrive(this.userStore.companyId, payload)
        this.successMsg = `"${drive.title}" posted successfully!`
        this.resetForm()
        setTimeout(() => this.$router.push(`/company/${this.userStore.companyId}`), 1500)
      } catch (e) {
        this.errorMsg = e.message || 'Failed to post drive'
      } finally {
        this.loading = false
      }
    },
  },
}
</script>

<style scoped>
.section-label {
  font-size: .7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: #6c757d;
  padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}
</style>