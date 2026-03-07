<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark shadow-sm">
    <div class="container-fluid px-4">

      <!-- Brand -->
      <router-link :to="homePath" class="navbar-brand fw-bold">
        <i class="bi bi-briefcase-fill me-2"></i>CampusHire
      </router-link>

      <!-- Mobile toggler -->
      <button class="navbar-toggler border-0" type="button"
        data-bs-toggle="collapse" data-bs-target="#navbarMain"
        aria-controls="navbarMain" aria-expanded="false">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarMain">

        <!-- Primary nav links -->
        <ul class="navbar-nav me-auto">
          <li v-for="link in navConfig.primary" :key="link.name" class="nav-item">
            <router-link :to="resolveLink(link)" class="nav-link" active-class="active">
              <i :class="`bi ${link.icon} me-1`"></i>{{ link.label }}
            </router-link>
          </li>
        </ul>

        <!-- Right side -->
        <ul class="navbar-nav align-items-lg-center gap-1">

          <!-- Guest -->
          <template v-if="!store.isAuthenticated">
            <li class="nav-item">
              <router-link to="/login" class="btn btn-outline-light btn-sm px-3">
                Sign In
              </router-link>
            </li>
            <li class="nav-item ms-1">
              <router-link to="/signup" class="btn btn-primary btn-sm px-3">
                Sign Up
              </router-link>
            </li>
          </template>

          <!-- Authenticated: account dropdown -->
          <li v-else class="nav-item dropdown">
            <a class="nav-link dropdown-toggle d-flex align-items-center gap-2"
              href="#" data-bs-toggle="dropdown" aria-expanded="false">
              <span class="avatar-circle">{{ initials }}</span>
              <span class="d-none d-lg-inline">{{ store.userName }}</span>
            </a>

            <ul class="dropdown-menu dropdown-menu-end shadow py-2">
              <li class="px-3 pb-2">
                <div class="fw-semibold text-dark small lh-tight">{{ store.userName }}</div>
                <div class="text-muted" style="font-size:.75rem">{{ store.userEmail }}</div>
                <span class="badge mt-1" :class="roleBadge">{{ store.role }}</span>
              </li>
              <li><hr class="dropdown-divider my-1"></li>
              <li>
                <a href="#" class="dropdown-item py-2 text-danger" @click.prevent="logout">
                  <i class="bi bi-box-arrow-right me-2"></i>Sign Out
                </a>
              </li>
            </ul>
          </li>

        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
import { useUserStore } from '@/stores/userStore'

const NAV = {
  student: {
    primary: [
      { label: 'Dashboard',    icon: 'bi-speedometer2',      name: 'StudentDashboard', dynamic: true },
      { label: 'MyJourney', icon: 'bi-file-earmark-text', name: 'StudentJourney' },
      { label: 'Saved Drives', icon: 'bi-bookmark',          name: 'StudentSaved' },
      { label: 'My Profile',   icon: 'bi-person-circle',     name: 'StudentProfile' },
    ],
  },
  company: {
    primary: [
      { label: 'Dashboard',  icon: 'bi-speedometer2', name: 'CompanyDashboard', dynamic: true },
      { label: 'Post Drive', icon: 'bi-plus-circle',  name: 'CreateDrive' },
      { label: 'Profile',    icon: 'bi-building',     name: 'CompanyProfile' },
    ],
  },
  admin: {
    primary: [
      { label: 'Dashboard', icon: 'bi-speedometer2',   name: 'AdminDashboard',  dynamic: true },
      { label: 'Students',  icon: 'bi-people',         name: 'AdminStudents' },
      { label: 'Companies', icon: 'bi-building',       name: 'AdminCompanies' },
      { label: 'Stats',     icon: 'bi-bar-chart-line', name: 'AdminGraphStats' },
    ],
  },
}

const DASHBOARD_NAME = {
  student: 'StudentDashboard',
  company: 'CompanyDashboard',
  admin:   'AdminDashboard',
}

export default {
  name: 'Navbar',
  setup() { return { store: useUserStore() } },
  computed: {
    navConfig() {
      return NAV[this.store.role] || { primary: []}
    },
    homePath() {
      if (!this.store.isAuthenticated) return '/'
      return this.resolveLink({ name: DASHBOARD_NAME[this.store.role], dynamic: true })
    },
    initials() {
      return (this.store.userName || '?')
        .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
    },
    roleBadge() {
      return { student: 'bg-primary', company: 'bg-success', admin: 'bg-danger' }[this.store.role] || 'bg-secondary'
    },
  },
  methods: {
    resolveLink(link) {
      return link.dynamic
        ? { name: link.name, params: { id: this.store.id } }
        : { name: link.name }
    },
    async logout() {
      await this.store.logout()
    },
  },
}
</script>

<style scoped>
.navbar             { border-bottom: 2px solid #0d6efd; }
.navbar-brand       { font-size: 1.25rem; color: #fff !important; transition: color .2s; }
.navbar-brand:hover { color: #0d6efd !important; }

.nav-link {
  color: #adb5bd !important;
  font-weight: 500;
  font-size: .9rem;
  padding: .5rem .75rem !important;
  position: relative;
  transition: color .2s;
}
.nav-link:hover       { color: #fff !important; }
.nav-link.active      { color: #fff !important; }
.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0; left: .75rem; right: .75rem;
  height: 2px;
  background: #0d6efd;
  border-radius: 2px 2px 0 0;
}

.avatar-circle {
  width: 32px; height: 32px;
  border-radius: 50%;
  background: #0d6efd; color: #fff;
  font-size: .72rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
  border: 2px solid rgba(255,255,255,.2);
}

.dropdown-menu {
  border: none;
  border-radius: 12px;
  min-width: 220px;
  box-shadow: 0 8px 32px rgba(0,0,0,.15) !important;
  animation: dropIn .15s ease;
}
@keyframes dropIn {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}
.dropdown-item {
  font-size: .9rem;
  border-radius: 6px;
  margin: 1px 4px;
  width: calc(100% - 8px);
  transition: background .15s;
}
.dropdown-item:hover              { background: #f0f4ff; }
.dropdown-item.text-danger:hover  { background: #fff5f5; }
</style>
