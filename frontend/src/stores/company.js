// companyProfile
// jobs
// applicants

import { defineStore } from "pinia"
import api from "@/utils/api"


export const CompanyStore = defineStore("company", {
    state: () => ({
        company_profile: null,
        jobs: [],
        applicants: {},
        loading: false
    }),
    actions: {
        async fetchCompanyProfile() {
            this.loading = true
            try {
                const res = await api.get("/company/profile")
                this.company_profile = res.data
            } finally {
                this.loading = false
            }
        },

        async fetchJobs() {
            const res = await api.get("/company/jobs")
            this.jobs = res.data
        }, 

        async fetchApplicants(jobId) {
            const res = await api.get(`/company/applicants/${jobId}`)
            this.applicants[jobId] = res.data
        },

        async createJob(jobData) {
            await api.post("/company/jobs", jobData)
            await this.fetchJobs()
        },
        async updateApplicationStatus(jobId, applicantId, status) {
            await api.put(`/company/applicants/${jobId}/${applicantId}`, { status })
            await this.fetchApplicants(jobId)
        }
    }
})