<template>
  <div class="container py-4">
    <h3 class="fw-bold mb-4">Available Jobs</h3>

    <div class="row g-4">
      <div class="col-md-4" v-for="job in jobs" :key="job.id">
        <div class="card shadow-sm h-100">
          <div class="card-body">
            <h5>{{ job.title }}</h5>
            <p class="text-muted">{{ job.company }}</p>
            <p>{{ job.location }}</p>
            <button class="btn btn-primary w-100">Apply</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "StudentHomePage",
  data() {
    return {
      jobs: [
        { id: 1, title: "Frontend Intern", company: "ABC Pvt Ltd", location: "Chennai" },
        { id: 2, title: "Backend Developer", company: "XYZ Tech", location: "Bangalore" }
      ]
    };
  }
};
</script>
<style scoped></style>