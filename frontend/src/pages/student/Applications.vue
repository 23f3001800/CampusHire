<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center
                  justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Applications</h3>
          <small class="text-muted">
            Track the status of all your drive applications
          </small>
        </div>
        <div class="d-flex gap-2">
          <!-- CSV Export -->
          <div>
            <button v-if="!store.csvExport.status"
                    class="btn btn-success btn-sm"
                    :disabled="!store.applications.length"
                    @click="startExport">
              <i class="bi bi-file-earmark-spreadsheet me-1"></i>
              Export CSV
            </button>
            <button v-else-if="store.csvExport.status === 'PENDING'"
                    class="btn btn-success btn-sm" disabled>
              <span class="spinner-border spinner-border-sm me-1"></span>
              Exporting…
            </button>
            <div v-else-if="store.csvExport.status === 'SUCCESS'"
                 class="d-flex gap-1">
              <a :href="`${apiBase}${store.csvExport.downloadUrl}`"
                 class="btn btn-success btn-sm" target="_blank">
                <i class="bi bi-download me-1"></i>Download
              </a>
              <button class="btn btn-outline-secondary btn-sm"
                      @click="store.resetCSVExport()">
                <i class="bi bi-arrow-repeat"></i>
              </button>
            </div>
            <button v-else-if="store.csvExport.status === 'FAILURE'"
                    class="btn btn-danger btn-sm"
                    @click="store.resetCSVExport()">
              <i class="bi bi-exclamation-circle me-1"></i>
              Failed — Retry
            </button>
          </div>

          <router-link :to="`/student/${userStore.studentId}`"
                       class="btn btn-outline-secondary btn-sm">
            <i class="bi bi-arrow-left me-1"></i>Dashboard
          </router-link>
        </div>
      </div>

      <!-- Stats strip -->
      <div class="row g-3 mb-4">
        <div class="col-6 col-md-3"
             v-for="s in statChips" :key="s.label">
          <div class="card border-0 shadow-sm text-center py-3">
            <div class="fw-bold fs-4" :class="s.color">
              {{ s.value }}
            </div>
            <small class="text-muted">{{ s.label }}</small>
          </div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card border-0 shadow-sm mb-4">
        <div class="card-body d-flex flex-wrap gap-2">
          <div class="input-group" style="max-width:280px">
            <span class="input-group-text bg-white">
              <i class="bi bi-search"></i>
            </span>
            <input v-model="search" type="text"
                   class="form-control border-start-0"
                   placeholder="Search company or drive…" />
          </div>
          <select v-model="statusFilter" class="form-select"
                  style="max-width:160px">
            <option value="">All Statuses</option>
            <option>Applied</option>
            <option>Shortlisted</option>
            <option>Selected</option>
            <option>Rejected</option>
          </select>
          <select v-model="sortBy" class="form-select"
                  style="max-width:160px">
            <option value="newest">Newest First</option>
            <option value="oldest">Oldest First</option>
          </select>
          <button v-if="search || statusFilter"
                  class="btn btn-outline-secondary btn-sm"
                  @click="search = ''; statusFilter = ''">
            <i class="bi bi-x me-1"></i>Clear
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div v-if="store.loadingApps" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <!-- Empty -->
      <div v-else-if="!filtered.length" class="text-center py-5">
        <i class="bi bi-inbox fs-1 text-muted d-block mb-2"></i>
        <p class="text-muted">
          {{ search || statusFilter
              ? 'No applications match your filters'
              : "You haven't applied to any drives yet" }}
        </p>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-primary mt-2">
          Browse Drives
        </router-link>
      </div>

      <!-- Cards -->
      <div v-else class="d-flex flex-column gap-3">
        <div v-for="app in filtered" :key="app.id"
             class="card border-0 shadow-sm app-card"
             :class="{
               'border-start border-4 border-success':
                 app.status === 'Selected',
               'border-start border-4 border-danger':
                 app.status === 'Rejected',
             }">
          <div class="card-body">

            <div class="d-flex justify-content-between
                        align-items-start flex-wrap gap-2">
              <div>
                <h5 class="fw-bold mb-1">{{ app.drive_title }}</h5>
                <p class="text-muted mb-0 small">
                  <i class="bi bi-building me-1"></i>
                  {{ app.company_name }}
                </p>
              </div>
              <span class="badge fs-6 px-3 py-2"
                    :class="statusClass(app.status)">
                <i class="bi me-1" :class="statusIcon(app.status)"></i>
                {{ app.status }}
              </span>
            </div>

            <div class="row g-2 mt-2 small text-muted">
              <div class="col-auto">
                <i class="bi bi-calendar-event me-1"></i>
                Applied {{ fmt(app.applied_date) }}
              </div>
              <div v-if="app.reviewed_date" class="col-auto">
                <i class="bi bi-eye me-1"></i>
                Reviewed {{ fmt(app.reviewed_date) }}
              </div>
            </div>

            <div v-if="app.notes"
                 class="alert alert-light border py-2 px-3
                        mt-3 mb-0 small">
              <strong>Recruiter note:</strong> {{ app.notes }}
            </div>

            <div class="d-flex justify-content-between
                        align-items-center mt-3">
              <div class="d-flex gap-2">
                <router-link
                  :to="`/student/drives/${app.drive_id}`"
                  class="btn btn-outline-secondary btn-sm">
                  <i class="bi bi-eye me-1"></i>View Drive
                </router-link>
                <router-link
                  v-if="app.status === 'Shortlisted' ||
                        app.status === 'Selected'"
                  :to="`/student/${userStore.studentId}/applications/${app.id}/interview`"
                  class="btn btn-outline-info btn-sm">
                  <i class="bi bi-camera-video me-1"></i>
                  Interview
                </router-link>
              </div>
              <button v-if="app.status === 'Applied'"
                      class="btn btn-outline-danger btn-sm"
                      :disabled="rowBusy[app.id]"
                      @click="withdraw(app.id)">
                <span v-if="rowBusy[app.id]"
                      class="spinner-border spinner-border-sm me-1"></span>
                <i v-else class="bi bi-x-circle me-1"></i>Withdraw
              </button>
            </div>

          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useStudentStore } from '@/stores/studentStore'
import { useUserStore }    from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

const apiBase      = import.meta.env.VITE_API_BASE_URL ?? ''
const search       = ref('')
const statusFilter = ref('')
const sortBy       = ref('newest')
const rowBusy      = reactive({})

const statChips = computed(() => {
  const s = store.applicationStats
  return [
    { label: 'Total',       value: s.total,       color: 'text-dark'    },
    { label: 'Shortlisted', value: s.shortlisted, color: 'text-info'    },
    { label: 'Selected',    value: s.selected,    color: 'text-success' },
    { label: 'Rejected',    value: s.rejected,    color: 'text-danger'  },
  ]
})

const filtered = computed(() => {
  let list = [...store.applications]
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.drive_title?.toLowerCase().includes(q) ||
      a.company_name?.toLowerCase().includes(q)
    )
  }
  if (statusFilter.value)
    list = list.filter(a => a.status === statusFilter.value)
  list.sort((a, b) => {
    const diff = new Date(b.applied_date) - new Date(a.applied_date)
    return sortBy.value === 'newest' ? diff : -diff
  })
  return list
})

onMounted(async () => {
  await Promise.all([
    store.fetchProfile(userStore.studentId),
    store.fetchApplications(userStore.studentId),
  ])
})

async function startExport() {
  try {
    await store.startCSVExport(userStore.studentId)
  } catch (e) {
    alert(e.message ?? 'Export failed')
  }
}

async function withdraw(appId) {
  if (!confirm('Withdraw this application?')) return
  rowBusy[appId] = true
  try {
    await store.withdrawApplication(userStore.studentId, appId)
  } catch (e) {
    alert(e?.message ?? 'Failed to withdraw')
  } finally {
    rowBusy[appId] = false
  }
}

function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : '—'
}
function statusClass(s) {
  return {
    Applied:     'bg-primary',
    Shortlisted: 'bg-info text-dark',
    Selected:    'bg-success',
    Rejected:    'bg-danger',
  }[s] ?? 'bg-secondary'
}
function statusIcon(s) {
  return {
    Applied:     'bi-send',
    Shortlisted: 'bi-star',
    Selected:    'bi-trophy',
    Rejected:    'bi-x-circle',
  }[s] ?? 'bi-circle'
}
</script>

<style scoped>
.app-card { transition: transform .15s; }
.app-card:hover { transform: translateY(-2px); }
</style>
