// pendingCompanies
// students
// companies
// reports

import { defineStore } from "pinia";
import api from "@/utils/api";

export const useAdminStore = defineStore("admin", {
  state: () => ({
    students: [],
    companies: [],
    reports: [],
    loading: false,
    }), 
    actions: {
        async fetchStudents() {
            const token = localStorage.getItem("token");
            const res = await api.get("/admin/students");
            this.students = res;
            console.log(res);
        },

        async fetchCompanies() {
            const res = await api.get("/admin/companies");
            this.companies = res;
            console.log(res);
        },
        async fetchReports() {
            const res = await api.get("/admin/reports");
            this.reports = res.data;
        },

        async approveCompany(companyId) {
            await api.post(`/admin/approve-company/${companyId}`);
            await this.fetchPendingCompanies();
        },
        async rejectCompany(companyId) {
            await api.post(`/admin/reject-company/${companyId}`);
            await this.fetchPendingCompanies();
        },
        async blockUser(user_id) {
            await api.post(`/admin/block-user/${user_id}`);
            await this.fetchStudents();
        },
        async unblockUser(user_id) {
            await api.post(`/admin/unblock-user/${user_id}`);
            await this.fetchStudents();
        }
    },
});
