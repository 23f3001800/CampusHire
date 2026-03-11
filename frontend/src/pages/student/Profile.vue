<template>
  <div class="profile-page bg-light min-vh-100 py-4">
    <div class="container" style="max-width:860px">

      <!-- Header -->
      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Profile</h3>
          <small class="text-muted">Keep your profile updated to unlock more opportunities</small>
        </div>
        <router-link :to="`/student/${userStore.studentId}`" class="btn btn-outline-secondary btn-sm">
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
            <i class="bi fs-3" :class="store.isProfileComplete ? 'bi-check-circle-fill text-success' : 'bi-exclamation-triangle-fill text-warning'"></i>
          </div>
        </div>
      </div>

      <!-- Alert -->
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

          <!-- ── PERSONAL ── -->
          <div v-show="activeTab === 'personal'">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">Full Name</label>
                <input class="form-control" :value="form.name" disabled />
                <small class="text-muted">Change via account settings</small>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Roll Number</label>
                <input class="form-control" v-model="form.roll_number" placeholder="e.g. CS20001" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Phone <span class="text-danger">*</span></label>
                <input class="form-control" v-model="form.phone" type="tel" placeholder="+91 98765 43210" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Alternate Phone</label>
                <input class="form-control" v-model="form.alternate_phone" type="tel" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Gender <span class="text-danger">*</span></label>
                <select class="form-select" v-model="form.gender">
                  <option value="">Select gender</option>
                  <option>Male</option><option>Female</option><option>Other</option><option>Prefer not to say</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Date of Birth</label>
                <input class="form-control" v-model="form.date_of_birth" type="date" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Address</label>
                <input class="form-control" v-model="form.address" placeholder="Street address" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">City</label>
                <input class="form-control" v-model="form.city" placeholder="City" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">State</label>
                <input class="form-control" v-model="form.state" placeholder="State" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">Pincode</label>
                <input class="form-control" v-model="form.pincode" placeholder="400001" maxlength="6" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Bio</label>
                <textarea class="form-control" v-model="form.bio" rows="3"
                  placeholder="A short bio about yourself…" maxlength="500"></textarea>
                <small class="text-muted">{{ (form.bio || '').length }}/500</small>
              </div>
            </div>
          </div>

          <!-- ── EDUCATION ── -->
          <div v-show="activeTab === 'education'">
            <div class="row g-3">
              <div class="col-md-6">
                <label class="form-label fw-semibold">College / University</label>
                <input class="form-control" v-model="form.college_name" placeholder="IIT Bombay" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Degree</label>
                <input class="form-control" v-model="form.degree" placeholder="B.Tech" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Branch <span class="text-danger">*</span></label>
                <select class="form-select" v-model="form.branch">
                  <option value="">Select branch</option>
                  <option value="CSE">Computer Science & Engineering</option>
                  <option value="ECE">Electronics & Communication</option>
                  <option value="ME">Mechanical Engineering</option>
                  <option value="Civil">Civil Engineering</option>
                  <option value="EE">Electrical Engineering</option>
                  <option value="IT">Information Technology</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Graduation Year <span class="text-danger">*</span></label>
                <input class="form-control" v-model.number="form.graduation_year" type="number"
                  placeholder="2025" min="2020" max="2030" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">CGPA</label>
                <input class="form-control" v-model.number="form.cgpa" type="number"
                  step="0.01" min="0" max="10" placeholder="8.50" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">10th %</label>
                <input class="form-control" v-model.number="form.tenth_percentage" type="number"
                  step="0.01" min="0" max="100" placeholder="92.5" />
              </div>
              <div class="col-md-4">
                <label class="form-label fw-semibold">12th %</label>
                <input class="form-control" v-model.number="form.twelfth_percentage" type="number"
                  step="0.01" min="0" max="100" placeholder="89.0" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold">Current Semester</label>
                <select class="form-select" v-model.number="form.current_semester">
                  <option value="">Select</option>
                  <option v-for="n in 8" :key="n" :value="n">Semester {{ n }}</option>
                </select>
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">Skills</label>
                <input class="form-control" v-model="form.skills"
                  placeholder="Python, Django, SQL, React (comma-separated)" />
                <small class="text-muted">Separate skills with commas</small>
              </div>
            </div>
          </div>

          <!-- ── SOCIAL ── -->
          <div v-show="activeTab === 'social'">
            <div class="row g-3">
              <div class="col-12">
                <label class="form-label fw-semibold">
                  <i class="bi bi-linkedin text-primary me-1"></i>LinkedIn URL
                </label>
                <input class="form-control" v-model="form.linkedin_url"
                  placeholder="https://linkedin.com/in/yourname" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">
                  <i class="bi bi-github me-1"></i>GitHub URL
                </label>
                <input class="form-control" v-model="form.github_url"
                  placeholder="https://github.com/yourname" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">
                  <i class="bi bi-globe me-1"></i>Portfolio URL
                </label>
                <input class="form-control" v-model="form.portfolio_url"
                  placeholder="https://yourportfolio.com" />
              </div>
              <div class="col-12">
                <label class="form-label fw-semibold">
                  <i class="bi bi-code-slash me-1"></i>Coding Profile URL
                </label>
                <input class="form-control" v-model="form.coding_profile_url"
                  placeholder="https://leetcode.com/yourname" />
              </div>
            </div>
          </div>

          <!-- ── RESUME ── -->
          <div v-show="activeTab === 'resume'">
            <!-- Current resume -->
            <div v-if="store.hasResume" class="resume-card p-4 rounded-3 mb-4 d-flex align-items-center gap-3">
              <div class="resume-icon">
                <i class="bi bi-file-earmark-pdf-fill fs-1 text-danger"></i>
              </div>
              <div class="flex-grow-1">
                <p class="fw-bold mb-1">{{ store.profile?.resume_filename }}</p>
                <small class="text-muted">Current resume on file</small>
              </div>
              <div class="d-flex gap-2">
                <button 
                    class="btn btn-outline-primary btn-sm"
                    @click="viewResume(store.profile?.resume_filename)"
                    :disabled="!store.profile?.resume_link"
                  >
                    <i class="bi bi-eye me-1"></i>View
                </button>
                <button class="btn btn-outline-danger btn-sm" @click="removeResume" :disabled="resumeLoading">
                  <i class="bi bi-trash me-1"></i>Remove
                </button>
              </div>
            </div>

            <!-- Upload zone -->
            <div class="upload-zone rounded-3 p-5 text-center"
              :class="{ 'drag-over': isDragOver }"
              @dragover.prevent="isDragOver = true"
              @dragleave="isDragOver = false"
              @drop.prevent="handleDrop">
              <i class="bi bi-cloud-upload fs-1 text-muted mb-3 d-block"></i>
              <p class="fw-semibold mb-1">Drag & drop your resume here</p>
              <p class="text-muted small mb-3">PDF, DOC or DOCX — max 5MB</p>
              <label class="btn btn-primary" :class="{ disabled: resumeLoading }">
                <span v-if="resumeLoading" class="spinner-border spinner-border-sm me-2"></span>
                <i v-else class="bi bi-upload me-2"></i>
                {{ resumeLoading ? 'Uploading…' : 'Browse File' }}
                <input type="file" class="d-none" accept=".pdf,.doc,.docx"
                  @change="handleFileSelect" :disabled="resumeLoading" />
              </label>
            </div>
          </div>

          <!-- Save button (not shown on resume tab) -->
          <div v-if="activeTab !== 'resume'" class="d-flex justify-content-end mt-4 pt-3 border-top">
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
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

export default {
  name: 'StudentProfile',
  setup() {
    return {
      store:     useStudentStore(),
      userStore: useUserStore(),
    }
  },
  data: () => ({
    activeTab:    'personal',
    form:         {},
    offerBusy:   {},
    successMsg:   '',
    errorMsg:     '',
    resumeLoading: false,
    isDragOver:   false,
  }),
  computed: {
    tabs: () => [
      { key: 'personal',  label: 'Personal',  icon: 'bi-person' },
      { key: 'education', label: 'Education', icon: 'bi-mortarboard' },
      { key: 'social',    label: 'Social',    icon: 'bi-share' },
      { key: 'resume',    label: 'Resume',    icon: 'bi-file-earmark-text' },
    ],
  },
  async mounted() {
    await this.store.fetchProfile(this.userStore.studentId)
    this._resetForm()
  },
  methods: {
    _resetForm() {
      const p = this.store.profile || {}
      this.form = {
        name:               p.name            || '',
        roll_number:        p.roll_number      || '',
        phone:              p.phone            || '',
        alternate_phone:    p.alternate_phone  || '',
        gender:             p.gender           || '',
        date_of_birth:      p.date_of_birth    || '',
        address:            p.address          || '',
        city:               p.city             || '',
        state:              p.state            || '',
        pincode:            p.pincode          || '',
        bio:                p.bio              || '',
        college_name:       p.college_name     || '',
        degree:             p.degree           || '',
        branch:             p.branch           || '',
        graduation_year:    p.graduation_year  || '',
        cgpa:               p.cgpa             || '',
        tenth_percentage:   p.tenth_percentage || '',
        twelfth_percentage: p.twelfth_percentage || '',
        current_semester:   p.current_semester || '',
        skills:             p.skills           || '',
        linkedin_url:       p.linkedin_url     || '',
        github_url:         p.github_url       || '',
        portfolio_url:      p.portfolio_url    || '',
        coding_profile_url: p.coding_profile_url || '',
      }
    },

    async save() {
      this.successMsg = ''
      this.errorMsg   = ''
      // Strip empty strings so we don't overwrite with blanks
      const payload = Object.fromEntries(
        Object.entries(this.form).filter(([, v]) => v !== '' && v !== null)
      )
      try {
        await this.store.updateProfile(this.userStore.studentId, payload)
        this.successMsg = 'Profile saved successfully!'
        window.scrollTo({ top: 0, behavior: 'smooth' })
      } catch (e) {
        this.errorMsg = e.message || 'Failed to save profile'
      }
    },

    async handleFileSelect(e) {
      const file = e.target.files[0]
      if (file) await this._upload(file)
    },

    handleDrop(e) {
      this.isDragOver = false
      const file = e.dataTransfer.files[0]
      if (file) this._upload(file)
    },
    async viewResume(filename) {
        this.offerBusy = true  // ✅ no .value
        try {
          const blob = await this.store.fetchresume(filename)
          if (blob) window.open(URL.createObjectURL(blob), '_blank')
        } catch (e) {
          showToast('danger', e?.message ?? 'Failed to load resume.')
        } finally {
          this.offerBusy = false // ✅ correct
        }
      },

    async _upload(file) {
      const ALLOWED = ['application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
      if (!ALLOWED.includes(file.type)) {
        this.errorMsg = 'Only PDF, DOC or DOCX files allowed'; return
      }
      if (file.size > 5 * 1024 * 1024) {
        this.errorMsg = 'File must be under 5MB'; return
      }
      this.resumeLoading = true
      this.errorMsg = ''
      try {
        await this.store.uploadResume(this.userStore.studentId, file)
        this.successMsg = 'Resume uploaded successfully!'
      } catch (e) {
        this.errorMsg = e.message || 'Upload failed'
      } finally {
        this.resumeLoading = false
      }
    },

    async removeResume() {
      if (!confirm('Remove your current resume?')) return
      this.resumeLoading = true
      try {
        await this.store.deleteResume(this.userStore.studentId)
        this.successMsg = 'Resume removed'
      } catch (e) {
        this.errorMsg = e.message
      } finally {
        this.resumeLoading = false
      }
    },
  },
}
</script>

<style scoped>
.nav-tabs .nav-link         { color: #6c757d; border: none; border-bottom: 3px solid transparent; }
.nav-tabs .nav-link.active  { color: #0d6efd; border-bottom-color: #0d6efd; background: none; font-weight: 600; }
.nav-tabs .nav-link:hover   { color: #0d6efd; }

.upload-zone {
  border: 2px dashed #dee2e6;
  background: #f8f9fa;
  cursor: pointer;
  transition: border-color .2s, background .2s;
}
.upload-zone.drag-over {
  border-color: #0d6efd;
  background: #e7f1ff;
}
.resume-card {
  background: #f8f9fa;
  border: 1px solid #dee2e6;
}
</style>