<template>
  <div class="profile-page container-fluid">
    <div class="profile-inner">

      <!-- LOADING STATE -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else>
        <!-- ALERT FOR INCOMPLETE -->
        <div v-if="!isComplete" class="alert alert-warning d-flex justify-content-between align-items-center">
          <div>
            <i class="bi bi-exclamation-triangle-fill me-2"></i>
            <strong>Profile Incomplete.</strong> Please complete your profile to apply for placements.
          </div>
          <button class="btn btn-warning btn-sm" @click="enableEdit">
            Complete Now
          </button>
        </div>

        <!-- SUCCESS/ERROR MESSAGES -->
        <div v-if="successMessage" class="alert alert-success alert-dismissible fade show">
          {{ successMessage }}
          <button type="button" class="btn-close" @click="successMessage = ''"></button>
        </div>

        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show">
          {{ errorMessage }}
          <button type="button" class="btn-close" @click="errorMessage = ''"></button>
        </div>

        <!-- HEADER -->
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h3 class="fw-bold">My Profile</h3>
          <div>
            <button
              v-if="viewMode"
              class="btn btn-outline-primary"
              @click="enableEdit"
            >
              <i class="bi bi-pencil me-2"></i>Update Profile
            </button>
            <button
              v-else
              class="btn btn-outline-secondary me-2"
              @click="cancelEdit"
            >
              Cancel
            </button>
          </div>
        </div>

        <!-- FORM -->
        <form @submit.prevent="saveProfile">
          <div class="row g-3">

            <!-- Basic Information -->
            <div class="col-12">
              <h5 class="border-bottom pb-2 mb-3">Basic Information</h5>
            </div>

            <div class="col-md-6">
              <label class="form-label">Name <span class="text-danger">*</span></label>
              <input class="form-control" v-model="profile.name" disabled />
            </div>

            <div class="col-md-6">
              <label class="form-label">Email <span class="text-danger">*</span></label>
              <input class="form-control" v-model="profile.email" disabled />
            </div>

            <div class="col-md-6">
              <label class="form-label">Phone <span class="text-danger">*</span></label>
              <input
                type="tel"
                class="form-control"
                v-model="profile.phone"
                :disabled="viewMode"
                :class="{ 'is-invalid': errors.phone }"
                placeholder="Enter 10-digit phone number"
                maxlength="10"
              />
              <div v-if="errors.phone" class="invalid-feedback">
                {{ errors.phone }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Gender <span class="text-danger">*</span></label>
              <select
                class="form-select"
                v-model="profile.gender"
                :disabled="viewMode"
                :class="{ 'is-invalid': errors.gender }"
              >
                <option value="">Select Gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
              <div v-if="errors.gender" class="invalid-feedback">
                {{ errors.gender }}
              </div>
            </div>

            <!-- Academic Information -->
            <div class="col-12 mt-4">
              <h5 class="border-bottom pb-2 mb-3">Academic Information</h5>
            </div>

            <div class="col-md-4">
              <label class="form-label">Roll Number</label>
              <input
                class="form-control"
                v-model="profile.roll_number"
                :disabled="viewMode"
                placeholder="e.g., 2021CS001"
              />
            </div>

            <div class="col-md-4">
              <label class="form-label">Department/Branch <span class="text-danger">*</span></label>
              <select
                class="form-select"
                v-model="profile.department"
                :disabled="viewMode"
                :class="{ 'is-invalid': errors.department }"
              >
                <option value="">Select Department</option>
                <option value="Computer Science">Computer Science</option>
                <option value="Information Technology">Information Technology</option>
                <option value="Electronics">Electronics</option>
                <option value="Mechanical">Mechanical</option>
                <option value="Civil">Civil</option>
                <option value="Electrical">Electrical</option>
              </select>
              <div v-if="errors.department" class="invalid-feedback">
                {{ errors.department }}
              </div>
            </div>

            <div class="col-md-4">
              <label class="form-label">Graduation Year <span class="text-danger">*</span></label>
              <input
                type="number"
                class="form-control"
                v-model.number="profile.graduation_year"
                :disabled="viewMode"
                :class="{ 'is-invalid': errors.graduation_year }"
                :min="new Date().getFullYear()"
                :max="new Date().getFullYear() + 5"
                placeholder="e.g., 2025"
              />
              <div v-if="errors.graduation_year" class="invalid-feedback">
                {{ errors.graduation_year }}
              </div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Current CGPA/Percentage</label>
              <input
                type="number"
                step="0.01"
                class="form-control"
                v-model.number="profile.cgpa"
                :disabled="viewMode"
                placeholder="e.g., 8.5 or 85"
                min="0"
                max="10"
              />
            </div>

            <div class="col-md-6">
              <label class="form-label">Date of Birth</label>
              <input
                type="date"
                class="form-control"
                v-model="profile.date_of_birth"
                :disabled="viewMode"
              />
            </div>

            <!-- Additional Information -->
            <div class="col-12 mt-4">
              <h5 class="border-bottom pb-2 mb-3">Additional Information</h5>
            </div>

            <div class="col-12">
              <label class="form-label">Skills (comma-separated)</label>
              <input
                class="form-control"
                v-model="profile.skills"
                :disabled="viewMode"
                placeholder="e.g., JavaScript, Python, React, Node.js"
              />
            </div>

            <div class="col-12">
              <label class="form-label">Bio/About</label>
              <textarea
                class="form-control"
                v-model="profile.bio"
                :disabled="viewMode"
                rows="3"
                placeholder="Write a brief description about yourself..."
              ></textarea>
            </div>

          </div>

          <!-- SAVE BUTTON -->
          <div v-if="!viewMode" class="text-end mt-4">
            <button 
              type="submit" 
              class="btn btn-success px-4"
              :disabled="saving"
            >
              <span v-if="saving">
                <span class="spinner-border spinner-border-sm me-2"></span>
                Saving...
              </span>
              <span v-else>
                <i class="bi bi-check-circle me-2"></i>Save Changes
              </span>
            </button>
          </div>
        </form>
      </div>

    </div>
  </div>
</template>

<script>
import api from "@/utils/api";

export default {
  data() {
    return {
      profile: {
        name: '',
        email: '',
        phone: '',
        gender: '',
        graduation_year: null,
        roll_number: '',
        department: '',
        cgpa: null,
        date_of_birth: '',
        skills: '',
        bio: ''
      },
      originalProfile: {},
      viewMode: true,
      isComplete: true,
      loading: true,
      saving: false,
      successMessage: '',
      errorMessage: '',
      errors: {},
      id: JSON.parse(localStorage.getItem("user")).student_id
    };
  },

  async created() {
    await this.loadProfile();
  },

  methods: {
    async loadProfile() {
      try {
        this.loading = true;
        const res = await api.get(`/student/${this.id}`);
        this.profile = { ...this.profile, ...res.data };
        this.originalProfile = JSON.parse(JSON.stringify(this.profile));
        
        this.checkCompleteness();

        if (!this.isComplete) {
          this.viewMode = false;
        }
      } catch (error) {
        this.errorMessage = 'Failed to load profile. Please try again.';
        console.error('Error loading profile:', error);
      } finally {
        this.loading = false;
      }
    },

    enableEdit() {
      this.viewMode = false;
      this.errors = {};
      this.successMessage = '';
      this.errorMessage = '';
    },

    cancelEdit() {
      if (this.hasChanges()) {
        if (confirm('You have unsaved changes. Are you sure you want to cancel?')) {
          this.profile = JSON.parse(JSON.stringify(this.originalProfile));
          this.viewMode = true;
          this.errors = {};
        }
      } else {
        this.viewMode = true;
        this.errors = {};
      }
    },

    hasChanges() {
      return JSON.stringify(this.profile) !== JSON.stringify(this.originalProfile);
    },

    validateForm() {
      this.errors = {};
      
      // Phone validation
      if (!this.profile.phone) {
        this.errors.phone = 'Phone number is required';
      } else if (!/^[6-9]\d{9}$/.test(this.profile.phone)) {
        this.errors.phone = 'Please enter a valid 10-digit phone number';
      }

      // Gender validation
      if (!this.profile.gender) {
        this.errors.gender = 'Gender is required';
      }

      // Department validation
      if (!this.profile.department) {
        this.errors.department = 'Department is required';
      }

      // Graduation year validation
      if (!this.profile.graduation_year) {
        this.errors.graduation_year = 'Graduation year is required';
      } else if (this.profile.graduation_year < new Date().getFullYear()) {
        this.errors.graduation_year = 'Graduation year must be current year or later';
      }

      return Object.keys(this.errors).length === 0;
    },

    async saveProfile() {
      if (!this.validateForm()) {
        this.errorMessage = 'Please fix the errors before saving';
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }

      try {
        this.saving = true;
        this.errorMessage = '';
        
        await api.put(`/student/${this.id}`, this.profile);
        
        this.originalProfile = JSON.parse(JSON.stringify(this.profile));
        this.viewMode = true;
        this.checkCompleteness();
        this.successMessage = 'Profile updated successfully!';
        
        window.scrollTo({ top: 0, behavior: 'smooth' });
        
        // Clear success message after 3 seconds
        setTimeout(() => {
          this.successMessage = '';
        }, 3000);
        
      } catch (error) {
        this.errorMessage = error.response?.data?.message || 'Failed to save profile. Please try again.';
        console.error('Error saving profile:', error);
      } finally {
        this.saving = false;
      }
    },

    checkCompleteness() {
      this.isComplete =
        this.profile.phone &&
        this.profile.gender &&
        this.profile.graduation_year &&
        this.profile.department;
    }
  }
};
</script>

<style scoped>
.profile-inner {
  max-width: 1400px;
  margin: auto;
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

.form-label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.text-danger {
  color: #dc3545;
}

h5 {
  color: #495057;
  font-weight: 600;
}

.alert {
  border-radius: 8px;
}

@media (max-width: 768px) {
  .profile-inner {
    padding: 20px;
  }
}
</style>