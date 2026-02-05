<template>
  <div class="container-fluid mt-4">
    <h1 class="mb-4">Admin Dashboard</h1>

    <!-- Overview Stats -->
    <div class="row mb-4">
      <div class="col-md-3">
        <div class="card text-white bg-primary">
          <div class="card-body">
            <h5 class="card-title">Total Students</h5>
            <p class="card-text">{{ adminStore.students.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-success">
          <div class="card-body">
            <h5 class="card-title">Total Companies</h5>
            <p class="card-text">{{ adminStore.companies.length }}</p>
          </div>
        </div>
      </div>
      <div class="col-md-3">
        <div class="card text-white bg-warning">
          <div class="card-body">
            <h5 class="card-title">Pending Companies</h5>
            <p class="card-text">{{ adminStore.companies.filter(c => c.status === 'pending').length }}</p>
          </div>
        </div>
      </div>
      <!-- <div class="col-md-3">
        <div class="card text-white bg-info">
          <div class="card-body">
            <h5 class="card-title">Reports</h5>
            <p class="card-text">{{ adminStore.reports.length }}</p>
          </div>
        </div>
      </div> -->
    </div>

    <!-- Quick Actions -->
    <div class="row mb-4">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5>Quick Actions</h5>
          </div>
          <div class="card-body">
            <button class="btn btn-primary me-2" @click="$router.push('/admin/students')">Manage Students</button>
            <button class="btn btn-success me-2" @click="$router.push('/admin/companies')">Manage Companies</button>
            <button class="btn btn-info" @click="fetchReports">View Reports</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Pending Companies -->
    <div class="row">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5>Pending Company Approvals</h5>
          </div>
          <div class="card-body">
            <div v-if="adminStore.loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <table v-else class="table table-striped">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in adminStore.companies" :key="company.id">
                  <td>{{ company.user.name }}</td>
                  <td>{{ company.user.email }}</td>
                  <td>
                    <button class="btn btn-success btn-sm me-2" @click="approveCompany(company.id)">Approve</button>
                    <button class="btn btn-danger btn-sm" @click="rejectCompany(company.id)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="adminStore.companies.length === 0" class="text-muted">No pending companies.</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Ongoing Placement Drives -->
    <div class="row" style="margin-top: 25px;">
      <div class="col-md-12">
        <div class="card">
          <div class="card-header">
            <h5>Ongoing Placement drive</h5>
          </div>
          <div class="card-body">
            <div v-if="adminStore.loading" class="text-center">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            <table v-else class="table table-striped">
              <thead>
                <tr>
                  <th>Drive id</th>
                  <th>title</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody v-if="jobsStore.jobs && jobsStore.jobs.length > 0">
                <tr v-for="job in jobsStore.jobs" :key="job.id">
                  <td>{{ job.id }}</td>
                  <td>{{ job.title }}</td>
                  <td>{{ job.description }}</td>
                  <td>
                    <button class="btn btn-success btn-sm me-2" @click="approveJob(job.id)">Approve</button>
                    <button class="btn btn-danger btn-sm" @click="rejectJob(job.id)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <p v-if="jobsStore.jobs.length === 0" class="text-muted">No jobs available.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { useAdminStore } from '@/stores/admin';
import { useJobsStore } from '@/stores/jobs';

export default {
  name: 'AdminHomePage',
  setup() {
    const adminStore = useAdminStore();
    const jobsStore = useJobsStore();
    return { adminStore, jobsStore };
  },
  async mounted() {
    await this.adminStore.fetchCompanies();
    await this.adminStore.fetchStudents();
    await this.jobsStore.fetchJobs();
  },
  methods: {
    async approveCompany(companyId) {
      await this.adminStore.approveCompany(companyId);
    },
    async rejectCompany(companyId) {
      await this.adminStore.rejectCompany(companyId);
    },
    async fetchReports() {
      await this.adminStore.fetchReports();
      // Optionally, navigate to a reports page or show modal
    }
  }
};
</script>

<style scoped>
/* Additional styles if needed */
</style>
