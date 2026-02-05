<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container-fluid">
      <!-- Logo/Brand -->
      <router-link to="/" class="navbar-brand fw-bold">
        <i class="bi bi-briefcase-fill me-2"></i>
        CampusHire
      </router-link>

      <!-- Toggle Button for Mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navbar Links -->
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item" v-if="!isLoggedIn">
            <router-link to="/" class="nav-link active">Home</router-link>
          </li>
          <li class="nav-item" v-if="isLoggedIn">
            <router-link :to="`/${role}/${id}`" class="nav-link active">Home</router-link>
          </li>
          <li v-for="item in roleLinks" :key="item.path" class="nav-item">
            <router-link :to="item.path" class="nav-link">
              {{ item.name }}
            </router-link>
          </li>
          <li>
            <router-link to="/about" class="nav-link">about</router-link>
          </li>
          <!-- User Menu Dropdown -->
          <li class="nav-item dropdown" v-if="isLoggedIn">
            <a
              class="nav-link dropdown-toggle"
              href="#"
              id="userDropdown"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              <i class="bi bi-person-circle me-1"></i>
              Account
            </a>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
               <li>
                <router-link to="/profile" class="dropdown-item">
                  <i class="bi bi-person me-2"></i>Profile
                </router-link>
              </li>
              <li v-for="item in accountLinks" :key="item.path">
                <router-link :to="item.path" class="dropdown-item">
                  {{ item.name }}
                </router-link>
              </li>
              <li><hr class="dropdown-divider" /></li>
              <li>
                <a href="#" class="dropdown-item" @click="logout">
                  <i class="bi bi-box-arrow-right me-2"></i>Logout
                </a>
              </li>
            </ul>
          </li>

          <!-- Sign In/Up Button -->
          <li v-if="!isLoggedIn" class="nav-item ms-lg-2">
            <router-link to="/login" class="btn btn-primary btn-sm">
              Sign In
            </router-link>
          </li>
        </ul>
      </div>
    </div>
  </nav>
</template>


<script>
import router from '@/router';

export default {
  name: "Navbar",
  data() {
    return {
      role: localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")).role : null,
      id: localStorage.getItem("user") ? JSON.parse(localStorage.getItem("user")).id : null,
      isLoggedIn: !!localStorage.getItem("token")
    };
  },

  computed: {
    roleLinks() {
      if (this.role === "admin" && this.isLoggedIn) {
        return [
          { name: "Students", path: "/admin/students" },
          { name: "Companies", path: "/admin/companies" }
        ];
      }
      if (this.role === "student" && this.isLoggedIn) {
        return [
          { name: "History", path: "/student/history" }
        ];
      }

      if (this.role === "company" && this.isLoggedIn) {
        this.$router.push(`/company/${this.id}`);
        return [
          { name: "Create Job", path: "/company/create_job" }
        ];
      }

      return [];
    },

    accountLinks() {
      if (this.role === "student" && this.isLoggedIn) {
        return [
          { name: "Applications", path: "/student/applications/history" },
          { name: "Saved Jobs", path: "/saved-jobs" }
        ];
      }

      if (this.role === "company" && this.isLoggedIn) {
        return [
          { name: "My Drives", path: "/company" }
        ];
      }

      return [];
    }
  },

  methods: {
    logout() {
      localStorage.clear();
      this.$router.push("/login");
    }
  }
};
</script>

<style scoped>
.navbar {
  border-bottom: 2px solid #0d6efd;
}

.navbar-brand {
  font-size: 1.5rem;
  color: #fff !important;
}

.navbar-brand:hover {
  color: #0d6efd !important;
  transition: color 0.3s ease;
}

.nav-link {
  color: #adb5bd !important;
  font-weight: 500;
  margin: 0 8px;
  transition: color 0.3s ease;
}

.nav-link:hover,
.nav-link.active {
  color: #0d6efd !important;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
  font-weight: 500;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0b5ed7;
}

.dropdown-menu {
  border-radius: 8px;
  border: none;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.dropdown-item {
  color: #212529;
  transition: background-color 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
  color: #0d6efd;
}

@media (max-width: 768px) {
  .nav-link {
    margin: 0.5rem 0;
  }

  .btn-primary {
    width: 100%;
    margin-top: 0.5rem;
  }
}
</style>
