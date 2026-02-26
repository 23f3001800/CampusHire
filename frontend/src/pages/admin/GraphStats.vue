<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:1100px">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading…</span>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger" style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3" @click="loadAll">
          <i class="bi bi-arrow-clockwise me-1"></i>Retry
        </button>
      </div>

      <!-- Charts -->
      <div v-else>

        <!-- Header -->
        <div class="d-flex align-items-center justify-content-between mb-4 flex-wrap gap-2">
          <div>
            <h3 class="fw-bold mb-1">Admin Analytics</h3>
            <p class="text-muted mb-0 small">
              Platform-wide charts across all companies, drives, students and placements
            </p>
          </div>
          <button class="btn btn-outline-secondary btn-sm"
                  :disabled="refreshing"
                  @click="refresh">
            <span v-if="refreshing"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-arrow-clockwise me-1"></i>
            Refresh
          </button>
        </div>

        <!-- Row 1: Companies by Approval + Drives by Status -->
        <div class="row g-4 mb-4">

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-building-check me-2 text-primary"></i>
                  Companies by Approval Status
                </h6>
              </div>
              <div class="card-body d-flex align-items-center
                          justify-content-center">
                <div class="chart-wrap">
                  <canvas ref="companyApprovalRef"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-briefcase me-2 text-success"></i>
                  Drives by Status
                </h6>
              </div>
              <div class="card-body d-flex align-items-center
                          justify-content-center">
                <div class="chart-wrap">
                  <canvas ref="driveStatusRef"></canvas>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Row 2: Students by Branch + Placements by Company -->
        <div class="row g-4 mb-4">

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-mortarboard me-2 text-info"></i>
                  Students by Branch
                </h6>
              </div>
              <div class="card-body">
                <div class="chart-wrap-bar">
                  <canvas ref="studentsBranchRef"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-trophy me-2 text-warning"></i>
                  Top Companies by Placements
                </h6>
              </div>
              <div class="card-body">
                <div class="chart-wrap-bar">
                  <canvas ref="placementsCompanyRef"></canvas>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Row 3: Application Status Distribution -->
        <div class="row g-4">

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-people me-2 text-danger"></i>
                  Applications by Status
                </h6>
              </div>
              <div class="card-body d-flex align-items-center
                          justify-content-center">
                <div class="chart-wrap">
                  <canvas ref="appStatusRef"></canvas>
                </div>
              </div>
            </div>
          </div>

          <div class="col-md-6">
            <div class="card border-0 shadow-sm h-100">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-bar-chart me-2 text-primary"></i>
                  Drives Posted per Month
                </h6>
              </div>
              <div class="card-body">
                <div class="chart-wrap-bar">
                  <canvas ref="drivesMonthRef"></canvas>
                </div>
              </div>
            </div>
          </div>

        </div>

      </div>
    </div>
  </div>
</template>

<script setup>
import {
  ref,
  onMounted,
  onBeforeUnmount,
  nextTick,
  watch,
} from 'vue'
import {
  Chart,
  ArcElement,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  DoughnutController,
  BarController,
} from 'chart.js'
import { useAdminStore } from '@/stores/adminStore'

// Register all needed Chart.js components
Chart.register(
  ArcElement,
  BarElement,
  LineElement,
  PointElement,
  CategoryScale,
  LinearScale,
  Tooltip,
  Legend,
  DoughnutController,
  BarController,
)

const store = useAdminStore()

// ── State ──────────────────────────────────────────────────────────────────
const loading    = ref(true)
const refreshing = ref(false)
const error      = ref('')

// ── Canvas refs ────────────────────────────────────────────────────────────
const companyApprovalRef  = ref(null)
const driveStatusRef      = ref(null)
const studentsBranchRef   = ref(null)
const placementsCompanyRef = ref(null)
const appStatusRef        = ref(null)
const drivesMonthRef      = ref(null)

// ── Chart instances (for cleanup) ──────────────────────────────────────────
let charts = {}

// ── Destroy all charts before re-drawing ──────────────────────────────────
function destroyAll() {
  Object.values(charts).forEach(c => c?.destroy())
  charts = {}
}

// ── Draw all charts from store data ───────────────────────────────────────
function drawAll() {
  destroyAll()

  // 1. Companies by Approval — Doughnut
  const approvalCounts = store.companyApprovalCounts
    || { Approved: 0, Pending: 0, Rejected: 0 }

  charts.companyApproval = new Chart(companyApprovalRef.value, {
    type: 'doughnut',
    data: {
      labels: ['Approved', 'Pending', 'Rejected'],
      datasets: [
        {
          data: [
            approvalCounts.Approved || 0,
            approvalCounts.Pending  || 0,
            approvalCounts.Rejected || 0,
          ],
          backgroundColor: ['#198754', '#ffc107', '#dc3545'],
          borderWidth: 2,
          borderColor: '#fff',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { usePointStyle: true, padding: 16 },
        },
        tooltip: {
          callbacks: {
            label: ctx =>
              ` ${ctx.label}: ${ctx.parsed}`,
          },
        },
      },
    },
  })

  // 2. Drives by Status — Doughnut
  const driveCounts = store.driveStatusCounts
    || { Open: 0, Closed: 0, Completed: 0 }

  charts.driveStatus = new Chart(driveStatusRef.value, {
    type: 'doughnut',
    data: {
      labels: ['Open', 'Closed', 'Completed'],
      datasets: [
        {
          data: [
            driveCounts.Open      || 0,
            driveCounts.Closed    || 0,
            driveCounts.Completed || 0,
          ],
          backgroundColor: ['#0d6efd', '#6c757d', '#0dcaf0'],
          borderWidth: 2,
          borderColor: '#fff',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { usePointStyle: true, padding: 16 },
        },
      },
    },
  })

  // 3. Students by Branch — Vertical Bar
  const branchMap = store.studentsByBranch || {}
  const branchLabels = Object.keys(branchMap)
  const branchValues = branchLabels.map(k => branchMap[k])

  charts.studentsBranch = new Chart(studentsBranchRef.value, {
    type: 'bar',
    data: {
      labels: branchLabels,
      datasets: [
        {
          label: 'Students',
          data: branchValues,
          backgroundColor: 'rgba(13,110,253,0.75)',
          borderColor: '#0d6efd',
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
          grid: { color: 'rgba(0,0,0,0.05)' },
        },
      },
    },
  })

  // 4. Top Companies by Placements — Horizontal Bar
  const placementEntries = store.placementsByCompany || []
  const placementLabels  = placementEntries.map(([name]) => name)
  const placementValues  = placementEntries.map(([, count]) => count)

  charts.placementsCompany = new Chart(placementsCompanyRef.value, {
    type: 'bar',
    data: {
      labels: placementLabels,
      datasets: [
        {
          label: 'Placements',
          data: placementValues,
          backgroundColor: 'rgba(25,135,84,0.75)',
          borderColor: '#198754',
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          beginAtZero: true,
          ticks: { precision: 0 },
          grid: { color: 'rgba(0,0,0,0.05)' },
        },
        y: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
      },
    },
  })

  // 5. Applications by Status — Doughnut
  // Aggregated from adminStore.drives total_applications breakdown
  // or from store.applicationStatusCounts if you add that getter
  const appCounts = store.applicationStatusCounts || {
    Applied: 0, Shortlisted: 0, Selected: 0, Rejected: 0,
  }

  charts.appStatus = new Chart(appStatusRef.value, {
    type: 'doughnut',
    data: {
      labels: ['Applied', 'Shortlisted', 'Selected', 'Rejected'],
      datasets: [
        {
          data: [
            appCounts.Applied     || 0,
            appCounts.Shortlisted || 0,
            appCounts.Selected    || 0,
            appCounts.Rejected    || 0,
          ],
          backgroundColor: ['#0d6efd', '#0dcaf0', '#198754', '#dc3545'],
          borderWidth: 2,
          borderColor: '#fff',
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '65%',
      plugins: {
        legend: {
          position: 'bottom',
          labels: { usePointStyle: true, padding: 16 },
        },
      },
    },
  })

  // 6. Drives Posted per Month — Bar
  // Derived from adminStore.drives grouped by posted_date month
  const monthMap = {}
  for (const d of store.drives || []) {
    if (!d.posted_date) continue
    const key = new Date(d.posted_date)
      .toLocaleDateString('en-IN', { month: 'short', year: '2-digit' })
    monthMap[key] = (monthMap[key] || 0) + 1
  }
  const monthLabels = Object.keys(monthMap)
  const monthValues = monthLabels.map(k => monthMap[k])

  charts.drivesMonth = new Chart(drivesMonthRef.value, {
    type: 'bar',
    data: {
      labels: monthLabels,
      datasets: [
        {
          label: 'Drives',
          data: monthValues,
          backgroundColor: 'rgba(13,202,240,0.75)',
          borderColor: '#0dcaf0',
          borderWidth: 1,
          borderRadius: 4,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { size: 11 } },
        },
        y: {
          beginAtZero: true,
          ticks: { precision: 0 },
          grid: { color: 'rgba(0,0,0,0.05)' },
        },
      },
    },
  })
}

// ── Load data ──────────────────────────────────────────────────────────────
async function loadAll() {
  loading.value = true
  error.value   = ''
  try {
    await store.fetchDashboardStats?.()
    await Promise.all([
      store.fetchCompanies?.(),
      store.fetchDrives?.(),
      store.fetchStudents?.(),
      store.fetchPlacements?.(),
    ])
  } catch (e) {
    error.value = e?.message ?? 'Failed to load analytics.'
    return
  } finally {
    loading.value = false
  }
  // Wait for DOM then draw
  await nextTick()
  drawAll()
}

async function refresh() {
  refreshing.value = true
  try {
    await loadAll()
  } finally {
    refreshing.value = false
  }
}

onMounted(loadAll)
onBeforeUnmount(destroyAll)
</script>

<style scoped>
.chart-wrap {
  position: relative;
  width: 100%;
  height: 280px;
}
.chart-wrap-bar {
  position: relative;
  width: 100%;
  height: 260px;
}
</style>
