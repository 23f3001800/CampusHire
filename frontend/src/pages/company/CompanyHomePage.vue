<template>

<!-- LOADING -->
<div v-if="!CompanyStore.company_profile" class="text-center py-5">
  Loading company profile...
</div>

<!-- APPROVED -->
<div v-else-if="CompanyStore.company_profile.approval_status === 'Approved'" class="container py-4">

  <div class="d-flex justify-content-between align-items-center mb-4">
    <h3 class="fw-bold">Company Dashboard</h3>
    <router-link to="/company/create_job" class="btn btn-success">
      + Create Job
    </router-link>
  </div>
  <div class="row g-4">
    <div class="col-md-6" v-for="job in jobs" :key="job.id">
      <div class="card shadow-sm">
        <div class="card-body">
          <h5>{{ job.title }}</h5>
          <p class="text-muted">Applicants: {{ job.applicants }}</p>
          <router-link
            :to="`/company/drive/${job.id}`"
            class="btn btn-outline-primary btn-sm"
          >
            View Details
          </router-link>
        </div>
      </div>
    </div>
  </div>

</div>

<!-- NOT APPROVED -->
<div v-else class="container py-4">
  <div>
    Please complete your company profile
    <router-link
      :to="`/company/profile`"
      class="btn btn-primary ms-2"
    >
      Go to Profile
    </router-link>
  </div>

  <div class="alert alert-warning text-center mt-3">
    Your company profile is under review.
  </div>
</div>

</template>

<script>
import { useCompanyStore } from '@/stores/company';
import { useUserStore } from '@/stores/user';

export default {
  name: 'CompanyHomePage',
  data() {
  const user = JSON.parse(localStorage.getItem("user"));
  return {
    id: user?.company_id || null,
    };
  },
  setup() {
    const CompanyStore = useCompanyStore();
    const userStore = useUserStore();
    return {
      CompanyStore,
      userStore,
    };
  },
  async created() {
    // Fetch jobs when component is created
      await this.CompanyStore.fetchCompanyProfile(this.id);
  },
};
</script>