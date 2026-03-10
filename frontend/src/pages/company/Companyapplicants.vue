<template>
  <div class="page-root">

    <!-- ── Global Toast ──────────────────────────────────────── -->
    <Transition name="fade">
      <div v-if="toast.show"
           class="toast-fixed alert d-flex align-items-center
                  gap-2 shadow-lg"
           :class="`alert-${toast.type}`">
        <i class="bi flex-shrink-0"
           :class="toast.type === 'success'
             ? 'bi-check-circle-fill'
             : 'bi-exclamation-triangle-fill'"></i>
        <span class="flex-grow-1 small fw-semibold">{{ toast.message }}</span>
        <button class="btn-close btn-close-sm"
                @click="toast.show = false"></button>
      </div>
    </Transition>

    <!-- ── Page loading / error ──────────────────────────────── -->
    <div v-if="pageLoading" class="d-flex align-items-center
         justify-content-center min-vh-100">
      <div class="text-center">
        <div class="spinner-border text-primary mb-3"></div>
        <p class="text-muted small">Loading applicants…</p>
      </div>
    </div>

    <div v-else-if="pageError" class="d-flex align-items-center
         justify-content-center min-vh-100">
      <div class="text-center">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ pageError }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>
    </div>

    <template v-else>

      <!-- ── Top header ─────────────────────────────────────── -->
      <div class="top-header px-4 py-3 bg-white border-bottom
                  d-flex align-items-center
                  justify-content-between gap-3 flex-wrap">
        <div class="d-flex align-items-center gap-3">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Drive
          </button>
          <div>
            <h5 class="fw-bold mb-0 lh-1">{{ drive?.title || '…' }}</h5>
            <small class="text-muted">
              <i class="bi bi-building me-1"></i>{{ store.companyName }}
            </small>
          </div>
          <button class="btn btn-success btn-sm" @click="exportCSV(drive.id)">
            <i class="bi bi-file-earmark-spreadsheet me-1"></i>
            Export CSV
          </button>
        </div>

        <!-- Pipeline chips -->
        <div class="d-flex gap-2 flex-wrap align-items-center">
          <button v-for="s in pipelineStats" :key="s.key"
                  class="chip-btn"
                  :class="activeFilter === s.key ? 'chip-active' : ''"
                  @click="setFilter(s.key)">
            <span class="fw-bold" :class="s.color">{{ s.value }}</span>
            <span class="chip-label">{{ s.label }}</span>
          </button>

          <button class="btn btn-outline-secondary btn-sm ms-2"
                  :disabled="store.loadingApps"
                  @click="loadApplicants(true)">
            <span v-if="store.loadingApps"
                  class="spinner-border spinner-border-sm"></span>
            <i v-else class="bi bi-arrow-clockwise"></i>
          </button>
        </div>
      </div>

      <!-- ── Master-Detail body ─────────────────────────────── -->
      <div class="master-detail">

        <!-- ════ LEFT — Applicant list ════ -->
        <div class="list-panel">

          <!-- Search + sort -->
          <div class="p-2 border-bottom bg-white sticky-top">
            <div class="input-group input-group-sm mb-2">
              <span class="input-group-text bg-white">
                <i class="bi bi-search text-muted"></i>
              </span>
              <input class="form-control border-start-0 ps-0"
                     v-model="search"
                     placeholder="Search name, branch…" />
              <button v-if="search"
                      class="btn btn-outline-secondary"
                      @click="search = ''">
                <i class="bi bi-x"></i>
              </button>
            </div>
            <div class="d-flex gap-2">
              <select class="form-select form-select-sm" v-model="activeFilter">
                <option value="">All</option>
                <option>Applied</option>
                <option>Shortlisted</option>
                <option>Selected</option>
                <option>Rejected</option>
              </select>
              <select class="form-select form-select-sm" v-model="sortBy">
                <option value="applied_date_desc">Newest</option>
                <option value="applied_date_asc">Oldest</option>
                <option value="cgpa_desc">CGPA ↓</option>
                <option value="name_asc">Name A–Z</option>
              </select>
            </div>
            <div class="mt-1 d-flex justify-content-between">
              <small class="text-muted">{{ filtered.length }} applicant(s)</small>
            </div>
          </div>

          <!-- Empty list -->
          <div v-if="!filtered.length"
               class="text-center py-5 px-3 text-muted">
            <i class="bi bi-people fs-1 d-block mb-2 opacity-25"></i>
            <small>{{ search || activeFilter
              ? 'No matches' : 'No applicants yet' }}</small>
          </div>

          <!-- Applicant rows -->
          <div v-else>
            <button v-for="app in filtered" :key="app.id"
                    class="applicant-row"
                    :class="{ 'row-active': selectedAppId === app.id }"
                    @click="selectApplicant(app)">

              <div class="row-avatar"
                   :class="avatarBg(app.status)">
                {{ initials(app.student_name) }}
              </div>

              <div class="row-info">
                <div class="d-flex align-items-center
                            justify-content-between gap-1 mb-1">
                  <span class="fw-semibold small text-truncate"
                        style="max-width:130px">
                    {{ app.student_name }}
                  </span>
                  <span class="badge flex-shrink-0"
                        style="font-size:.62rem"
                        :class="statusBadge(app.status)">
                    {{ app.status }}
                  </span>
                </div>
                <div class="d-flex align-items-center
                            justify-content-between">
                  <small class="text-muted text-truncate"
                         style="max-width:120px">
                    {{ app.student_branch || '—' }}
                  </small>
                  <small class="text-muted flex-shrink-0">
                    {{ app.student_cgpa ? `CGPA ${app.student_cgpa}` : '' }}
                  </small>
                </div>
                <div class="d-flex align-items-center
                            justify-content-between mt-1">
                  <small class="text-muted" style="font-size:.68rem">
                    {{ formatDate(app.applied_date) }}
                  </small>
                  <span v-if="store.getInterviewForApp(app.id)"
                        class="badge bg-info text-dark"
                        style="font-size:.6rem">
                    <i class="bi bi-calendar-check me-1"></i>IV
                  </span>
                </div>
              </div>

            </button>
          </div>
        </div>

        <!-- ════ RIGHT — Student profile + actions ════ -->
        <div class="detail-panel bg-light">

          <!-- Empty state -->
          <div v-if="!selectedAppId"
               class="h-100 d-flex flex-column align-items-center
                      justify-content-center text-center p-4">
            <div class="empty-illustration mb-4">
              <i class="bi bi-person-lines-fill"></i>
            </div>
            <h5 class="fw-bold text-muted mb-1">
              Select an applicant
            </h5>
            <p class="text-muted small mb-0">
              Click any row on the left to review their profile,
              manage their application, and take actions.
            </p>
          </div>

          <!-- Profile loading -->
          <div v-else-if="studentLoading"
               class="h-100 d-flex align-items-center
                      justify-content-center">
            <div class="text-center">
              <div class="spinner-border text-primary mb-2"></div>
              <p class="text-muted small">Loading profile…</p>
            </div>
          </div>

          <!-- Profile error -->
          <div v-else-if="studentError"
               class="h-100 d-flex align-items-center
                      justify-content-center p-4">
            <div class="text-center">
              <i class="bi bi-exclamation-circle text-danger fs-1 mb-3 d-block"></i>
              <p class="text-muted">{{ studentError }}</p>
              <button class="btn btn-outline-primary btn-sm"
                      @click="selectApplicant(selectedApp)">
                Retry
              </button>
            </div>
          </div>

          <!-- Profile loaded -->
          <div v-else-if="student" class="detail-scroll">

            <!-- ── Profile header strip ──────────────────── -->
            <div class="detail-header bg-white border-bottom p-4">
              <div class="d-flex align-items-center
                          justify-content-between flex-wrap gap-3">
                <div class="d-flex align-items-center gap-3">
                  <div class="profile-avatar">
                    {{ initials(student.name) }}
                  </div>
                  <div>
                    <h5 class="fw-bold mb-1">{{ student.name }}</h5>
                    <p class="text-muted small mb-2">
                      <i class="bi bi-envelope me-1"></i>{{ student.email }}
                      <span v-if="student.phone" class="ms-2">
                        <i class="bi bi-telephone me-1"></i>{{ student.phone }}
                      </span>
                    </p>
                    <div class="d-flex gap-1 flex-wrap mb-2">
                      <span v-if="student.branch"
                            class="badge bg-primary bg-opacity-10 text-primary">
                        {{ student.branch }}
                      </span>
                      <span v-if="student.cgpa"
                            class="badge bg-success bg-opacity-10 text-success">
                        CGPA {{ student.cgpa }}
                      </span>
                      <span v-if="student.graduation_year"
                            class="badge bg-info bg-opacity-10 text-info">
                        {{ student.graduation_year }}
                      </span>
                      <span v-if="student.degree"
                            class="badge bg-secondary bg-opacity-10 text-secondary">
                        {{ student.degree }}
                      </span>
                    </div>

                    <!-- Social links — always visible in header -->
                    <div class="d-flex gap-2 flex-wrap align-items-center">
                      <a v-if="student.linkedin_url"
                         :href="student.linkedin_url" target="_blank"
                         class="social-pill social-linkedin">
                        <i class="bi bi-linkedin me-1"></i>LinkedIn
                      </a>
                      <a v-if="student.github_url"
                         :href="student.github_url" target="_blank"
                         class="social-pill social-github">
                        <i class="bi bi-github me-1"></i>GitHub
                      </a>
                      <a v-if="student.portfolio_url"
                         :href="student.portfolio_url" target="_blank"
                         class="social-pill social-portfolio">
                        <i class="bi bi-globe2 me-1"></i>Portfolio
                      </a>
                      <span v-if="!student.linkedin_url && !student.github_url && !student.portfolio_url"
                            class="text-muted small fst-italic">
                        <i class="bi bi-link-45deg me-1"></i>No social links added
                      </span>
                    </div>
                  </div>
                </div>
                <span class="badge fs-6 px-3 py-2"
                      :class="statusBadge(selectedApp?.status)">
                  <i class="bi me-1"
                     :class="statusIcon(selectedApp?.status)"></i>
                  {{ selectedApp?.status }}
                </span>
              </div>

              <!-- Timeline -->
              <div v-if="selectedApp"
                   class="d-flex gap-3 flex-wrap mt-3 pt-3 border-top">
                <div v-if="selectedApp.applied_date" class="timeline-pill">
                  <small class="text-muted d-block">Applied</small>
                  <strong class="small">{{ formatDate(selectedApp.applied_date) }}</strong>
                </div>
                <div v-if="selectedApp.reviewed_date" class="timeline-pill">
                  <small class="text-muted d-block">Reviewed</small>
                  <strong class="small">{{ formatDate(selectedApp.reviewed_date) }}</strong>
                </div>
                <div v-if="interview?.interview_date" class="timeline-pill border-info">
                  <small class="text-muted d-block">Interview</small>
                  <strong class="small text-info">
                    {{ formatDate(interview.interview_date) }}
                  </strong>
                </div>
              </div>
            </div>

            <!-- ── Two-column body ───────────────────────── -->
            <div class="row g-0">

              <!-- Left body: profile info -->
              <div class="col-lg-7 p-4 d-flex flex-column gap-4">

                <!-- Academic details -->
                <div class="card border-0 shadow-sm">
                  <div class="card-body p-4">
                    <h6 class="section-label">Academic Details</h6>
                    <div class="row g-3">
                      <div class="col-6">
                        <div class="info-block">
                          <small class="text-muted d-block">Roll Number</small>
                          <strong>{{ student.roll_number || '—' }}</strong>
                        </div>
                      </div>
                      <div class="col-6">
                        <div class="info-block">
                          <small class="text-muted d-block">10th / 12th %</small>
                          <strong>
                            {{ student.tenth_percentage ?? '—' }} /
                            {{ student.twelfth_percentage ?? '—' }}
                          </strong>
                        </div>
                      </div>
                      <div v-if="student.college_name" class="col-12">
                        <div class="info-block">
                          <small class="text-muted d-block">College</small>
                          <strong>{{ student.college_name }}</strong>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Skills -->
                <div v-if="skillList.length" class="card border-0 shadow-sm">
                  <div class="card-body p-4">
                    <h6 class="section-label">Skills</h6>
                    <div class="d-flex flex-wrap gap-1">
                      <span v-for="s in skillList" :key="s"
                            class="badge bg-primary bg-opacity-10
                                   text-primary py-2 px-3">
                        {{ s }}
                      </span>
                    </div>
                    <template v-if="student.bio">
                      <h6 class="section-label mt-4">Bio</h6>
                      <p class="text-muted small mb-0"
                         style="white-space:pre-wrap">
                        {{ student.bio }}
                      </p>
                    </template>
                  </div>
                </div>

                <!-- Cover Letter -->
                <div v-if="selectedApp?.cover_letter"
                     class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-file-text me-2 text-primary"></i>
                      Cover Letter
                    </h6>
                  </div>
                  <div class="card-body">
                    <p class="text-muted small mb-0"
                       style="white-space:pre-wrap">
                      {{ selectedApp.cover_letter }}
                    </p>
                  </div>
                </div>

                <!-- Recruiter Notes (read-only) -->
                <div v-if="selectedApp?.notes"
                     class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3
                              d-flex align-items-center
                              justify-content-between">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-chat-left-text me-2 text-secondary"></i>
                      Recruiter Notes
                    </h6>
                    <button class="btn btn-outline-secondary btn-sm"
                            @click="openNotesModal">
                      <i class="bi bi-pencil"></i>
                    </button>
                  </div>
                  <div class="card-body">
                    <p class="text-muted small mb-0"
                       style="white-space:pre-wrap">
                      {{ selectedApp.notes }}
                    </p>
                  </div>
                </div>

              </div>

              <!-- Right body: actions + interview + resume -->
              <div class="col-lg-5 p-4 d-flex flex-column gap-3
                           border-start-lg">

                <!-- Actions card -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-lightning-charge me-2 text-warning"></i>
                      Actions
                    </h6>
                  </div>
                  <div class="card-body p-3 d-flex flex-column gap-2">

                    <!-- Move Forward -->
                    <p class="action-group-label">Move Forward</p>

                    <button v-if="selectedApp?.status === 'Applied'"
                            class="btn btn-info btn-sm text-white"
                            :disabled="actionPending"
                            @click="doShortlist">
                      <span v-if="actionPending"
                            class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-person-check me-1"></i>
                      Shortlist Candidate
                    </button>

                    <button v-if="['Applied','Shortlisted']
                                    .includes(selectedApp?.status)"
                            class="btn btn-outline-primary btn-sm"
                            :disabled="actionPending"
                            @click="openInterviewModal">
                      <i class="bi bi-calendar-event me-1"></i>
                      {{ interview ? 'Reschedule Interview' : 'Schedule Interview' }}
                    </button>

                    <button v-if="selectedApp?.status === 'Shortlisted'"
                            class="btn btn-success btn-sm"
                            :disabled="actionPending"
                            @click="openSelectionModal('Selected')">
                      <i class="bi bi-check-circle me-1"></i>
                      Mark as Selected
                    </button>

                    <button v-if="!['Rejected','Selected']
                                    .includes(selectedApp?.status)"
                            class="btn btn-outline-danger btn-sm"
                            :disabled="actionPending"
                            @click="openSelectionModal('Rejected')">
                      <i class="bi bi-x-circle me-1"></i>
                      Reject Applicant
                    </button>

                    <!-- Offer letter (Selected only) -->
                    <template v-if="selectedApp?.status === 'Selected'">
                      <button v-if="!hasOfferLetter"
                              class="btn btn-warning btn-sm"
                              @click="openOfferModal('edit')">
                        <i class="bi bi-file-earmark-text me-1"></i>
                        Generate Offer Letter
                      </button>
                      <template v-else>
                        <button class="btn btn-success btn-sm"
                                @click="openOfferModal('preview')">
                          <i class="bi bi-eye me-1"></i>View Offer Letter
                        </button>
                        <button class="btn btn-outline-warning btn-sm"
                                @click="openOfferModal('edit')">
                          <i class="bi bi-pencil me-1"></i>Edit &amp; Regenerate
                        </button>
                      </template>
                    </template>

                    <!-- Utilities -->
                    <p class="action-group-label mt-2">Utilities</p>
                    <button class="btn btn-outline-secondary btn-sm"
                            @click="openNotesModal">
                      <i class="bi bi-chat-left-text me-1"></i>
                      {{ selectedApp?.notes ? 'Edit Notes' : 'Add Internal Note' }}
                    </button>

                    <!-- Revert -->
                    <template v-if="['Shortlisted','Selected','Rejected']
                                      .includes(selectedApp?.status)">
                      <p class="action-group-label mt-2">Revert</p>
                      <button v-if="selectedApp?.status === 'Shortlisted'"
                              class="btn btn-sm btn-light border"
                              :disabled="actionPending"
                              @click="doUndo('Applied', 'Undo shortlist? Applicant returns to Applied.')">
                        <i class="bi bi-arrow-counterclockwise me-1 text-muted"></i>
                        <span class="text-muted">Undo Shortlist</span>
                      </button>
                      <button v-if="selectedApp?.status === 'Selected'"
                              class="btn btn-sm btn-light border"
                              :disabled="actionPending"
                              @click="doUndo('Shortlisted', 'Undo selection? Returns to Shortlisted.')">
                        <i class="bi bi-arrow-counterclockwise me-1 text-muted"></i>
                        <span class="text-muted">Undo Selection</span>
                      </button>
                      <button v-if="selectedApp?.status === 'Rejected'"
                              class="btn btn-sm btn-light border"
                              :disabled="actionPending"
                              @click="doUndo('Applied', 'Restore applicant to Applied?')">
                        <i class="bi bi-arrow-counterclockwise me-1 text-muted"></i>
                        <span class="text-muted">Restore to Applied</span>
                      </button>
                    </template>

                  </div>
                </div>

                <!-- Interview details -->
                <div v-if="interview"
                     class="card border-0 shadow-sm border-start
                            border-info border-3">
                  <div class="card-header bg-white border-bottom py-3
                              d-flex align-items-center
                              justify-content-between">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-calendar-check me-2 text-info"></i>
                      Interview
                    </h6>
                    <span class="badge bg-info text-dark">
                      {{ interview.interview_type }}
                    </span>
                  </div>
                  <div class="card-body p-3">
                    <ul class="list-unstyled mb-0 d-flex flex-column gap-2">
                      <li class="d-flex align-items-start gap-2">
                        <i class="bi bi-camera-video text-muted mt-1 flex-shrink-0"></i>
                        <div>
                          <small class="text-muted d-block">Mode</small>
                          <strong class="small">{{ interview.interview_mode }}</strong>
                        </div>
                      </li>
                      <li class="d-flex align-items-start gap-2">
                        <i class="bi bi-clock text-muted mt-1 flex-shrink-0"></i>
                        <div>
                          <small class="text-muted d-block">Date &amp; Time</small>
                          <strong class="small">
                            {{ formatDateTime(interview.interview_date) }}
                          </strong>
                        </div>
                      </li>
                      <li v-if="interview.interview_link"
                          class="d-flex align-items-start gap-2">
                        <i class="bi bi-link-45deg text-muted mt-1 flex-shrink-0"></i>
                        <div>
                          <small class="text-muted d-block">
                            {{ interview.interview_mode === 'Online'
                                ? 'Meeting Link' : 'Venue' }}
                          </small>
                          <a v-if="interview.interview_mode === 'Online'"
                             :href="interview.interview_link"
                             target="_blank" class="small text-primary text-break">
                            {{ interview.interview_link }}
                          </a>
                          <strong v-else class="small">
                            {{ interview.interview_link }}
                          </strong>
                        </div>
                      </li>
                      <li v-if="interview.interviewer"
                          class="d-flex align-items-start gap-2">
                        <i class="bi bi-person-badge text-muted mt-1 flex-shrink-0"></i>
                        <div>
                          <small class="text-muted d-block">Interviewer(s)</small>
                          <strong class="small">{{ interview.interviewer }}</strong>
                        </div>
                      </li>
                      <li v-if="interview.instructions"
                          class="d-flex align-items-start gap-2">
                        <i class="bi bi-info-circle text-muted mt-1 flex-shrink-0"></i>
                        <div>
                          <small class="text-muted d-block">Instructions</small>
                          <span class="small text-muted">
                            {{ interview.instructions }}
                          </span>
                        </div>
                      </li>
                    </ul>
                    <div class="mt-3 pt-3 border-top d-flex flex-column gap-2">

                      <!-- Completed state banner -->
                      <div v-if="interview.status === 'Completed'"
                           class="interview-done-banner">
                        <i class="bi bi-patch-check-fill me-2"></i>
                        Interview marked as completed
                      </div>

                      <!-- Mark as Completed -->
                      <button v-if="interview.status !== 'Completed'"
                              class="btn btn-sm btn-success w-100"
                              :disabled="actionPending"
                              @click="doCompleteInterview">
                        <span v-if="actionPending"
                              class="spinner-border spinner-border-sm me-1"></span>
                        <i v-else class="bi bi-patch-check me-1"></i>
                        Mark Interview as Completed
                      </button>

                      <div class="d-flex gap-2">
                        <button class="btn btn-sm btn-outline-primary flex-fill"
                                :disabled="actionPending"
                                @click="openInterviewModal">
                          <i class="bi bi-pencil me-1"></i>Reschedule
                        </button>
                        <button class="btn btn-sm btn-outline-danger flex-fill"
                                :disabled="actionPending"
                                @click="doRevokeInterview">
                          <i class="bi bi-calendar-x me-1"></i>Revoke
                        </button>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- Resume -->
                <div class="card border-0 shadow-sm">
                  <div class="card-header bg-white border-bottom py-3">
                    <h6 class="mb-0 fw-bold">
                      <i class="bi bi-file-earmark-pdf me-2 text-danger"></i>
                      Resume
                    </h6>
                  </div>
                  <div class="card-body d-grid gap-2 p-3">
                    <button v-if="student.resume_filename"
                            class="btn btn-primary btn-sm"
                            :disabled="resumeBusy"
                            @click="viewResume">
                      <span v-if="resumeBusy"
                            class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi bi-eye me-1"></i>
                      View / Download
                    </button>
                    <p v-else class="text-muted small mb-0">No resume uploaded.</p>
                  </div>
                </div>



              </div>
            </div>
          </div>

        </div>
      </div>
    </template>

    <!-- ══════════════════════════════════════════════════
         MODALS
    ══════════════════════════════════════════════════ -->

    <!-- Interview modal -->
    <div v-if="interviewModal.show"
         class="modal-backdrop-custom"
         @click.self="interviewModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom">
          <h6 class="fw-bold mb-0">
            <i class="bi bi-calendar-event me-2"></i>
            {{ interview ? 'Reschedule Interview' : 'Schedule Interview' }}
            — {{ student?.name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="interviewModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <div v-if="interview"
               class="alert alert-info d-flex align-items-center
                      gap-2 py-2 px-3 mb-3 small">
            <i class="bi bi-info-circle-fill flex-shrink-0"></i>
            Editing interview scheduled for
            <strong>{{ formatDateTime(interview.interview_date) }}</strong>.
          </div>
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Interview Type <span class="text-danger">*</span>
              </label>
              <select class="form-select form-select-sm"
                      v-model="interviewForm.interview_type">
                <option value="Technical">Technical</option>
                <option value="HR">HR</option>
                <option value="Managerial">Managerial</option>
              </select>
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Mode <span class="text-danger">*</span>
              </label>
              <select class="form-select form-select-sm"
                      v-model="interviewForm.interview_mode">
                <option value="Online">Online</option>
                <option value="Onsite">Onsite</option>
                <option value="Phone">Phone</option>
              </select>
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Date &amp; Time <span class="text-danger">*</span>
              </label>
              <input class="form-control form-control-sm"
                     type="datetime-local"
                     v-model="interviewForm.interview_date" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                {{ interviewForm.interview_mode === 'Online'
                    ? 'Meeting Link / URL' : 'Venue / Location' }}
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interview_link"
                     :placeholder="interviewForm.interview_mode === 'Online'
                       ? 'https://meet.google.com/…' : 'Room 101, Block A'" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Interviewer Name(s)
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interviewer"
                     placeholder="John Doe, Jane Smith" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Instructions
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.instructions"
                     placeholder="Join 5 min early, bring ID…" />
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="interviewModal.show = false">Cancel</button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="interviewModal.saving"
                  @click="submitInterview">
            <span v-if="interviewModal.saving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-calendar-check me-1"></i>
            {{ interview ? 'Update Interview' : 'Schedule' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Selection / Rejection modal -->
    <div v-if="selectionModal.show"
         class="modal-backdrop-custom"
         @click.self="selectionModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom"
             :class="selectionModal.status === 'Selected'
               ? 'bg-success' : 'bg-danger'">
          <h6 class="fw-bold mb-0 text-white">
            <i class="bi me-2"
               :class="selectionModal.status === 'Selected'
                 ? 'bi-check-circle' : 'bi-x-circle'"></i>
            {{ selectionModal.status === 'Selected'
                ? 'Finalise Selection' : 'Reject Applicant' }}
            — {{ student?.name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="selectionModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <div class="row g-3">
            <template v-if="selectionModal.status === 'Selected'">
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                  Offered Salary (INR)
                </label>
                <input class="form-control form-control-sm"
                      type="number" min="0"
                      v-model.number="selectionForm.salary"
                      placeholder="e.g. 800000" />
                <!-- Live Preview -->
                <small class="text-muted mt-1 d-block">
                  Preview: ₹ {{ formattedSalary }}
                </small>
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                  Joining Date
                </label>
                <input class="form-control form-control-sm"
                       type="date"
                       v-model="selectionForm.joining_date" />
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                   feedback
                </label>
                <input class="form-control form-control-sm"
                       type="text"
                       v-model="selectionForm.feedback" />
              </div>
            </template>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                {{ selectionModal.status === 'Rejected'
                    ? 'Rejection Feedback (optional)'
                    : 'Internal Notes (optional)' }}
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="selectionForm.notes" rows="3"
                        :placeholder="selectionModal.status === 'Rejected'
                          ? 'Did not meet technical requirements…'
                          : 'Internal notes…'">
              </textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="selectionModal.show = false">Cancel</button>
          <button class="btn btn-sm px-4"
                  :class="selectionModal.status === 'Selected'
                    ? 'btn-success' : 'btn-danger'"
                  :disabled="selectionModal.saving"
                  @click="submitSelection">
            <span v-if="selectionModal.saving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi me-1"
               :class="selectionModal.status === 'Selected'
                 ? 'bi-check-circle' : 'bi-x-circle'"></i>
            Confirm {{ selectionModal.status }}
          </button>
        </div>
      </div>
    </div>

    <!-- Notes modal -->
    <div v-if="notesModal.show"
         class="modal-backdrop-custom"
         @click.self="notesModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom">
          <h6 class="fw-bold mb-0">
            <i class="bi bi-chat-left-text me-2"></i>
            Internal Notes — {{ student?.name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="notesModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <p class="text-muted small mb-2">
            Notes are internal and not visible to the student.
          </p>
          <textarea class="form-control"
                    v-model="notesModal.text" rows="5"
                    placeholder="Internal recruiter notes…"></textarea>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="notesModal.show = false">Cancel</button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="notesModal.saving"
                  @click="saveNotes">
            <span v-if="notesModal.saving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-floppy me-1"></i>
            Save Notes
          </button>
        </div>
      </div>
    </div>

    <!-- Offer letter modal -->
    <div v-if="offerModal.show"
         class="modal-backdrop-custom"
         @click.self="offerModal.show = false">
      <div class="modal-card shadow-lg" style="max-width:700px">
        <div class="modal-header-custom" style="background:#198754">
          <h6 class="fw-bold mb-0 text-white">
            <i class="bi bi-file-earmark-text me-2"></i>
            Offer Letter —
            {{ offerModal.step === 1 ? 'Fill Details' : 'Preview & Save' }}
          </h6>
          <div class="d-flex align-items-center gap-2">
            <span class="badge"
                  :class="offerModal.step === 1
                    ? 'bg-white text-success' : 'bg-success-subtle text-white'">
              1 Details
            </span>
            <i class="bi bi-chevron-right text-white-50"></i>
            <span class="badge"
                  :class="offerModal.step === 2
                    ? 'bg-white text-success' : 'bg-success-subtle text-white'">
              2 Preview
            </span>
            <button class="btn-close btn-close-white ms-2"
                    @click="offerModal.show = false"></button>
          </div>
        </div>
        <div class="modal-body-custom">
          <!-- Step 1 -->
          <div v-if="offerModal.step === 1" class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Candidate Name</label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.studentName" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Role / Position</label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.role" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Company Name</label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.companyName" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Letter Date</label>
              <input class="form-control form-control-sm" type="date"
                     v-model="offerFields.letterDate" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Offered CTC (INR)</label>
              <input class="form-control form-control-sm" type="number" min="0"
                     v-model.number="offerFields.salary" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Joining Date</label>
              <input class="form-control form-control-sm" type="date"
                     v-model="offerFields.joiningDate" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Signatory Name</label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.hrName"
                     placeholder="Priya Sharma" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">Signatory Designation</label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.hrDesignation"
                     placeholder="HR Manager" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Additional Terms / Clauses
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="offerFields.extraClauses" rows="3"
                        placeholder="Offer subject to background verification…">
              </textarea>
            </div>
          </div>
          <!-- Step 2 preview -->
          <div v-else id="offer-print-area"
               class="offer-preview border rounded p-4">
            <div class="text-center mb-4">
              <h4 class="fw-bold mb-0 text-uppercase">
                {{ offerFields.companyName }}
              </h4>
              <p class="text-muted small mb-0">Offer of Employment</p>
              <hr class="my-3" />
            </div>
            <div class="d-flex justify-content-between flex-wrap mb-4">
              <div>
                <strong>To,</strong><br />
                {{ offerFields.studentName }}<br />
                <span class="text-muted small">{{ student?.email }}</span>
              </div>
              <div class="text-end">
                <small class="text-muted d-block">Date</small>
                <strong>{{ formatDate(offerFields.letterDate) }}</strong>
              </div>
            </div>
            <p class="mb-4">
              <strong>
                Sub: Offer of Employment — {{ offerFields.role }}
              </strong>
            </p>
            <p>Dear <strong>{{ offerFields.studentName }}</strong>,</p>
            <p>
              We are delighted to offer you the position of
              <strong>{{ offerFields.role }}</strong> at
              <strong>{{ offerFields.companyName }}</strong>.
              After careful evaluation, we are confident that you will be
              a valuable addition to our team.
            </p>
            <table class="table table-bordered table-sm my-4 small">
              <tbody>
                <tr>
                  <th class="bg-light" style="width:40%">Position</th>
                  <td>{{ offerFields.role }}</td>
                </tr>
                <tr>
                  <th class="bg-light">Annual CTC</th>
                  <td>
                    ₹ {{ Number(offerFields.salary || 0)
                          .toLocaleString('en-IN') }}
                  </td>
                </tr>
                <tr>
                  <th class="bg-light">Joining Date</th>
                  <td>{{ formatDate(offerFields.joiningDate) || '—' }}</td>
                </tr>
              </tbody>
            </table>
            <p>
              Kindly confirm your acceptance within
              <strong>7 working days</strong>.
              Failure to do so will render this offer null and void.
            </p>
            <template v-if="offerFields.extraClauses">
              <p class="fw-semibold mb-1">
                Additional Terms &amp; Conditions:
              </p>
              <p class="text-muted small" style="white-space:pre-wrap">
                {{ offerFields.extraClauses }}
              </p>
            </template>
            <div class="mt-5">
              <p class="mb-0">Yours sincerely,</p>
              <p class="mb-0 mt-4">
                <strong>{{ offerFields.hrName || 'HR Team' }}</strong><br />
                {{ offerFields.hrDesignation || 'HR Department' }}<br />
                <strong>{{ offerFields.companyName }}</strong>
              </p>
            </div>
            <div class="mt-5 pt-3 border-top text-center small text-muted">
              System-generated offer letter · {{ offerFields.companyName }}
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="offerModal.show = false">Close</button>
          <button v-if="offerModal.step === 2"
                  class="btn btn-outline-secondary btn-sm"
                  @click="offerModal.step = 1">
            <i class="bi bi-pencil me-1"></i>Edit
          </button>
          <button v-if="offerModal.step === 1"
                  class="btn btn-success btn-sm px-4"
                  @click="offerModal.step = 2">
            <i class="bi bi-eye me-1"></i>Preview
          </button>
          <button v-if="offerModal.step === 2"
                  class="btn btn-primary btn-sm px-4"
                  :disabled="offerSaving"
                  @click="saveOfferLetter">
            <span v-if="offerSaving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-cloud-upload me-1"></i>
            {{ offerSaving ? 'Saving…' : 'Save Offer Letter' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCompanyStore }     from '@/stores/companyStore'
import { useUserStore }        from '@/stores/userStore'

const router    = useRouter()
const route     = useRoute()
const store     = useCompanyStore()
const userStore = useUserStore()

const driveId = computed(() => parseInt(route.params.driveId))
const cid     = computed(() => userStore.companyId)
const apiBase  = import.meta.env.VITE_API_BASE_URL ?? ''

// ── Page-level state ──────────────────────────────────────────
const pageLoading = ref(true)
const pageError   = ref('')
const drive       = ref(null)

// ── List state ────────────────────────────────────────────────
const search       = ref('')
const activeFilter = ref('')
const sortBy       = ref('applied_date_desc')

// ── Selected applicant ────────────────────────────────────────
const selectedAppId  = ref(null)
const student        = ref(null)
const studentLoading = ref(false)
const studentError   = ref('')
const actionPending  = ref(false)
const resumeBusy     = ref(false)

// Offer letter persistence
const offerLetterSaved = ref(false)

const selectedApp = computed(() => {
  if (!selectedAppId.value) return null
  return (store.applicants[driveId.value] || [])
    .find(a => a.id === selectedAppId.value) ?? null
})

const interview = computed(() =>
  selectedAppId.value
    ? store.getInterviewForApp(selectedAppId.value)
    : null
)

const hasOfferLetter = computed(() =>
  offerLetterSaved.value ||
  !!selectedApp.value?.placement?.offer_letter_url
)


const skillList = computed(() =>
  (student.value?.skills || '').split(',')
    .map(s => s.trim()).filter(Boolean)
)

// ── Toast ─────────────────────────────────────────────────────
const toast = reactive({ show: false, type: 'success', message: '' })
function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

// ── Modal state ───────────────────────────────────────────────
const interviewModal = reactive({ show: false, saving: false })
const interviewForm  = reactive({
  interview_type: 'Technical', interview_mode: 'Online',
  interview_date: '', interview_link: '',
  interviewer: '', instructions: '',
})
const selectionModal = reactive({ show: false, saving: false, status: 'Selected' })
const selectionForm  = reactive({ salary: null, joining_date: '', notes: '' , feedback: ''})
const notesModal     = reactive({ show: false, saving: false, text: '' })
const offerModal     = reactive({ show: false, step: 1 })
const offerSaving    = ref(false)
const offerFields    = reactive({
  studentName: '', role: '', companyName: '',
  letterDate: new Date().toISOString().slice(0, 10),
  salary: null, joiningDate: '', hrName: '',
  hrDesignation: 'HR Manager', extraClauses: '',
})

// ── Filtered list ─────────────────────────────────────────────
const filtered = computed(() => {
  let list = [...(store.applicants[driveId.value] || [])]
  if (activeFilter.value)
    list = list.filter(a => a.status === activeFilter.value)
  if (search.value) {
    const q = search.value.toLowerCase()
    list = list.filter(a =>
      a.student_name?.toLowerCase().includes(q)   ||
      a.student_email?.toLowerCase().includes(q)  ||
      a.student_branch?.toLowerCase().includes(q) ||
      a.student_roll?.toLowerCase().includes(q)
    )
  }
  const sorters = {
    applied_date_desc: (a, b) => new Date(b.applied_date) - new Date(a.applied_date),
    applied_date_asc:  (a, b) => new Date(a.applied_date) - new Date(b.applied_date),
    cgpa_desc:  (a, b) => (b.student_cgpa ?? 0) - (a.student_cgpa ?? 0),
    name_asc:   (a, b) => (a.student_name ?? '').localeCompare(b.student_name ?? ''),
  }
  if (sorters[sortBy.value]) list.sort(sorters[sortBy.value])
  return list
})

const pipelineStats = computed(() => {
  const all   = store.applicants[driveId.value] || []
  const count = s => all.filter(a => a.status === s).length
  return [
    { key: '',            label: 'Total',       value: all.length,           color: 'text-dark'    },
    { key: 'Applied',     label: 'Applied',     value: count('Applied'),     color: 'text-primary' },
    { key: 'Shortlisted', label: 'Shortlisted', value: count('Shortlisted'), color: 'text-info'    },
    { key: 'Selected',    label: 'Selected',    value: count('Selected'),    color: 'text-success' },
  ]
})

const formattedSalary = computed(() => {
  const salary = selectionForm.salary
  if (!salary) return '-' // fallback if empty or 0
  // Format number in Indian notation
  return new Intl.NumberFormat('en-IN').format(salary)
})

// ── Load ──────────────────────────────────────────────────────
async function loadApplicants(force = false) {
  pageLoading.value = true
  pageError.value   = ''
  try {
    await store.fetchDrives(cid.value)
    drive.value = store.getDriveById(driveId.value)
    await store.fetchApplicants(cid.value, driveId.value, force)
  } catch (e) {
    pageError.value = e?.message ?? 'Failed to load applicants.'
  } finally {
    pageLoading.value = false
  }
}

// ── Select applicant ──────────────────────────────────────────
async function selectApplicant(app) {
  selectedAppId.value  = app.id
  student.value        = null
  studentLoading.value = true
  studentError.value   = ''
  offerLetterSaved.value = !!localStorage.getItem(`offer_letter_saved_${app.id}`)
  try {
    const results = await Promise.all([
      store.fetchStudentProfile(app.student_id),
      store.fetchInterviewForApplication(cid.value, app.id),
    ])
    student.value = results[0]
  } catch (e) {
    studentError.value = e?.message ?? 'Failed to load profile.'
  } finally {
    studentLoading.value = false
  }
}

function setFilter(key) {
  activeFilter.value = activeFilter.value === key ? '' : key
}

// ── Actions ───────────────────────────────────────────────────
async function doShortlist() {
  actionPending.value = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId.value, selectedAppId.value, 'Shortlisted'
    )
    showToast('success', `${student.value?.name} shortlisted.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally { actionPending.value = false }
}

async function doUndo(targetStatus, confirmMsg) {
  if (!confirm(confirmMsg)) return
  actionPending.value = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId.value, selectedAppId.value, targetStatus
    )
    showToast('success', `Reverted to ${targetStatus}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Revert failed.')
  } finally { actionPending.value = false }
}

async function doRevokeInterview() {
  if (!confirm('Revoke this interview?')) return
  actionPending.value = true
  try {
    await store.cancelInterview(cid.value, selectedAppId.value)
    showToast('success', 'Interview revoked.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to revoke.')
  } finally { actionPending.value = false }
}

async function doCompleteInterview() {
  if (!confirm('Mark this interview as completed?')) return
  actionPending.value = true
  try {
    await store.completeInterview(cid.value, selectedAppId.value, {
  status: "completed"
  })
    showToast('success', `Interview marked as completed for ${student.value?.name}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to mark as completed.')
  } finally { actionPending.value = false }
}

// ── Interview modal ───────────────────────────────────────────
function openInterviewModal() {
  const iv = interview.value
  Object.assign(interviewForm, {
    interview_type: iv?.interview_type ?? 'Technical',
    interview_mode: iv?.interview_mode ?? 'Online',
    interview_date: iv?.interview_date
      ? new Date(iv.interview_date).toISOString().slice(0, 16) : '',
    interview_link: iv?.interview_link ?? '',
    interviewer:    iv?.interviewer    ?? '',
    instructions:   iv?.instructions   ?? '',
  })
  interviewModal.show = true
}

async function submitInterview() {
  if (!interviewForm.interview_date) {
    showToast('danger', 'Interview date is required.'); return
  }
  interviewModal.saving = true
  try {
    const payload = {
      ...interviewForm,
      interview_date: new Date(interviewForm.interview_date).toISOString(),
    }
    const isReschedule = !!interview.value
    if (isReschedule) {
      await store.rescheduleInterview(cid.value, selectedAppId.value, payload)
    } else {
      await store.scheduleInterview(cid.value, selectedAppId.value, payload)
    }
    interviewModal.show = false
    showToast('success',
      `Interview ${isReschedule ? 'rescheduled' : 'scheduled'} for ${student.value?.name}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save interview.')
  } finally { interviewModal.saving = false }
}

// ── Selection modal ───────────────────────────────────────────
function openSelectionModal(status) {
  selectionModal.status      = status
  selectionForm.salary       = null
  selectionForm.joining_date = ''
  selectionForm.notes        = ''
  selectionForm.feedback     = ''
  selectionModal.show        = true
}

async function submitSelection() {
  selectionModal.saving = true
  try {
    const payload = {
      status: selectionModal.status,
      ...(selectionForm.notes        && { notes:       selectionForm.notes }),
      ...(selectionModal.status === 'Selected' && {
        ...(selectionForm.salary       && { salary:       selectionForm.salary }),
        ...(selectionForm.joining_date && { joining_date: selectionForm.joining_date }),
        ...(selectionForm.feedback     && { feedback:     selectionForm.feedback }),
      }),
    }
    await store.finalizeSelection(cid.value, selectedAppId.value, payload)
    selectionModal.show = false
    showToast('success',
      `${student.value?.name} marked as ${selectionModal.status.toLowerCase()}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally { selectionModal.saving = false }
}

// ── Notes modal ───────────────────────────────────────────────
function openNotesModal() {
  notesModal.text = selectedApp.value?.notes || ''
  notesModal.show = true
}
async function saveNotes() {
  notesModal.saving = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId.value, selectedAppId.value,
      selectedApp.value.status, notesModal.text
    )
    notesModal.show = false
    showToast('success', 'Notes saved.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save notes.')
  } finally { notesModal.saving = false }
}

// ── Offer letter ──────────────────────────────────────────────
function openOfferModal(mode = 'edit') {
  if (mode === 'edit') {
    const d = store.getDriveById(driveId.value)
    Object.assign(offerFields, {
      studentName:   student.value?.name || '',
      role:          d?.title || '',
      companyName:   store.companyName,
      letterDate:    new Date().toISOString().slice(0, 10),
      salary:        selectedApp.value?.placement?.salary ?? null,
      joiningDate:   selectedApp.value?.placement?.joining_date?.slice(0, 10) ?? '',
      hrName: '', hrDesignation: 'HR Manager', extraClauses: '',
    })
    offerModal.step = 1
  } else {
    offerModal.step = 2
  }
  offerModal.show = true
}

async function saveOfferLetter() {
  offerSaving.value = true
  try {
    const html2pdf  = (await import('html2pdf.js')).default
    const element   = document.getElementById('offer-print-area')
    if (!element) throw new Error('Preview element not found.')
    const pdfBlob = await html2pdf().set({
      margin: [10,15,10,15], filename: `offer-${selectedAppId.value}.pdf`,
      image: { type:'jpeg', quality:.98 },
      html2canvas: { scale:2, useCORS:true },
      jsPDF: { unit:'mm', format:'a4', orientation:'portrait' },
    }).from(element).output('blob')

    const fd = new FormData()
    fd.append('student_id',     String(student.value?.id ?? ''))
    fd.append('application_id', String(selectedAppId.value))
    fd.append('offer_letter',   pdfBlob, `offer-${selectedAppId.value}.pdf`)

    const res = await fetch(`${apiBase}/upload-offer`, {
      method: 'POST',
      headers: { 'Authentication-Token': localStorage.getItem('token') },
      body: fd,
    })
    if (!res.ok) {
      const b = await res.json().catch(() => ({}))
      throw new Error(b?.message ?? `Upload failed (${res.status})`)
    }
    const data = await res.json()

    // Patch in-memory record
    const appRecord = (store.applicants[driveId.value] || [])
      .find(a => a.id === selectedAppId.value)
    if (appRecord) {
      if (!appRecord.placement) appRecord.placement = {}
      appRecord.placement.offer_letter_filename = data.offer_letter_filename
      appRecord.placement.offer_letter_url      = data.offer_letter_url
    }
    localStorage.setItem(`offer_letter_saved_${selectedAppId.value}`, '1')
    offerLetterSaved.value = true
    offerModal.show = false
    showToast('success', 'Offer letter saved successfully.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save offer letter.')
  } finally { offerSaving.value = false }
}

// ── Resume ────────────────────────────────────────────────────
async function viewResume() {
  if (!student.value?.resume_filename) return
  resumeBusy.value = true
  try {
    const res = await fetch(
      `${apiBase}/uploads/resumes/${student.value.resume_filename}`,
      { headers: { 'Authentication-Token': localStorage.getItem('token') } }
    )
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
    const url = URL.createObjectURL(
      new Blob([await res.blob()], { type: 'application/pdf' })
    )
    window.open(url, '_blank')
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to load resume.')
  } finally { resumeBusy.value = false }
}
async function exportCSV(driveId) {
  try {
    await store.exportApplicationsCSV(driveId)
    showToast('success', 'CSV downloaded successfully.')
  } catch {
    showToast('danger', store.csvError || 'Export failed.')
  }
}
// ── Helpers ───────────────────────────────────────────────────
function initials(name) {
  return (name || '?').split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}
function formatDate(d) {
  return d ? new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  }) : '—'
}
function formatDateTime(d) {
  return d ? new Date(d).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  }) : '—'
}
function statusBadge(s) {
  return {
    Applied: 'bg-primary', Shortlisted: 'bg-info text-dark',
    Selected: 'bg-success', Rejected: 'bg-danger',
  }[s] ?? 'bg-secondary'
}
function statusIcon(s) {
  return {
    Applied: 'bi-send', Shortlisted: 'bi-person-check',
    Selected: 'bi-check-circle-fill', Rejected: 'bi-x-circle-fill',
  }[s] ?? 'bi-circle'
}
function avatarBg(s) {
  return {
    Applied: 'avatar-blue', Shortlisted: 'avatar-cyan',
    Selected: 'avatar-green', Rejected: 'avatar-red',
  }[s] ?? 'avatar-gray'
}

onMounted(() => loadApplicants())
</script>

<style scoped>
/* ── Layout ──────────────────────────────────────────────────── */
.page-root {
  display: flex;
  flex-direction: column;
  height: 120vh;
  overflow: hidden;
  background: #f4f6fb;
}
.top-header { flex-shrink: 0; }

.master-detail {
  display: flex;
  flex: 1;
  overflow: hidden;
}

/* ── Left list panel ────────────────────────────────────────── */
.list-panel {
  width: 300px;
  flex-shrink: 0;
  border-right: 1px solid #dee2e6;
  background: #fff;
  overflow-y: auto;
}

/* ── Right detail panel ─────────────────────────────────────── */
.detail-panel {
  flex: 1;
  overflow-y: auto;
}
.detail-scroll { min-height: 100%; }
.detail-header { position: sticky; top: 0; z-index: 10; }

/* ── Pipeline chips ─────────────────────────────────────────── */
.chip-btn {
  display: flex; flex-direction: column;
  align-items: center; gap: 1px;
  padding: .35rem .75rem;
  border: 1px solid #dee2e6;
  border-radius: 8px;
  background: #fff; cursor: pointer;
  transition: all .15s;
}
.chip-btn:hover { border-color: #0d6efd; background: #f0f5ff; }
.chip-active    { border-color: #0d6efd !important; background: #e8f0fe !important; }
.chip-label     { font-size: .65rem; color: #6c757d; }

/* ── Applicant rows ─────────────────────────────────────────── */
.applicant-row {
  display: flex;
  align-items: flex-start;
  gap: .75rem;
  width: 100%;
  text-align: left;
  padding: .75rem 1rem;
  border: none;
  border-bottom: 1px solid #f0f0f0;
  background: transparent;
  cursor: pointer;
  transition: background .12s;
}
.applicant-row:hover  { background: #f8f9fa; }
.row-active {
  background: #eff5ff !important;
  border-left: 3px solid #0d6efd;
  padding-left: calc(1rem - 3px);
}
.row-info { flex: 1; min-width: 0; }

/* Avatars */
.row-avatar {
  width: 38px; height: 38px;
  border-radius: 50%; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  font-size: .75rem; font-weight: 700; color: #fff;
}
.avatar-blue  { background: linear-gradient(135deg, #0d6efd, #0a58ca); }
.avatar-cyan  { background: linear-gradient(135deg, #0dcaf0, #0aa2c0); }
.avatar-green { background: linear-gradient(135deg, #198754, #146c43); }
.avatar-red   { background: linear-gradient(135deg, #dc3545, #b02a37); }
.avatar-gray  { background: linear-gradient(135deg, #6c757d, #495057); }

/* ── Profile avatar ─────────────────────────────────────────── */
.profile-avatar {
  width: 64px; height: 64px; border-radius: 50%; flex-shrink: 0;
  background: linear-gradient(135deg, #0d6efd, #6610f2);
  color: #fff; display: flex; align-items: center;
  justify-content: center; font-size: 1.4rem; font-weight: 700;
}

/* ── Empty state illustration ───────────────────────────────── */
.empty-illustration {
  width: 80px; height: 80px; border-radius: 50%;
  background: #e9ecef;
  display: flex; align-items: center; justify-content: center;
  font-size: 2rem; color: #adb5bd;
}

/* ── Info blocks ────────────────────────────────────────────── */
.info-block {
  padding: .75rem; background: #f8f9fa;
  border-radius: 8px; height: 100%;
}
.timeline-pill {
  padding: .4rem .75rem;
  background: #f8f9fa; border-radius: 8px;
}
.section-label {
  font-size: .7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  color: #6c757d; padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
.action-group-label {
  font-size: .65rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .07em;
  color: #6c757d; margin-bottom: 0;
}

/* ── Right body column border on large screens ──────────────── */
@media (min-width: 992px) {
  .border-start-lg { border-left: 1px solid #dee2e6; }
}

/* ── Toast ──────────────────────────────────────────────────── */
.toast-fixed {
  position: fixed; top: 1rem; right: 1rem;
  z-index: 2000; min-width: 280px;
  border-radius: 10px;
}

/* ── Modals ─────────────────────────────────────────────────── */
.modal-backdrop-custom {
  position: fixed; inset: 0; z-index: 1050;
  background: rgba(0,0,0,.5);
  display: flex; align-items: center;
  justify-content: center; padding: 1rem;
}
.modal-card {
  background: #fff; border-radius: 14px;
  width: 100%; max-width: 540px;
  max-height: 92vh; overflow-y: auto;
}
.modal-header-custom {
  background: #0d6efd; color: #fff;
  padding: 1rem 1.25rem;
  border-radius: 14px 14px 0 0;
  display: flex; align-items: center;
  justify-content: space-between;
  position: sticky; top: 0; z-index: 1;
}
.modal-body-custom  { padding: 1.25rem; }
.modal-footer-custom {
  padding: .75rem 1.25rem;
  border-top: 1px solid #dee2e6;
  display: flex; justify-content: flex-end; gap: .5rem;
  position: sticky; bottom: 0; background: #fff; z-index: 1;
}

/* ── Offer preview ──────────────────────────────────────────── */
.offer-preview {
  font-family: 'Georgia', serif;
  font-size: .92rem; line-height: 1.9; background: #fff;
}

/* ── Responsive: stack on mobile ───────────────────────────── */
@media (max-width: 768px) {
  .page-root   { height: auto; overflow: auto; }
  .master-detail { flex-direction: column; overflow: visible; }
  .list-panel  { width: 100%; border-right: none; border-bottom: 1px solid #dee2e6; }
  .detail-panel { overflow: visible; }
}

/* ── Social pills ───────────────────────────────────────────── */
.social-pill {
  display: inline-flex; align-items: center;
  padding: .28rem .75rem; border-radius: 20px;
  font-size: .75rem; font-weight: 600;
  text-decoration: none; transition: all .15s;
  border: 1.5px solid transparent;
}
.social-linkedin {
  background: #e8f0fe; color: #0a66c2;
  border-color: #c5d8f8;
}
.social-linkedin:hover {
  background: #0a66c2; color: #fff;
}
.social-github {
  background: #f0f0f0; color: #24292e;
  border-color: #d0d0d0;
}
.social-github:hover {
  background: #24292e; color: #fff;
}
.social-portfolio {
  background: #e8f5e9; color: #2e7d32;
  border-color: #c8e6c9;
}
.social-portfolio:hover {
  background: #2e7d32; color: #fff;
}

/* ── Interview completed banner ─────────────────────────────── */
.interview-done-banner {
  background: #d1fae5; color: #065f46;
  border: 1px solid #6ee7b7;
  border-radius: 8px; padding: .5rem .75rem;
  font-size: .8rem; font-weight: 600;
  display: flex; align-items: center;
}

/* ── Fade transition ────────────────────────────────────────── */
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }
</style>