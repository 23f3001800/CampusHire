<template>
<div class="container py-4">

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
</template>
