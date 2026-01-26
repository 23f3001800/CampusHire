import { defineStore } from "pinia"
import api from "@/utils/api"


export const StudentStore = defineStore("student", {
  state: () => ({
    profile: null,
    applications: [],
    eligibleJobs: [],
    loading: false
  }),

    actions: {
        async fetchProfile() {
        this.loading = true
        try {
            const res = await api.get("/student/profile")
            this.profile = res.data
        } finally {
            this.loading = false
        }
            },

        async fetchEligibleJobs() {
        const res = await api.get("/student/eligible-jobs")
        this.eligibleJobs = res.data
        },

        async fetchApplications() {
        const res = await api.get("/student/applications")
        this.applications = res.data
        },  

        async applyJob(jobId) {
        await api.post(`/student/apply/${jobId}`)
        await this.fetchApplications()
        }
    }
})