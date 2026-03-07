<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:1100px">

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3">Loading applicants…</p>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger" style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3" @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else>

        <!-- Header -->
        <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
          <div>
            <button class="btn btn-outline-secondary btn-sm mb-1" @click="router.back()">
              <i class="bi bi-arrow-left me-1"></i>Back to Drive
            </button>
            <h4 class="fw-bold mb-0">Applicants — {{ drive?.title || '…' }}</h4>
            <small class="text-muted">
              <i class="bi bi-building me-1"></i>{{ store.companyName }}
            </small>
          </div>
          <button class="btn btn-outline-secondary btn-sm"
                  :disabled="store.loadingApps"
                  @click="loadApplicants(true)">
            <span v-if="store.loadingApps" class="spinner-border spinner-border-sm"></span>
            <i v-else class="bi bi-arrow-clockwise"></i>
            Refresh
          </button>
        </div>

        <!-- Pipeline stat chips — clickable to filter -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3" v-for="s in pipelineStats" :key="s.key">
            <div class="card border-0 shadow-sm text-center py-3 h-100 cursor-pointer"
                 :class="activeFilter === s.key ? 'border-primary border-2' : ''"
                 @click="setFilter(s.key)">
              <div class="fw-bold fs-3 lh-1" :class="s.color">{{ s.value }}</div>
              <small class="text-muted mt-1">{{ s.label }}</small>
            </div>
          </div>
        </div>

        <!-- Filters -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body py-3">
            <div class="row g-2 align-items-center">
              <div class="col-md-5">
                <div class="input-group input-group-sm">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input class="form-control" v-model="search"
                         placeholder="Search by name, email, branch…" />
                  <button v-if="search" class="btn btn-outline-secondary" @click="search = ''">
                    <i class="bi bi-x"></i>
                  </button>
                </div>
              </div>
              <div class="col-md-3">
                <select class="form-select form-select-sm" v-model="activeFilter">
                  <option value="">All Statuses</option>
                  <option>Applied</option>
                  <option>Shortlisted</option>
                  <option>Selected</option>
                  <option>Rejected</option>
                </select>
              </div>
              <div class="col-md-3">
                <select class="form-select form-select-sm" v-model="sortBy">
                  <option value="applied_date_desc">Newest First</option>
                  <option value="applied_date_asc">Oldest First</option>
                  <option value="cgpa_desc">CGPA High → Low</option>
                  <option value="name_asc">Name A–Z</option>
                </select>
              </div>
              <div class="col-md-1 text-end">
                <small class="text-muted">{{ filtered.length }}</small>
              </div>
            </div>
          </div>
        </div>

        <!-- Table -->
        <div class="card border-0 shadow-sm">
          <div class="card-body p-0">

            <div v-if="store.loadingApps" class="text-center py-4">
              <div class="spinner-border spinner-border-sm text-primary"></div>
            </div>

            <div v-else-if="!filtered.length" class="text-center py-5 text-muted">
              <i class="bi bi-people fs-1 d-block mb-2"></i>
              {{ search || activeFilter ? 'No applicants match your filters.' : 'No applicants yet.' }}
            </div>

            <div v-else class="table-responsive">
              <table class="table table-hover mb-0 align-middle">
                <thead class="table-light">
                  <tr>
                    <th>Applicant</th>
                    <th>Branch / CGPA</th>
                    <th>Applied</th>
                    <th>Status</th>
                    <th>Interview</th>
                    <th class="text-end">Action</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="app in filtered" :key="app.id">

                    <!-- Applicant info -->
                    <td>
                      <div class="d-flex align-items-center gap-2">
                        <i class="bi bi-person-circle fs-3 text-primary"></i>
                        <div>
                          <div class="fw-semibold">{{ app.student_name }}</div>
                          <div class="small text-muted">{{ app.student_email }}</div>
                          <div v-if="app.student_roll" class="small text-muted">
                            {{ app.student_roll }}
                          </div>
                        </div>
                      </div>
                    </td>

                    <!-- Branch / CGPA -->
                    <td>
                      <span class="badge bg-light text-dark">{{ app.student_branch || '—' }}</span>
                      <div class="small text-muted mt-1">CGPA: {{ app.student_cgpa ?? '—' }}</div>
                    </td>

                    <!-- Applied date -->
                    <td class="small">{{ formatDate(app.applied_date) }}</td>

                    <!-- Status -->
                    <td>
                      <span class="badge" :class="statusBadge(app.status)">{{ app.status }}</span>
                      <div v-if="app.reviewed_date" class="small text-muted mt-1">
                        {{ formatDate(app.reviewed_date) }}
                      </div>
                    </td>

                    <!-- Interview -->
                    <td>
                      <span v-if="store.getInterviewForApp(app.id)"
                            class="badge bg-info text-dark">
                        <i class="bi bi-calendar-check me-1"></i>Scheduled
                      </span>
                      <span v-else class="text-muted small">—</span>
                    </td>

                    <!-- Single action: open full profile where all actions live -->
                    <td class="text-end">
                      <router-link
                        :to="{
                          path:  `/company/students/${app.student_id}`,
                          query: { driveId: driveId, applicationId: app.id }
                        }"
                        class="btn btn-sm btn-primary">
                        <i class="bi bi-person-lines-fill me-1"></i>Review
                      </router-link>
                    </td>

                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute }  from 'vue-router'
import { useCompanyStore }      from '@/stores/companyStore'
import { useUserStore }         from '@/stores/userStore'

const router    = useRouter()
const route     = useRoute()
const store     = useCompanyStore()
const userStore = useUserStore()

const driveId = computed(() => parseInt(route.params.driveId))
const cid     = computed(() => userStore.companyId)

const loading      = ref(true)
const error        = ref('')
const drive        = ref(null)
const search       = ref('')
const activeFilter = ref('')
const sortBy       = ref('applied_date_desc')

const filtered = computed(() => {
  let list = [...(store.applicants[driveId.value] || [])]
  if (activeFilter.value) list = list.filter(a => a.status === activeFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.student_name?.toLowerCase().includes(q)   ||
      a.student_email?.toLowerCase().includes(q)  ||
      a.student_branch?.toLowerCase().includes(q) ||
      a.student_roll?.toLowerCase().includes(q)
    )
  }
  const sorters = {
    applied_date_desc: (a, b) => new Date(b.applied_date) - new Date(a.applied_date),
    applied_date_asc:  (a, b) => new Date(a.applied_date) - new Date(b.applied_date),
    cgpa_desc:  (a, b) => (b.student_cgpa ?? 0) - (a.student_cgpa ?? 0),
    name_asc:   (a, b) => (a.student_name ?? '').localeCompare(b.student_name ?? ''),
  }
  if (sorters[sortBy.value]) list.sort(sorters[sortBy.value])
  return list
})

const pipelineStats = computed(() => {
  const all    = store.applicants[driveId.value] || []
  const count  = s => all.filter(a => a.status === s).length
  return [
    { key: '',            label: 'Total',       value: all.length,           color: 'text-dark'    },
    { key: 'Applied',     label: 'Applied',     value: count('Applied'),     color: 'text-primary' },
    { key: 'Shortlisted', label: 'Shortlisted', value: count('Shortlisted'), color: 'text-info'    },
    { key: 'Selected',    label: 'Selected',    value: count('Selected'),    color: 'text-success' },
  ]
})

async function loadApplicants(force = false) {
  loading.value = true
  error.value   = ''
  try {
    await store.fetchDrives(cid.value)
    drive.value = store.getDriveById(driveId.value)
    await store.fetchApplicants(cid.value, driveId.value, force)
  } catch (e) {
    error.value = e?.message ?? 'Failed to load applicants.'
  } finally {
    loading.value = false
  }
}

function setFilter(key) {
  activeFilter.value = activeFilter.value === key ? '' : key
}

function formatDate(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    : '—'
}

function statusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}

onMounted(() => loadApplicants())
</script>

<style scoped>
.cursor-pointer { cursor: pointer; }
.table th {
  font-size: .78rem; text-transform: uppercase;
  letter-spacing: .04em; color: #6c757d; white-space: nowrap;
}
</style>