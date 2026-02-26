<template>
  <div class="dashboard bg-light min-vh-100">

    <!-- Loading profile -->
    <div v-if="store.loadingProfile"
         class="d-flex justify-content-center align-items-center"
         style="min-height:60vh">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3"></div>
        <p class="text-muted">Loading company profile…</p>
      </div>
    </div>

    <!-- Profile incomplete -->
    <div v-else-if="!store.isProfileComplete" class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card shadow-sm border-warning">
            <div class="card-body text-center p-5">
              <i class="bi bi-exclamation-triangle-fill
                        text-warning fs-1 mb-3"></i>
              <h4>Complete Your Company Profile</h4>
              <p class="text-muted mb-3">
                {{ store.profileCompletionDetails.percentage }}%
                complete — finish your profile to start posting drives.
              </p>
              <div class="progress mb-4" style="height:10px">
                <div class="progress-bar"
                     :class="progressClass(
                       store.profileCompletionDetails.percentage
                     )"
                     :style="{
                       width: store.profileCompletionDetails.percentage
                              + '%'
                     }">
                </div>
              </div>
              <div v-if="store.missingFieldsWithLabels.required.length"
                   class="text-start mb-4">
                <h6 class="text-danger fw-semibold">
                  <i class="bi bi-x-circle me-2"></i>Required:
                </h6>
                <ul class="list-unstyled ms-3">
                  <li v-for="f in store.missingFieldsWithLabels.required"
                      :key="f.key" class="small py-1">
                    <i class="bi bi-arrow-right me-2
                               text-muted"></i>{{ f.label }}
                  </li>
                </ul>
              </div>
              <router-link to="/company/profile"
                           class="btn btn-primary btn-lg">
                <i class="bi bi-pencil me-2"></i>Complete Profile
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Pending / Rejected approval -->
    <div v-else-if="!store.isApproved" class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-7">
          <div class="card shadow-sm"
               :class="store.approvalStatus === 'Rejected'
                 ? 'border-danger' : 'border-info'">
            <div class="card-body text-center p-5">
              <i class="fs-1 mb-3"
                 :class="store.approvalStatus === 'Rejected'
                   ? 'bi bi-x-circle-fill text-danger'
                   : 'bi bi-clock-history text-info'"></i>
              <h4>
                {{ store.approvalStatus === 'Rejected'
                    ? 'Profile Rejected'
                    : 'Profile Under Review' }}
              </h4>
              <p class="text-muted mb-4">
                {{ store.approvalStatus === 'Rejected'
                    ? 'Your profile was rejected. Update your details and contact admin.'
                    : 'Your company profile is being reviewed by our admin team.' }}
              </p>
              <div class="alert"
                   :class="store.approvalStatus === 'Rejected'
                     ? 'alert-danger' : 'alert-info'">
                <strong>Status:</strong>
                <span class="badge ms-2"
                      :class="store.approvalStatus === 'Rejected'
                        ? 'bg-danger' : 'bg-warning text-dark'">
                  {{ store.approvalStatus }}
                </span>
              </div>
              <div class="d-flex justify-content-center gap-2">
                <router-link to="/company/profile"
                             class="btn btn-outline-primary">
                  <i class="bi bi-pencil me-1"></i>Edit Profile
                </router-link>
                <button class="btn btn-outline-secondary"
                        :disabled="store.loadingProfile"
                        @click="refresh">
                  <span v-if="store.loadingProfile"
                        class="spinner-border spinner-border-sm
                               me-1"></span>
                  <i v-else class="bi bi-arrow-clockwise me-1"></i>
                  Refresh
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Main dashboard (approved) ── -->
    <div v-else class="container py-4">

      <!-- Header -->
      <div class="d-flex justify-content-between
                  align-items-center mb-4 flex-wrap gap-2">
        <div class="d-flex align-items-center gap-3">
          <img v-if="store.logoUrl"
               :src="store.logoUrl"
               class="rounded-3 border"
               style="width:52px;height:52px;object-fit:cover" />
          <div v-else class="company-avatar-sm">
            {{ initials(store.companyName) }}
          </div>
          <div>
            <h3 class="fw-bold mb-0">{{ store.companyName }}</h3>
            <p class="text-muted mb-0 small">
              <i class="bi bi-check-circle-fill
                        text-success me-1"></i>Verified Company
            </p>
          </div>
        </div>
        <div class="d-flex gap-2">
          <router-link to="/company/profile"
                       class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-building me-1"></i>Profile
          </router-link>
          <router-link to="/company/create-drive"
                       class="btn btn-success">
            <i class="bi bi-plus-circle me-2"></i>New Drive
          </router-link>
        </div>
      </div>

      <!-- Pending drives warning -->
      <div v-if="store.pendingDrives.length"
           class="alert alert-warning d-flex align-items-center
                  gap-2 mb-4">
        <i class="bi bi-clock-history flex-shrink-0"></i>
        <span>
          <strong>{{ store.pendingDrives.length }}</strong>
          drive{{ store.pendingDrives.length > 1 ? 's' : '' }}
          awaiting admin approval.
        </span>
      </div>

      <!-- KPI stat cards -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"
             v-for="s in stats" :key="s.label">
          <div class="stat-card text-white" :class="s.bg">
            <i :class="`bi ${s.icon} fs-2 opacity-75`"></i>
            <div>
              <h3 class="mb-0 fw-bold">{{ s.value }}</h3>
              <small>{{ s.label }}</small>
            </div>
          </div>
        </div>
      </div>

      <!-- Drive tabs -->
      <ul class="nav nav-tabs mb-4">
        <li class="nav-item" v-for="t in tabs" :key="t.key">
          <a class="nav-link"
             :class="{ active: activeTab === t.key }"
             @click.prevent="activeTab = t.key" href="#">
            {{ t.label }}
            <span class="badge ms-1"
                  :class="activeTab === t.key
                    ? 'bg-primary' : 'bg-secondary'">
              {{ t.count }}
            </span>
          </a>
        </li>
      </ul>

      <!-- Loading drives -->
      <div v-if="store.loadingDrives" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- Empty state -->
      <div v-else-if="!displayedDrives.length"
           class="text-center py-5">
        <i class="bi bi-inbox fs-1 text-muted"></i>
        <p class="mt-2 text-muted">
          {{
            activeTab === 'active'
              ? 'No open drives. Create one to start accepting applications.'
              : 'No drives in this category.'
          }}
        </p>
        <router-link v-if="activeTab === 'active'"
                     to="/company/create-drive"
                     class="btn btn-primary mt-2">
          <i class="bi bi-plus-circle me-2"></i>Create Drive
        </router-link>
      </div>

      <!-- Drive cards -->
      <div v-else class="row g-4">
        <div class="col-lg-6"
             v-for="drive in displayedDrives" :key="drive.id">
          <div class="card drive-card shadow-sm h-100 border-0">
            <div class="card-body">

              <!-- Drive header -->
              <div class="d-flex justify-content-between mb-2">
                <div class="flex-grow-1 me-2">
                  <h5 class="mb-1 text-truncate">{{ drive.title }}</h5>
                  <p class="text-muted mb-0 small">
                    <i class="bi bi-geo-alt me-1"></i>
                    {{ drive.location || 'Location not set' }}
                  </p>
                </div>
                <div class="d-flex flex-column align-items-end gap-1">
                  <span class="badge"
                        :class="statusBadge(drive.status)">
                    {{ drive.status }}
                  </span>
                  <span v-if="drive.admin_approval_status !== 'Approved'"
                        class="badge"
                        :class="approvalBadge(
                          drive.admin_approval_status
                        )">
                    {{ drive.admin_approval_status || 'Pending' }}
                  </span>
                </div>
              </div>

              <!-- Drive details grid -->
              <div class="row g-2 bg-light rounded p-2 mb-3 small">
                <div class="col-6">
                  <span class="text-muted d-block">Type</span>
                  <strong>{{ drive.job_type || '—' }}</strong>
                </div>
                <div class="col-6">
                  <span class="text-muted d-block">Deadline</span>
                  <strong :class="{
                    'text-danger': isUrgent(drive.application_deadline)
                  }">
                    {{ formatDate(drive.application_deadline) }}
                  </strong>
                </div>
                <div class="col-6">
                  <span class="text-muted d-block">Salary</span>
                  <strong>{{ salaryText(drive) }}</strong>
                </div>
                <div class="col-6">
                  <span class="text-muted d-block">Applicants</span>
                  <strong>{{ drive.total_applications ?? 0 }}</strong>
                </div>
              </div>

              <!-- Pipeline badges (from applicant cache if loaded) -->
              <div v-if="hasPipelineData(drive.id)"
                   class="d-flex flex-wrap gap-1 mb-3">
                <template v-for="(v, k) in store.getDriveStats(drive.id)"
                          :key="k">
                  <span v-if="k !== 'total' && v > 0"
                        class="badge" :class="statusBadge(k)">
                    {{ v }} {{ k }}
                  </span>
                </template>
              </div>

              <!-- Actions -->
              <div class="d-flex gap-2">
                <router-link :to="`/company/drives/${drive.id}`"
                             class="btn btn-outline-primary
                                    btn-sm flex-grow-1">
                  <i class="bi bi-eye me-1"></i>Details
                </router-link>
                <router-link
                  v-if="(drive.total_applications ?? 0) > 0"
                  :to="`/company/drives/${drive.id}/applicants`"
                  class="btn btn-primary btn-sm">
                  <i class="bi bi-people me-1"></i>
                  {{ drive.total_applications }}
                </router-link>
                <button class="btn btn-outline-secondary btn-sm"
                        :disabled="toggling === drive.id"
                        :title="drive.status === 'Open'
                          ? 'Close drive' : 'Reopen drive'"
                        @click="toggleStatus(drive.id)">
                  <span v-if="toggling === drive.id"
                        class="spinner-border
                               spinner-border-sm"></span>
                  <i v-else class="bi"
                     :class="drive.status === 'Open'
                       ? 'bi-toggle-on text-success'
                       : 'bi-toggle-off text-secondary'"></i>
                </button>
              </div>

            </div>
          </div>
        </div>
      </div>

      <!-- Recent applicants table -->
      <div v-if="store.recentApplicants.length" class="mt-5">
        <div class="d-flex justify-content-between
                    align-items-center mb-3">
          <h5 class="fw-bold mb-0">Recent Applicants</h5>
          <small class="text-muted">
            Last {{ store.recentApplicants.length }} across all drives
          </small>
        </div>
        <div class="card shadow-sm border-0">
          <div class="table-responsive">
            <table class="table table-hover mb-0 align-middle">
              <thead class="table-light">
                <tr>
                  <th>Applicant</th>
                  <th>Drive</th>
                  <th>Applied</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in store.recentApplicants" :key="a.id">
                  <td>
                    <strong>{{ a.student_name }}</strong>
                    <div class="small text-muted">
                      {{ a.student_email }}
                    </div>
                  </td>
                  <td class="small">{{ a.drive_title }}</td>
                  <td class="small">
                    {{ formatDate(a.applied_date) }}
                  </td>
                  <td>
                    <span class="badge"
                          :class="statusBadge(a.status)">
                      {{ a.status }}
                    </span>
                  </td>
                  <td>
                    <router-link
                      :to="`/company/drives/${a.drive_id}/applicants`"
                      class="btn btn-sm btn-outline-primary">
                      View
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
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
  name: 'CompanyDashboard',

  setup() {
    return {
      store:     useCompanyStore(),
      userStore: useUserStore(),
    }
  },

  data: () => ({
    activeTab: 'active',
    toggling:  null,   // driveId currently being toggled
  }),

  computed: {
    tabs() {
      const s = this.store
      return [
        { key: 'active',    label: 'Active',    count: s.activeDrives.length    },
        { key: 'all',       label: 'All',       count: s.drives.length          },
        { key: 'closed',    label: 'Closed',    count: s.closedDrives.length    },
        { key: 'completed', label: 'Completed', count: s.completedDrives.length },
      ]
    },
    displayedDrives() {
      const map = {
        active:    this.store.activeDrives,
        all:       this.store.drives,
        closed:    this.store.closedDrives,
        completed: this.store.completedDrives,
      }
      return map[this.activeTab] || []
    },
    stats() {
      const s = this.store
      return [
        {
          label: 'Total Drives', value: s.drives.length,
          bg: 'bg-primary', icon: 'bi-briefcase-fill',
        },
        {
          label: 'Active Drives', value: s.activeDrives.length,
          bg: 'bg-success', icon: 'bi-check-circle-fill',
        },
        {
          label: 'Total Applicants', value: s.totalApplicants,
          bg: 'bg-info', icon: 'bi-people-fill',
        },
        {
          label: 'Completed', value: s.completedDrives.length,
          bg: 'bg-warning', icon: 'bi-trophy-fill',
        },
      ]
    },
  },

  async mounted() {
    const cid = this.userStore.companyId
    await this.store.fetchProfile(cid)
    if (this.store.isApproved) {
      await this.store.fetchDrives(cid)
    }
  },

  methods: {
    async refresh() {
      await this.store.fetchProfile(this.userStore.companyId, true)
    },

    async toggleStatus(driveId) {
      this.toggling = driveId
      try {
        await this.store.toggleDriveStatus(
          this.userStore.companyId, driveId
        )
      } catch (e) {
        alert(e?.message ?? 'Failed to update status.')
      } finally {
        this.toggling = null
      }
    },

    hasPipelineData(driveId) {
      return !!this.store.applicants[driveId]
    },

    formatDate(d) {
      if (!d) return 'N/A'
      return new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    },

    isUrgent(deadline) {
      if (!deadline) return false
      const diff = new Date(deadline) - new Date()
      return diff > 0 && diff < 3 * 86_400_000
    },

    salaryText(drive) {
      if (!drive.salary_min && !drive.salary_max) return '—'
      const sym = drive.currency === 'INR' ? '₹' : (drive.currency || '')
      const fmt = v => v >= 100000
        ? `${sym}${(v / 100000).toFixed(1)}L`
        : `${sym}${v?.toLocaleString('en-IN')}`
      if (drive.salary_min && drive.salary_max)
        return `${fmt(drive.salary_min)}–${fmt(drive.salary_max)}`
      return fmt(drive.salary_min || drive.salary_max)
    },

    progressClass(p) {
      return p < 30 ? 'bg-danger' : p < 70 ? 'bg-warning' : 'bg-success'
    },

    initials(name) {
      return (name || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },

    statusBadge(s) {
      return {
        Open: 'bg-success', Closed: 'bg-secondary',
        Completed: 'bg-primary',
        Applied: 'bg-primary', Shortlisted: 'bg-info',
        Selected: 'bg-success', Rejected: 'bg-danger',
        applied: 'bg-primary', shortlisted: 'bg-info',
        selected: 'bg-success', rejected: 'bg-danger',
      }[s] ?? 'bg-secondary'
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
.company-avatar-sm {
  width: 52px; height: 52px; border-radius: 10px;
  background: linear-gradient(135deg, #0d6efd, #0a58ca);
  color: #fff; display: flex; align-items: center;
  justify-content: center;
  font-size: 1.2rem; font-weight: 700; flex-shrink: 0;
}
.stat-card {
  padding: 1.2rem 1.5rem; border-radius: 12px;
  display: flex; align-items: center; gap: 1rem;
  box-shadow: 0 2px 8px rgba(0,0,0,.1);
}
.drive-card {
  border-left: 4px solid #0d6efd !important;
  transition: transform .2s;
}
.drive-card:hover { transform: translateY(-3px); }
.nav-tabs .nav-link {
  color: #6c757d; border: none;
  border-bottom: 2px solid transparent;
}
.nav-tabs .nav-link.active {
  color: #0d6efd; border-bottom-color: #0d6efd; background: none;
}
</style>
