import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/stores/userStore'

// ── Lazy-loaded pages ─────────────────────────────────────────────────────────
const HomePage         = () => import('@/pages/HomePage.vue')
const AboutPage        = () => import('@/pages/AboutPage.vue')
const LoginPage        = () => import('@/pages/LoginPage.vue')
const SignupPage       = () => import('@/pages/SignupPage.vue')
const NotFound         = () => import('@/pages/NotFound.vue')
const Unauthorized     = () => import('@/pages/Unauthorized.vue')

const StudentDashboard = () => import('@/pages/student/Dashboard.vue')
const StudentProfile   = () => import('@/pages/student/Profile.vue')
const StudentApps      = () => import('@/pages/student/Applications.vue')
const StudentSaved     = () => import('@/pages/student/SavedDrives.vue')
const StudentPlacements   = () => import('@/pages/student/PlacementHistory.vue')

const CompanyDashboard = () => import('@/pages/company/Dashboard.vue')
const CompanyProfile   = () => import('@/pages/company/Profile.vue')
const CompanyCreateDrive = () => import('@/pages/company/CreateDrive.vue')
const CompanyDriveDetail = () => import('@/pages/company/DriveDetail.vue')
const CompanyApplicants  = () => import('@/pages/company/Applicants.vue')

const AdminDashboard   = () => import('@/pages/admin/Dashboard.vue')
const AdminStudents    = () => import('@/pages/admin/Students.vue')
const AdminCompanies   = () => import('@/pages/admin/Companies.vue')

// ── Route definitions ─────────────────────────────────────────────────────────
const routes = [
  // Public
  { path: '/',        name: 'Home',   component: HomePage },
  { path: '/login',   name: 'Login',  component: LoginPage,  meta: { guestOnly: true } },
  { path: '/signup',  name: 'Signup', component: SignupPage, meta: { guestOnly: true } },
  { path: '/about',   name: 'About',  component: AboutPage },

  // Student
  { path: '/student/:id',                     name: 'StudentDashboard', component: StudentDashboard, meta: { auth: true, role: 'student' } },
  { path: '/student/profile',                  name: 'StudentProfile',   component: StudentProfile,   meta: { auth: true, role: 'student' } },
  { path: '/student/applications',             name: 'StudentApps',      component: StudentApps,      meta: { auth: true, role: 'student' } },
  { path: '/student/saved-drives',             name: 'StudentSaved',     component: StudentSaved,     meta: { auth: true, role: 'student' } },
  { path: '/student/placement-history',        name: 'StudentPlacements', component: StudentPlacements, meta: { auth: true, role: 'student' } },
  // Company
  { path: '/company/:id',                      name: 'CompanyDashboard', component: CompanyDashboard,   meta: { auth: true, role: 'company' } },
  { path: '/company/profile',                  name: 'CompanyProfile',   component: CompanyProfile,     meta: { auth: true, role: 'company' } },
  { path: '/company/create-drive',             name: 'CreateDrive',      component: CompanyCreateDrive, meta: { auth: true, role: 'company' } },
  { path: '/company/drives/:driveId',          name: 'DriveDetail',      component: CompanyDriveDetail, meta: { auth: true, role: 'company' } },
  { path: '/company/drives/:driveId/applicants', name: 'Applicants',     component: CompanyApplicants,  meta: { auth: true, role: 'company' } },

  // Admin
  { path: '/admin/:id',        name: 'AdminDashboard', component: AdminDashboard, meta: { auth: true, role: 'admin' } },
  { path: '/admin/students',   name: 'AdminStudents',  component: AdminStudents,  meta: { auth: true, role: 'admin' } },
  { path: '/admin/companies',  name: 'AdminCompanies', component: AdminCompanies, meta: { auth: true, role: 'admin' } },

  // Error
  { path: '/unauthorized', name: 'Unauthorized', component: Unauthorized },
  { path: '/:pathMatch(.*)*', name: 'NotFound',  component: NotFound },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: (to, from, saved) => saved || { top: 0 },
})

// ── Navigation guard ──────────────────────────────────────────────────────────
router.beforeEach(async (to, from, next) => {
  const store = useUserStore()
  if (!store.isInitialized) await store.initialize()

  if (to.meta.auth && !store.isAuthenticated) {
    return next({ path: '/login', query: { redirect: to.fullPath } })
  }
  if (to.meta.role && store.role !== to.meta.role) {
    return next('/unauthorized')
  }
  if (to.meta.guestOnly && store.isAuthenticated) {
    return next(`/${store.role}/${store.id}`)
  }
  next()
})

export default router