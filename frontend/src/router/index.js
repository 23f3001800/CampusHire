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
const StudentDriveDetail = () => import('@/pages/student/DriveDetail.vue')
const StudentCompanyView  = () => import('@/pages/student/CompanyView.vue')

const CompanyDashboard = () => import('@/pages/company/Dashboard.vue')
const CompanyProfile   = () => import('@/pages/company/Profile.vue')
const CompanyCreateDrive = () => import('@/pages/company/CreateDrive.vue')
const CompanyDriveDetail = () => import('@/pages/company/DriveDetail.vue')
const CompanyApplicants  = () => import('@/pages/company/Applicants.vue')
const CompanyStudentView  = () => import('@/pages/company/StudentView.vue')

const AdminDashboard   = () => import('@/pages/admin/Dashboard.vue')
const AdminStudents    = () => import('@/pages/admin/Students.vue')
const AdminCompanies   = () => import('@/pages/admin/Companies.vue')
const AdminGraphStats   = () => import('@/pages/admin/GraphStats.vue')
const AdminDriveDetail = () => import('@/pages/admin/DriveDetail.vue')
const AdminStudentView  = () => import('@/pages/admin/StudentDetail.vue')
const AdminCompanyView  = () => import('@/pages/admin/CompanyView.vue')

// common routes for both student compny admin can be added here if needed

const  viewprofile = () => import('@/pages/company/ViewProfile.vue')
const  viewdrive = () => import('@/pages/company/DriveDetail.vue')

// ── Route definitions ─────────────────────────────────────────────────────────
const routes = [
  // Public
  { path: '/',        name: 'Home',   component: HomePage },
  { path: '/login',   name: 'Login',  component: LoginPage,  meta: { guestOnly: true } },
  { path: '/signup',  name: 'Signup', component: SignupPage, meta: { guestOnly: true } },
  { path: '/about',   name: 'About',  component: AboutPage },

  // Student
  { path: '/student/:id',                     name: 'StudentDashboard', component: StudentDashboard, meta: { auth: true} },
  { path: '/student/profile',                  name: 'StudentProfile',   component: StudentProfile,   meta: { auth: true, role: 'student' } },
  { path: '/student/applications',             name: 'StudentApps',      component: StudentApps,      meta: { auth: true} },
  { path: '/student/saved-drives',             name: 'StudentSaved',     component: StudentSaved,     meta: { auth: true, role: 'student' } },
  { path: '/student/placement-history',        name: 'StudentPlacements', component: StudentPlacements, meta: { auth: true, role: 'student' } },
  {path: '/student/drives/:driveId', name: 'StudentDriveDetail', component: StudentDriveDetail, meta: { auth: true, role: 'student' } },
  {path: '/student/companies/:companyId', name: 'StudentCompanyView', component: StudentCompanyView, meta: { auth: true, role: 'student' } },
  // Company
  { path: '/company/:id',                      name: 'CompanyDashboard', component: CompanyDashboard,   meta: { auth: true, role: 'company' } },
  { path: '/company/profile',                  name: 'CompanyProfile',   component: CompanyProfile,     meta: { auth: true, role: 'company' } },
  { path: '/company/create-drive',             name: 'CreateDrive',      component: CompanyCreateDrive, meta: { auth: true, role: "company"} },
  { path: '/company/drives/:driveId',          name: 'DriveDetail',      component: CompanyDriveDetail, meta: { auth: true }, role: "company" },
  { path: '/company/students/:studentId', name: 'CompanyStudentView', component: CompanyStudentView, meta: { auth: true, role: 'company' } },
  { path: '/company/drives/:driveId/applicants', name: 'Applicants',     component: CompanyApplicants,  meta: { auth: true} },

  // Admin
  { path: '/admin/:id',        name: 'AdminDashboard', component: AdminDashboard, meta: { auth: true, role: 'admin' } },
  { path: '/admin/students',   name: 'AdminStudents',  component: AdminStudents,  meta: { auth: true, role: 'admin' } },
  { path: '/admin/companies',  name: 'AdminCompanies', component: AdminCompanies, meta: { auth: true, role: 'admin' } },
  { path: '/admin/graph-stats', name: 'AdminGraphStats', component: AdminGraphStats, meta: { auth: true, role: 'admin' } },
  {path: '/admin/drives/:driveId', name: 'AdminDriveDetail', component: AdminDriveDetail, meta: { auth: true, role: 'admin' } },
  {path: '/admin/students/:studentId', name: 'AdminStudentView', component: AdminStudentView, meta: { auth: true, role: 'admin' } },
  {path: '/admin/companies/:companyId', name: 'AdminCompanyView', component: AdminCompanyView, meta: { auth: true, role: 'admin' } },

  // Common
  { path: '/view-profile/:userId', name: 'ViewProfile', component: viewprofile, meta: { auth: true} },
  { path: '/view-drive/:driveId', name: 'ViewDrive', component: viewdrive, meta: { auth: true} },
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