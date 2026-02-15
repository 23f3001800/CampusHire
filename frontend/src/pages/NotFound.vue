<template>
  <div class="error-page">
    <div class="container text-center py-5">
      <div class="error-content">
        <i class="bi bi-exclamation-triangle display-1 text-warning mb-4"></i>
        <h1 class="display-4 fw-bold mb-3">404 - Page Not Found</h1>
        <p class="lead text-muted mb-4">
          The page you're looking for doesn't exist.
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
  name: 'NotFound'
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
```

---

## ✅ Complete Integration Checklist

### **1. File Structure:**
```
src/
├── main.js                      ✅ Configure app
├── App.vue                      ✅ Main layout
├── router/
│   └── index.js                 ✅ Router config with guards
├── stores/
│   ├── userStore.js            ✅ Auth & common methods
│   ├── studentStore.js         ✅ Student data
│   └── companyStore.js         ✅ Company data
├── utils/
│   └── api.js                  ✅ Axios instance
├── components/
│   ├── Navbar.vue              ✅ Navigation
│   └── Footer.vue              ✅ Footer
└── views/
    ├── HomePage.vue            ✅ Landing
    ├── LoginPage.vue           ✅ Login
    ├── SignupPage.vue          ✅ Signup
    ├── AboutPage.vue           ⚠️ Create this
    ├── Unauthorized.vue        ⚠️ Create this
    ├── NotFound.vue            ⚠️ Create this
    ├── student/
    │   ├── Dashboard.vue       ✅ Student home
    │   ├── Profile.vue         ✅ Student profile
    │   ├── Applications.vue    ⚠️ Create this
    │   └── SavedJobs.vue       ⚠️ Create this
    └── company/
        ├── Dashboard.vue       ✅ Company home
        ├── Profile.vue         ⚠️ Create this
        ├── CreateJob.vue       ⚠️ Create this
        ├── JobDetails.vue      ⚠️ Create this
        └── Applicants.vue      ⚠️ Create this
```

### **2. Integration Flow:**
```
User visits site
    ↓
App.vue loads
    ↓
userStore.initialize() runs
    ↓
Check localStorage for token
    ↓
If token exists → Verify with backend
    ↓
Router guard checks authentication
    ↓
Redirect to appropriate page