<template>
<div class="admin-page">

  <div class="container">

    <div class="page-header">
      <h2>Companies</h2>
      <input v-model="search" placeholder="Search companies..." class="search-box"/>
    </div>

    <div class="table-card">
      <table class="table table-borderless align-middle">
        <thead>
          <tr>
            <th>Company Name</th>
            <th>Email</th>
            <th>Industry</th>
            <th>website</th>
            <th>location</th>
            <th>Status</th>
            <th></th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="c in adminStore.companies" :key="c.id">
            <td class="fw-semibold">{{ c.user.name }}</td>
            <td class="text-muted">{{ c.user.email }}</td>
            <td>{{ c.industry }}</td>
            <td>{{ c.website }}</td>
            <td>{{ c.location }}</td>

            <td>
              <span :class="c.blocked ? 'status-bad' : 'status-good'">
                {{ c.blocked ? 'Blocked' : 'Active' }}
              </span>
            </td>

            <td class="text-end">
              <button
                :class="c.blocked ? 'btn-unblock' : 'btn-block'"
                @click="toggleBlock(c)"
              >
                {{ c.blocked ? 'Unblock' : 'Block' }}
              </button>
            </td>
          </tr>
        </tbody>

      </table>
    </div>

  </div>
</div>
</template>

<script>
import { useAdminStore } from '@/stores/admin';
 
export default {
  name: "CompanyListPage",
  setup() {
    const adminStore = useAdminStore();
    return { adminStore };
  },

  data() {
    return {
      search: "",
      companies: []
    };
  },
  
  async mounted() {
    await this.adminStore.fetchCompanies();
    this.companies = this.adminStore.companies;
  },

  computed: {
    filteredCompanies() {
      return this.companies.filter(c =>
        c.name.toLowerCase().includes(this.search.toLowerCase())
      );
    }
  },
  methods: {
    toggleBlock(user) {
      user.blocked = !user.blocked;
    }
  }
};
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #eef2ff, #f8fafc);
  padding: 40px 0;
}

/* HEADER */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.page-header h2 {
  font-weight: 700;
  color: #1f2937;
}

/* SEARCH */
.search-box {
  border: none;
  padding: 10px 16px;
  border-radius: 10px;
  width: 260px;
  background: white;
  box-shadow: 0 4px 12px rgba(0,0,0,0.06);
  outline: none;
}

/* CARD */
.table-card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.08);
  transition: 0.25s;
}

.table-card:hover {
  transform: translateY(-3px);
}

/* TABLE */
thead tr {
  background: linear-gradient(45deg, #2563eb, #38bdf8);
  color: white;
  border-radius: 10px;
}

th {
  padding: 14px !important;
  font-weight: 600;
}

tbody tr {
  transition: 0.2s;
}

tbody tr:hover {
  background: #f1f5ff;
}

/* STATUS */
.status-good {
  background: #dcfce7;
  color: #15803d;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

.status-bad {
  background: #fee2e2;
  color: #b91c1c;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 13px;
}

/* BUTTONS */
.btn-block {
  background: #fee2e2;
  color: #b91c1c;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  transition: 0.2s;
}

.btn-block:hover {
  background: #b91c1c;
  color: white;
}

.btn-unblock {
  background: #dcfce7;
  color: #15803d;
  border: none;
  padding: 8px 14px;
  border-radius: 8px;
  transition: 0.2s;
}

.btn-unblock:hover {
  background: #15803d;
  color: white;
}
</style>