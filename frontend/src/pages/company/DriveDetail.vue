<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:900px">

      <!-- Header -->
      <div class="d-flex align-items-center justify-content-between mb-4">
        <button class="btn btn-outline-secondary btn-sm" @click="$router.back()">
          <i class="bi bi-arrow-left me-1"></i>Back
        </button>
        <div class="d-flex gap-2">
          <button class="btn btn-outline-primary btn-sm" @click="editMode = !editMode">
            <i class="bi" :class="editMode ? 'bi-x-lg' : 'bi-pencil'"></i>
            {{ editMode ? 'Cancel' : 'Edit Drive' }}
          </button>
          <button class="btn btn-sm" :class="drive?.status === 'Open' ? 'btn-warning' : 'btn-success'"
            @click="toggleStatus" :disabled="toggling">
            <span v-if="toggling" class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi me-1" :class="drive?.status === 'Open' ? 'bi-toggle-on' : 'bi-toggle-off'"></i>
            {{ drive?.status === 'Open' ? 'Close Drive' : 'Reopen Drive' }}
          </button>
          <button class="btn btn-outline-danger btn-sm" @click="deleteDrive">
            <i class="bi bi-trash me-1"></i>Delete
          </button>
        </div>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="!drive" class="text-center py-5 text-muted">
        Drive not found.
      </div>

      <template v-else>

        <!-- ── VIEW MODE ─────────────────────────────────────────────────── -->
        <template v-if="!editMode">

          <!-- Title card -->
          <div class="card border-0 shadow-sm mb-4">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h3 class="fw-bold mb-1">{{ drive.title }}</h3>
                  <p class="text-muted mb-0">
                    <i class="bi bi-geo-alt me-1"></i>{{ drive.location || '—' }}
                    <span class="mx-2">·</span>
                    <i class="bi bi-briefcase me-1"></i>{{ drive.job_type || '—' }}
                  </p>
                </div>
                <span class="badge fs-6 px-3 py-2"
                  :class="{ Open: 'bg-success', Closed: 'bg-secondary', Completed: 'bg-primary' }[drive.status]">
                  {{ drive.status }}
                </span>
              </div>

              <div class="row g-3 mt-3">
                <div class="col-sm-6 col-md-3">
                  <div class="info-chip">
                    <small class="text-muted">CTC / Stipend</small>
                    <div class="fw-bold text-success">{{ salaryText }}</div>
                  </div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div class="info-chip">
                    <small class="text-muted">Min CGPA</small>
                    <div class="fw-bold">{{ drive.min_cgpa || 'None' }}</div>
                  </div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div class="info-chip">
                    <small class="text-muted">Grad Year</small>
                    <div class="fw-bold">{{ drive.eligible_graduation_year || 'Any' }}</div>
                  </div>
                </div>
                <div class="col-sm-6 col-md-3">
                  <div class="info-chip">
                    <small class="text-muted">Total Applied</small>
                    <div class="fw-bold text-primary">{{ drive.total_applications }}</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Stats row -->
          <div class="row g-3 mb-4">
            <div class="col-6 col-md-3" v-for="s in appStats" :key="s.label">
              <div class="card border-0 shadow-sm text-center py-3">
                <div class="fw-bold fs-4" :class="s.color">{{ s.value }}</div>
                <small class="text-muted">{{ s.label }}</small>
              </div>
            </div>
          </div>

          <!-- Details -->
          <div class="row g-4">
            <div class="col-md-8">
              <div class="card border-0 shadow-sm h-100">
                <div class="card-body p-4">
                  <h6 class="section-label">Description</h6>
                  <p class="text-muted" style="white-space:pre-wrap">{{ drive.description || 'No description provided.' }}</p>

                  <h6 class="section-label mt-4">Skills Required</h6>
                  <div class="d-flex flex-wrap gap-1" v-if="drive.skills_required">
                    <span v-for="skill in drive.skills_required.split(',')" :key="skill"
                      class="badge bg-primary bg-opacity-10 text-primary">
                      {{ skill.trim() }}
                    </span>
                  </div>
                  <p v-else class="text-muted small">None specified</p>

                  <h6 class="section-label mt-4">Eligible Branches</h6>
                  <div class="d-flex flex-wrap gap-1" v-if="drive.eligible_branches">
                    <span v-for="branch in drive.eligible_branches.split(',')" :key="branch"
                      class="badge bg-info bg-opacity-10 text-info">
                      {{ branch.trim() }}
                    </span>
                  </div>
                  <p v-else class="text-muted small">All branches</p>
                </div>
              </div>
            </div>

            <div class="col-md-4">
              <div class="card border-0 shadow-sm">
                <div class="card-body p-4">
                  <h6 class="section-label">Schedule</h6>
                  <div class="d-flex flex-column gap-3">
                    <div>
                      <small class="text-muted d-block">Application Deadline</small>
                      <span class="fw-bold" :class="isUrgent ? 'text-danger' : ''">
                        {{ formatDate(drive.application_deadline) }}
                      </span>
                      <span v-if="isUrgent" class="badge bg-danger ms-1">Urgent</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Drive Date</small>
                      <span class="fw-bold">{{ formatDate(drive.drive_date) }}</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Posted</small>
                      <span>{{ formatDate(drive.posted_date) }}</span>
                    </div>
                    <div>
                      <small class="text-muted d-block">Experience</small>
                      <span>{{ drive.experience_required || 'Freshers' }}</span>
                    </div>
                  </div>

                  <div class="mt-4 d-grid">
                    <router-link :to="`/company/drives/${driveId}/applicants`"
                      class="btn btn-primary">
                      <i class="bi bi-people me-2"></i>View Applicants
                      <span class="badge bg-white text-primary ms-1">{{ drive.total_applications }}</span>
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </template>

        <!-- ── EDIT MODE ─────────────────────────────────────────────────── -->
        <div v-else class="card border-0 shadow-sm">
          <div class="card-body p-4">
            <h5 class="fw-bold mb-4">Edit Drive</h5>

            <div class="row g-3">
              <div class="col-12">
                <label class="form-label fw-semibold">Title <span class="text-danger">*</span></label>
                <input class="form-control" v-model="editForm.title" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Job Type</label>
                <select class="form-select" v-model="editForm.job_type">
                  <option>Full-time</option><option>Internship</option><option>Contract</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Location</label>
                <input class="form-control" v-model="editForm.location" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Currency</label>
                <select class="form-select" v-model="editForm.currency">
                  <option value="INR">INR</option><option value="USD">USD</option>
                </select>
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Min Salary</label>
                <input class="form-control" v-model.number="editForm.salary_min" type="number" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Max Salary</label>
                <input class="form-control" v-model.number="editForm.salary_max" type="number" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Min CGPA</label>
                <input class="form-control" v-model.number="editForm.min_cgpa" type="number" step="0.1" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Grad Year</label>
                <input class="form-control" v-model.number="editForm.eligible_graduation_year" type="number" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Experience</label>
                <input class="form-control" v-model="editForm.experience_required" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Eligible Branches</label>
                <input class="form-control" v-model="editForm.eligible_branches" placeholder="CSE,ECE,IT" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Skills Required</label>
                <input class="form-control" v-model="editForm.skills_required" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Application Deadline</label>
                <input class="form-control" v-model="editForm.application_deadline" type="datetime-local" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Drive Date</label>
                <input class="form-control" v-model="editForm.drive_date" type="datetime-local" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Description</label>
                <textarea class="form-control" v-model="editForm.description" rows="4"></textarea>
              </div>
            </div>

            <div class="d-flex gap-2 justify-content-end mt-4 pt-3 border-top">
              <button class="btn btn-outline-secondary" @click="editMode = false">Cancel</button>
              <button class="btn btn-primary px-5" @click="saveEdit" :disabled="saving">
                <span v-if="saving" class="spinner-border spinner-border-sm me-2"></span>
                {{ saving ? 'Saving…' : 'Save Changes' }}
              </button>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script>
import { useCompanyStore } from '@/stores/companyStore'
import { useUserStore }    from '@/stores/userStore'

export default {
  name: 'DriveDetail',

  setup() {
    return { store: useCompanyStore(), userStore: useUserStore() }
  },

  data: () => ({
    editMode:  false,
    editForm:  {},
    loading:   false,
    saving:    false,
    toggling:  false,
  }),

  computed: {
    driveId() { return parseInt(this.$route.params.driveId) },

    drive() { return this.store.getDriveById(this.driveId) },

    appStats() {
      const s = this.store.getDriveStats(this.driveId)
      return [
        { label: 'Applied',     value: s.applied,     color: 'text-primary' },
        { label: 'Shortlisted', value: s.shortlisted, color: 'text-info'    },
        { label: 'Selected',    value: s.selected,    color: 'text-success' },
        { label: 'Rejected',    value: s.rejected,    color: 'text-danger'  },
      ]
    },

    salaryText() {
      if (!this.drive) return '—'
      const { salary_min, salary_max, currency } = this.drive
      const sym = currency === 'INR' ? '₹' : currency
      const fmt = v => v >= 100000 ? `${sym}${(v/100000).toFixed(1)}L` : `${sym}${v?.toLocaleString()}`
      if (salary_min && salary_max) return `${fmt(salary_min)}–${fmt(salary_max)}`
      if (salary_max) return `Up to ${fmt(salary_max)}`
      if (salary_min) return `From ${fmt(salary_min)}`
      return 'Not disclosed'
    },

    isUrgent() {
      if (!this.drive?.application_deadline) return false
      const diff = new Date(this.drive.application_deadline) - new Date()
      return diff > 0 && diff < 3 * 86400000
    },
  },

  async mounted() {
    this.loading = true
    await Promise.all([
      this.store.fetchDrives(this.userStore.companyId),
      this.store.fetchApplicants(this.userStore.companyId, this.driveId),
    ])
    this.loading = false
    this._initEditForm()
  },

  methods: {
    _initEditForm() {
      const d = this.drive
      if (!d) return
      const toLocal = iso => iso ? iso.slice(0, 16) : ''
      this.editForm = {
        title:                    d.title,
        job_type:                 d.job_type           || '',
        location:                 d.location           || '',
        description:              d.description        || '',
        currency:                 d.currency           || 'INR',
        salary_min:               d.salary_min         || null,
        salary_max:               d.salary_max         || null,
        min_cgpa:                 d.min_cgpa           || null,
        eligible_graduation_year: d.eligible_graduation_year || null,
        eligible_branches:        d.eligible_branches  || '',
        skills_required:          d.skills_required    || '',
        experience_required:      d.experience_required|| '',
        application_deadline:     toLocal(d.application_deadline),
        drive_date:               toLocal(d.drive_date),
      }
    },

    async saveEdit() {
      if (!this.editForm.title) { alert('Title is required'); return }
      this.saving = true
      try {
        const payload = { ...this.editForm }
        if (payload.application_deadline)
          payload.application_deadline = new Date(payload.application_deadline).toISOString()
        if (payload.drive_date)
          payload.drive_date = new Date(payload.drive_date).toISOString()
        Object.keys(payload).forEach(k => payload[k] === '' && delete payload[k])

        await this.store.updateDrive(this.userStore.companyId, this.driveId, payload)
        this.editMode = false
      } catch (e) {
        alert(e.message || 'Failed to save')
      } finally {
        this.saving = false
      }
    },

    async toggleStatus() {
      this.toggling = true
      try { await this.store.toggleDriveStatus(this.userStore.companyId, this.driveId) }
      catch (e) { alert(e.message) }
      finally { this.toggling = false }
    },

    async deleteDrive() {
      if (!confirm('Permanently delete this drive and all its applications?')) return
      try {
        await this.store.deleteDrive(this.userStore.companyId, this.driveId)
        this.$router.push(`/company/${this.userStore.companyId}`)
      } catch (e) { alert(e.message) }
    },

    formatDate(d) {
      return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit' }) : '—'
    },
  },
}
</script>

<style scoped>
.info-chip { background: #f8f9fa; border-radius: 8px; padding: .75rem 1rem; }
.section-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6c757d;
  padding-bottom: .5rem; border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
</style>