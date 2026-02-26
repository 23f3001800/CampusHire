<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:900px">

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="company">

        <div class="d-flex align-items-center mb-4">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back
          </button>
        </div>

        <!-- Header -->
        <div class="card border-0 shadow-sm mb-4">
          <div class="card-body p-4">
            <div class="d-flex align-items-center gap-4 flex-wrap">
              <div class="bg-primary bg-opacity-10 rounded-3
                          d-flex align-items-center justify-content-center
                          flex-shrink-0"
                   style="width:80px;height:80px">
                <!-- logo_url from company_fields marshal -->
                <img v-if="company.logo_url"
                     :src="company.logo_url"
                     :alt="company.company_name"
                     class="rounded-3"
                     style="width:80px;height:80px;object-fit:contain" />
                <i v-else class="bi bi-building text-primary"
                   style="font-size:2.5rem"></i>
              </div>
              <div class="flex-grow-1">
                <!-- company_name from company_fields marshal -->
                <h3 class="fw-bold mb-1">{{ company.company_name }}</h3>
                <p class="text-muted mb-2 small">
                  <!-- industry, location from company_fields marshal -->
                  <span v-if="company.industry">
                    <i class="bi bi-grid me-1"></i>{{ company.industry }}
                  </span>
                  <span v-if="company.location" class="ms-3">
                    <i class="bi bi-geo-alt me-1"></i>{{ company.location }}
                  </span>
                  <span v-if="company.company_size" class="ms-3">
                    <i class="bi bi-people me-1"></i>{{ company.company_size }}
                  </span>
                </p>
                <div class="d-flex gap-2 flex-wrap">
                  <span class="badge bg-success bg-opacity-10 text-success">
                    <i class="bi bi-patch-check me-1"></i>Verified
                  </span>
                  <!-- website from company_fields marshal -->
                  <a v-if="company.website"
                     :href="company.website" target="_blank"
                     class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-globe me-1"></i>Website
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="row g-4">
          <div class="col-md-8">

            <!-- description from company_fields marshal -->
            <div class="card border-0 shadow-sm mb-4">
              <div class="card-body p-4">
                <h6 class="section-label">About Company</h6>
                <p class="text-muted" style="white-space:pre-wrap">
                  {{ company.description || 'No description available.' }}
                </p>
              </div>
            </div>

            <!-- Open Drives -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-briefcase me-2 text-success"></i>
                  Open Drives ({{ openDrives.length }})
                </h6>
              </div>

              <div v-if="loadingDrives"
                   class="card-body text-center py-4">
                <div class="spinner-border spinner-border-sm
                            text-success"></div>
              </div>

              <div v-else-if="!openDrives.length"
                   class="card-body text-center text-muted small py-4">
                No open drives right now
              </div>

              <div v-else class="list-group list-group-flush">
                <router-link
                  v-for="d in openDrives" :key="d.id"
                  :to="`/student/drives/${d.id}`"
                  class="list-group-item list-group-item-action py-3">
                  <div class="d-flex justify-content-between
                              align-items-start">
                    <div>
                      <!-- title, job_type, location from drive_fields -->
                      <p class="fw-semibold mb-1">{{ d.title }}</p>
                      <p class="small text-muted mb-1">
                        <i class="bi bi-briefcase me-1"></i>
                        {{ d.job_type }}
                        <span v-if="d.location" class="ms-2">
                          <i class="bi bi-geo-alt me-1"></i>{{ d.location }}
                        </span>
                      </p>
                      <!-- salary_max from drive_fields -->
                      <p v-if="d.salary_max"
                         class="small text-success mb-0">
                        {{ formatSalary(d.salary_max) }}
                      </p>
                    </div>
                    <div class="text-end ms-3">
                      <span class="badge bg-success mb-1">Open</span>
                      <p class="small text-muted mb-1">
                        <i class="bi bi-clock me-1"></i>
                        {{ fmt(d.application_deadline) }}
                      </p>
                      <span v-if="store.hasApplied(d.id)"
                            class="badge bg-primary">Applied</span>
                    </div>
                  </div>
                </router-link>
              </div>

              <!-- Past drives -->
              <div v-if="pastDrives.length"
                   class="card-footer bg-white border-0">
                <button class="btn btn-link btn-sm text-muted p-0"
                        @click="showPast = !showPast">
                  <i class="bi me-1"
                     :class="showPast
                       ? 'bi-chevron-up' : 'bi-chevron-down'"></i>
                  {{ showPast ? 'Hide' : 'Show' }}
                  {{ pastDrives.length }} past drives
                </button>
                <div v-if="showPast" class="mt-2">
                  <div v-for="d in pastDrives" :key="d.id"
                       class="d-flex justify-content-between
                              align-items-center py-2
                              border-bottom small text-muted">
                    <span>{{ d.title }}</span>
                    <span class="badge bg-secondary">{{ d.status }}</span>
                  </div>
                </div>
              </div>
            </div>

          </div>

          <!-- Sidebar -->
          <div class="col-md-4 d-flex flex-column gap-3">
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <h6 class="section-label">At a Glance</h6>
                <div class="d-flex flex-column gap-3">
                  <div class="d-flex justify-content-between">
                    <small class="text-muted">Total Drives</small>
                    <strong>{{ drives.length }}</strong>
                  </div>
                  <div class="d-flex justify-content-between">
                    <small class="text-muted">Open Now</small>
                    <strong class="text-success">
                      {{ openDrives.length }}
                    </strong>
                  </div>
                  <!-- hr_contact from company_fields marshal -->
                  <div v-if="company.hr_contact">
                    <small class="text-muted d-block">HR Contact</small>
                    <a :href="`tel:${company.hr_contact}`"
                       class="small">
                      {{ company.hr_contact }}
                    </a>
                  </div>
                  <!-- hr_email from company_fields marshal -->
                  <div v-if="company.hr_email">
                    <small class="text-muted d-block">HR Email</small>
                    <a :href="`mailto:${company.hr_email}`"
                       class="small">
                      {{ company.hr_email }}
                    </a>
                  </div>
                </div>
              </div>
            </div>
          </div>

        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute }      from 'vue-router'
import { useStudentStore }          from '@/stores/studentStore'

const router       = useRouter()
const route        = useRoute()
const store        = useStudentStore()

const companyId   = parseInt(route.params.companyId)
const loading     = ref(true)
const loadingDrives = ref(false)
const error       = ref('')
const showPast    = ref(false)

// ── Read from store cache ─────────────────────────────────────────────────
const company = computed(() => store.companyCache[companyId] ?? null)
const drives  = computed(() => store.companyDriveCache[companyId] ?? [])

const openDrives = computed(() =>
  drives.value.filter(d => d.status === 'Open')
)
const pastDrives = computed(() =>
  drives.value.filter(d => d.status !== 'Open')
)

async function load() {
  loading.value = true
  error.value   = ''
  try {
    // store action → GET /company/:id
    await store.fetchCompanyProfile(companyId)
    if (!store.companyCache[companyId])
      error.value = 'Company not found.'
  } catch (e) {
    error.value = e?.message ?? 'Failed to load company.'
  } finally {
    loading.value = false
  }
}

async function loadDrives() {
  loadingDrives.value = true
  try {
    // store action → GET /company/:id/drives
    await store.fetchCompanyDrives(companyId)
  } finally {
    loadingDrives.value = false
  }
}

function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : 'N/A'
}
function formatSalary(s) {
  if (!s) return ''
  return s >= 100_000
    ? `₹${(s / 100_000).toFixed(1)} LPA`
    : `₹${s.toLocaleString('en-IN')}`
}

onMounted(async () => {
  await load()
  loadDrives()   // non-blocking
})
</script>

<style scoped>
.section-label {
  font-size: .7rem; font-weight: 700; text-transform: uppercase;
  letter-spacing: .08em; color: #6c757d;
  padding-bottom: .5rem; border-bottom: 1px solid #dee2e6;
  margin-bottom: 1rem;
}
</style>
