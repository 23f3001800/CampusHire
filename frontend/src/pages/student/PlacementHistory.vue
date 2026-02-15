<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:960px">

      <div class="d-flex align-items-center justify-content-between mb-4">
        <div>
          <h3 class="fw-bold mb-0">My Placement History</h3>
          <small class="text-muted">Your successful placements and offers</small>
        </div>
        <router-link :to="`/student/${userStore.studentId}`" class="btn btn-outline-secondary btn-sm">
          <i class="bi bi-arrow-left me-1"></i>Dashboard
        </router-link>
      </div>

      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
      </div>

      <div v-else-if="!placements.length" class="empty-state text-center py-5">
        <i class="bi bi-trophy fs-1 text-muted d-block mb-3"></i>
        <h5 class="text-muted">No Placements Yet</h5>
        <p class="text-muted small">When you get selected by companies, they'll appear here.</p>
        <router-link :to="`/student/${userStore.studentId}`" class="btn btn-primary mt-2">
          <i class="bi bi-briefcase me-2"></i>Browse Open Drives
        </router-link>
      </div>

      <div v-else>
        <!-- Summary cards -->
        <div class="row g-3 mb-4">
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-primary">{{ placements.length }}</div>
              <small class="text-muted">Total Offers</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-success">{{ placementsByStatus('Joined') }}</div>
              <small class="text-muted">Joined</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-warning">{{ placementsByStatus('Offered') }}</div>
              <small class="text-muted">Pending</small>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="card border-0 shadow-sm text-center py-3">
              <div class="fw-bold fs-3 text-danger">{{ placementsByStatus('Declined') }}</div>
              <small class="text-muted">Declined</small>
            </div>
          </div>
        </div>

        <!-- Placements list -->
        <div class="d-flex flex-column gap-3">
          <div v-for="p in placements" :key="p.id"
            class="card border-0 shadow-sm placement-card"
            :class="{ 'border-start border-4 border-success': p.status === 'Joined' }">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start flex-wrap gap-2">
                <div>
                  <h5 class="fw-bold mb-1">{{ p.position_title }}</h5>
                  <p class="text-muted mb-0">
                    <i class="bi bi-building me-1"></i>{{ p.company_name }}
                  </p>
                </div>
                <span class="badge fs-6 px-3 py-2" :class="statusBadge(p.status)">
                  {{ p.status }}
                </span>
              </div>

              <div class="row g-3 mt-2">
                <div class="col-md-4">
                  <small class="text-muted d-block">Package</small>
                  <strong class="text-success">{{ formatSalary(p.salary, p.currency) }}</strong>
                </div>
                <div class="col-md-4" v-if="p.joining_date">
                  <small class="text-muted d-block">Joining Date</small>
                  <strong>{{ formatDate(p.joining_date) }}</strong>
                </div>
                <div class="col-md-4">
                  <small class="text-muted d-block">Offer Received</small>
                  <strong>{{ formatDate(p.created_at) }}</strong>
                </div>
              </div>

              <div v-if="p.offer_letter" class="mt-3">
                <a :href="p.offer_letter" target="_blank" class="btn btn-outline-primary btn-sm">
                  <i class="bi bi-file-earmark-pdf me-1"></i>View Offer Letter
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { useUserStore } from '@/stores/userStore'
import api from '@/utils/api'

export default {
  name: 'PlacementHistory',
  setup() {
    return { userStore: useUserStore() }
  },
  data: () => ({
    placements: [],
    loading: false,
  }),
  async mounted() {
    this.loading = true
    try {
      this.placements = await api.get(`/student/${this.userStore.studentId}/placements`)
    } catch (e) {
      console.error(e)
    } finally {
      this.loading = false
    }
  },
  methods: {
    placementsByStatus(status) {
      return this.placements.filter(p => p.status === status).length
    },
    formatSalary(s, currency = 'INR') {
      if (!s) return 'Not disclosed'
      const sym = currency === 'INR' ? '₹' : currency
      return s >= 100000 ? `${sym}${(s / 100000).toFixed(1)} LPA` : `${sym}${s.toLocaleString('en-IN')}`
    },
    formatDate(d) {
      return d ? new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }) : '—'
    },
    statusBadge(s) {
      return { Offered: 'bg-warning text-dark', Joined: 'bg-success', Declined: 'bg-danger' }[s] || 'bg-secondary'
    },
  },
}
</script>

<style scoped>
.placement-card { transition: transform .15s; }
.placement-card:hover { transform: translateY(-2px); }
</style>