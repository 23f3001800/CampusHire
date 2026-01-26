import { createRouter, createWebHistory } from 'vue-router'

import HomePage from "@/pages/HomePage.vue"; 

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", component: HomePage },
    { path: "/login", component: () => import("@/pages/LoginPage.vue") },
    { path: "/signup", component: () => import("@/pages/SignupPage.vue") }
    
  ],
})

export default router
