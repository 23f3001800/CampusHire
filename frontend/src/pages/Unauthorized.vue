<template>
  <div class="error-page">
    <div class="container text-center py-5">
      <div class="error-content">
        <i class="bi bi-shield-x display-1 text-danger mb-4"></i>
        <h1 class="display-4 fw-bold mb-3">403 - Unauthorized</h1>
        <p class="lead text-muted mb-4">
          You don't have permission to access this page.
        </p>
        <div class="d-flex gap-3 justify-content-center">
          <router-link to="/" class="btn btn-primary">
            <i class="bi bi-house me-2"></i>Go Home
          </router-link>
          <button @click="$router.back()" class="btn btn-outline-secondary">
            <i class="bi bi-arrow-left me-2"></i>Go Back
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Unauthorized'
};
</script>

<style scoped>
.error-page {
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>