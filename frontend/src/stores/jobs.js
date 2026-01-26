// jobs
// jobDetails
// filters

import { defineStore } from "pinia"
import api from "@/utils/api"
export const useJobsStore = defineStore("jobs", {
    state: () => ({
        jobs: [],
        jobDetails: null,
        filters: {
            location: null,
            type: null,
            company: null,
            keywords: null
        },
        loading: false
    }),
    actions: {
        async fetchJobs() {
            this.loading = true
            try {
                const res = await api.get("/jobs", { params: this.filters })
                this.jobs = res.data
            } finally {
                this.loading = false
            }
        },

        async fetchJobDetails(jobId) {
            this.loading = true
            try {
                const res = await api.get(`/jobs/${jobId}`)
                this.jobDetails = res.data
            } finally {
                this.loading = false
            }
        },

        setFilters(newFilters) {
            this.filters = { ...this.filters, ...newFilters }
        }
    }
})
