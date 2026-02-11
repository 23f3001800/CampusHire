<template>
  <div>
    <div v-if="!isProfileComplete()"
      class="container mt-4"
    >
      <div class="alert alert-danger d-flex justify-content-between align-items-center shadow-sm">
        
        <div>
          <strong>Profile Incomplete!</strong><br />
          Please complete your profile before applying for jobs.
        </div>

        <router-link
          :to="`/student/profile`"
          class="btn btn-danger"
        >
          Complete Profile
        </router-link>

      </div>
    </div>
    <div class="container py-4">
      <h3 class="fw-bold mb-4">Available Jobs</h3>

      <div class="row g-4">
        <div class="col-md-4" v-for="job in jobStore.jobs" :key="job.id">
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
  </div>
</template>



<script>
import { useUserStore } from "@/stores/user";
import { useJobsStore } from "@/stores/jobs";

export default {
  name : "studenthomepage",
  setup() {
    const userStore = useUserStore();
    const jobStore = useJobsStore()

    const isProfileComplete = () => {
      const s = userStore.studentProfile;

      return (
        s &&
        s.phone_number &&
        s.date_of_birth &&
        s.cgpa &&
        s.graduation_year &&
        s.gender
      );
    };

    return { userStore, isProfileComplete , jobStore};
  },
  async mounted() {
    await this.jobStore.fetchJobs();
  }
};
</script>


<style scoped></style>