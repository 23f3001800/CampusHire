import { createRouter, createWebHistory } from "vue-router"


import HomePage from "@/pages/HomePage.vue";


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", component: HomePage },
    { path: "/login", component: () => import("@/pages/LoginPage.vue") },
    { path: "/signup", component: () => import("@/pages/SignupPage.vue") },
    { path: "/admin/:id", component: () => import("@/pages/Admin/AdminHomePage.vue") },
    { path: "/admin/students", component: () => import("@/pages/Admin/StudentListPage.vue") },
    { path: "/admin/companies", component: () => import("@/pages/Admin/CompanyListPage.vue") },
    { path: "/admin/applied-students", component: () => import("@/pages/Admin/AppliedSudents.vue") },
    { path: "/admin/job-details/:id", component: () => import("@/pages/Admin/JobDetails.vue") },
    {path: "/student/:id", component: () => import("@/pages/student/StudentHomePage.vue")},
    {path: "/company/:id", component: () => import("@/pages/company/CompanyHomePage.vue")},
    { path: "/about", component: () => import("@/pages/AboutPage.vue") },
  ],
});

export default router;