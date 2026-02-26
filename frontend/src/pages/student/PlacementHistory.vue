<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center
                  justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Placement History</h3>
          <small class="text-muted">
            Your successful placements and offers
          </small>
        </div>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <div v-if="store.loadingPlacements" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="!store.placements.length"
           class="text-center py-5">
        <i class="bi bi-trophy fs-1 text-muted d-block mb-3"></i>
        <h5 class="text-muted">No Placements Yet</h5>
        <p class="text-muted small">
          When you get selected, offers will appear here.
        </p>
        <router-link :to="`/student/${userStore.studentId}`"
                     class="btn btn-primary mt-2">
          <i class="bi bi-briefcase me-2"></i>Browse Open Drives
        </router-link>
      </div>

      <div v-else>

        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-primary">
                {{ store.placements.length }}
              </div>
              <small class="text-muted">Total Offers</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-success">
                {{ countByStatus('Joined') }}
              </div>
              <small class="text-muted">Joined</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-warning">
                {{ countByStatus('Offered') }}
              </div>
              <small class="text-muted">Pending</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-info">{{ highestSalary }}</div>
              <small class="text-muted">Best Package</small>
            </div>
          </div>
        </div>

        <div v-if="store.hasActivePlacement"
             class="alert alert-success d-flex
                    align-items-center gap-2 mb-4">
          <i class="bi bi-trophy-fill fs-4"></i>
          <strong>Congratulations!</strong>
          You have an active placement offer waiting for your response.
        </div>

        <div class="d-flex flex-column gap-3">
          <div v-for="p in store.placements" :key="p.id"
               class="card border-0 shadow-sm placement-card"
               :class="{
                 'border-start border-4 border-success':
                   p.status === 'Joined',
                 'border-start border-4 border-warning':
                   p.status === 'Offered',
                 'border-start border-4 border-danger':
                   p.status === 'Declined',
               }">
            <div class="card-body p-4">
              <div class="d-flex justify-content-between
                          align-items-start flex-wrap gap-2">
                <div>
                  <!-- position_title, company_name from placement_fields -->
                  <h5 class="fw-bold mb-1">{{ p.position_title }}</h5>
                  <p class="text-muted mb-0 small">
                    <i class="bi bi-building me-1"></i>
                    {{ p.company_name }}
                  </p>
                </div>
                <span class="badge fs-6 px-3 py-2"
                      :class="statusBadge(p.status)">
                  <i class="bi me-1" :class="statusIcon(p.status)"></i>
                  {{ p.status }}
                </span>
              </div>

              <div class="row g-3 mt-2">
                <div class="col-md-4">
                  <small class="text-muted d-block">Package</small>
                  <!-- salary, currency from placement_fields -->
                  <strong class="text-success">
                    {{ formatSalary(p.salary, p.currency) }}
                  </strong>
                </div>
                <!-- joining_date from placement_fields -->
                <div v-if="p.joining_date" class="col-md-4">
                  <small class="text-muted d-block">Joining Date</small>
                  <strong>{{ fmt(p.joining_date) }}</strong>
                </div>
                <div class="col-md-4">
                  <small class="text-muted d-block">Offer Received</small>
                  <strong>{{ fmt(p.created_at) }}</strong>
                </div>
              </div>

              <!-- offer_letter from placement_fields -->
              <div v-if="p.offer_letter" class="mt-3">
                <a :href="p.offer_letter" target="_blank"
                   class="btn btn-outline-primary btn-sm">
                  <i class="bi bi-file-earmark-pdf me-1"></i>
                  View Offer Letter
                </a>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useStudentStore }     from '@/stores/studentStore'
import { useUserStore }        from '@/stores/userStore'

const store     = useStudentStore()
const userStore = useUserStore()

const countByStatus = status =>
  store.placements.filter(p => p.status === status).length

const highestSalary = computed(() => {
  const salaries = store.placements.map(p => p.salary).filter(Boolean)
  if (!salaries.length) return 'N/A'
  return formatSalary(Math.max(...salaries))
})

onMounted(() => store.fetchPlacements(userStore.studentId))

// salary, currency from placement_fields marshal
function formatSalary(s, currency = 'INR') {
  if (!s) return 'Not disclosed'
  const sym = currency === 'INR' ? '₹' : (currency ?? '₹')
  return s >= 100_000
    ? `${sym}${(s / 100_000).toFixed(1)} LPA`
    : `${sym}${s.toLocaleString('en-IN')}`
}
function fmt(d) {
  return d
    ? new Date(d).toLocaleDateString('en-IN', {
        day: 'numeric', month: 'short', year: 'numeric',
      })
    : '—'
}
function statusBadge(s) {
  return {
    Offered:  'bg-warning text-dark',
    Joined:   'bg-success',
    Declined: 'bg-danger',
  }[s] ?? 'bg-secondary'
}
function statusIcon(s) {
  return {
    Offered:  'bi-envelope-open',
    Joined:   'bi-trophy',
    Declined: 'bi-x-circle',
  }[s] ?? 'bi-circle'
}
</script>

<style scoped>
.placement-card { transition: transform .15s; }
.placement-card:hover { transform: translateY(-2px); }
</style>
