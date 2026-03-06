<template>
  <div class="bg-light min-vh-100 py-4">
    <div class="container" style="max-width:900px">

      <!-- Loading -->
      <div v-if="loading" class="text-center py-5">
        <div class="spinner-border text-primary"></div>
        <p class="text-muted mt-3">Loading student profile…</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="text-center py-5">
        <i class="bi bi-exclamation-circle text-danger"
           style="font-size:3rem"></i>
        <h5 class="mt-3 text-muted">{{ error }}</h5>
        <button class="btn btn-outline-primary mt-3"
                @click="router.back()">
          <i class="bi bi-arrow-left me-1"></i>Go Back
        </button>
      </div>

      <template v-else-if="student">

        <!-- Toast -->
        <Transition name="fade">
          <div v-if="toast.show"
               class="toast-banner alert d-flex
                      align-items-center gap-2 shadow mb-3"
               :class="`alert-${toast.type}`" role="alert">
            <i class="bi flex-shrink-0 fs-5"
               :class="toast.type === 'success'
                 ? 'bi-check-circle-fill'
                 : 'bi-exclamation-triangle-fill'"></i>
            <span class="flex-grow-1 fw-semibold">
              {{ toast.message }}
            </span>
            <button class="btn-close"
                    @click="toast.show = false"></button>
          </div>
        </Transition>

        <!-- Page header -->
        <div class="d-flex align-items-center
                    justify-content-between mb-4 flex-wrap gap-2">
          <button class="btn btn-outline-secondary btn-sm"
                  @click="router.back()">
            <i class="bi bi-arrow-left me-1"></i>Back to Applicants
          </button>
          <!-- Status pill in header -->
          <span v-if="application"
                class="badge fs-6 px-3 py-2"
                :class="statusBadgeClass(application.status)">
            <i class="bi me-1"
               :class="statusIcon(application.status)"></i>
            {{ application.status }}
          </span>
        </div>

        <div class="row g-4">

          <!-- ════════════ LEFT ════════════ -->
          <div class="col-lg-8 d-flex flex-column gap-4">

            <!-- Identity card -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <div class="d-flex align-items-center gap-3 mb-4">
                  <div class="student-avatar">
                    {{ initials(student.name) }}
                  </div>
                  <div class="flex-grow-1">
                    <h4 class="fw-bold mb-1">
                      {{ student.name || '—' }}
                    </h4>
                    <p class="mb-1 text-muted small">
                      <i class="bi bi-envelope me-1"></i>
                      {{ student.email || '—' }}
                    </p>
                    <div class="d-flex gap-2 mt-2 flex-wrap">
                      <span v-if="student.branch"
                            class="badge bg-primary
                                   bg-opacity-10 text-primary">
                        <i class="bi bi-diagram-3 me-1"></i>
                        {{ student.branch }}
                      </span>
                      <span v-if="student.cgpa"
                            class="badge bg-success
                                   bg-opacity-10 text-success">
                        <i class="bi bi-award me-1"></i>
                        CGPA {{ student.cgpa }}
                      </span>
                      <span v-if="student.graduation_year"
                            class="badge bg-info
                                   bg-opacity-10 text-info">
                        <i class="bi bi-calendar me-1"></i>
                        {{ student.graduation_year }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Application timeline row -->
                <div v-if="application"
                     class="d-flex gap-3 flex-wrap
                            border-top pt-3 mt-2">
                  <div v-if="application.applied_date"
                       class="timeline-item">
                    <small class="text-muted d-block">Applied</small>
                    <strong class="small">
                      {{ formatDate(application.applied_date) }}
                    </strong>
                  </div>
                  <div v-if="application.reviewed_date"
                       class="timeline-item">
                    <small class="text-muted d-block">Reviewed</small>
                    <strong class="small">
                      {{ formatDate(application.reviewed_date) }}
                    </strong>
                  </div>
                  <div v-if="interview?.interview_date"
                       class="timeline-item">
                    <small class="text-muted d-block">Interview</small>
                    <strong class="small text-info">
                      {{ formatDate(interview.interview_date) }}
                    </strong>
                  </div>
                </div>

                <div class="row g-3 mt-1">
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">
                        Roll Number
                      </small>
                      <strong>
                        {{ student.roll_number || '—' }}
                      </strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Phone</small>
                      <strong>{{ student.phone || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">Degree</small>
                      <strong>{{ student.degree || '—' }}</strong>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="info-block">
                      <small class="text-muted d-block">
                        10th / 12th %
                      </small>
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

            <!-- Skills & Bio -->
            <div class="card border-0 shadow-sm">
              <div class="card-body p-4">
                <template v-if="skillList.length">
                  <h6 class="section-label">Skills</h6>
                  <div class="d-flex flex-wrap gap-1 mb-4">
                    <span v-for="s in skillList" :key="s"
                          class="badge bg-primary
                                 bg-opacity-10 text-primary
                                 py-2 px-3">
                      {{ s }}
                    </span>
                  </div>
                </template>
                <template v-if="student.bio">
                  <h6 class="section-label">Bio</h6>
                  <p class="text-muted small mb-0"
                     style="white-space:pre-wrap">
                    {{ student.bio }}
                  </p>
                </template>
                <template v-if="student.experience_required">
                  <h6 class="section-label mt-4">Experience</h6>
                  <p class="text-muted small mb-0">
                    {{ student.experience_required }}
                  </p>
                </template>
              </div>
            </div>

            <!-- Cover letter -->
            <div v-if="application?.cover_letter"
                 class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-file-text me-2
                             text-primary"></i>Cover Letter
                </h6>
              </div>
              <div class="card-body">
                <p class="text-muted small mb-0"
                   style="white-space:pre-wrap">
                  {{ application.cover_letter }}
                </p>
              </div>
            </div>

          </div>

          <!-- ════════════ RIGHT ════════════ -->
          <div class="col-lg-4 d-flex flex-column gap-3">

            <!-- ── Actions card ── -->
            <div v-if="application" class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-lightning-charge me-2
                             text-warning"></i>Actions
                </h6>
              </div>
              <div class="card-body p-3">

                <!-- Group: Forward actions -->
                <p class="text-uppercase text-muted mb-2"
                   style="font-size:.65rem;letter-spacing:.07em;
                          font-weight:700">
                  Move Forward
                </p>
                <div class="d-grid gap-2 mb-3">

                  <button
                    v-if="application.status === 'Applied'"
                    class="btn btn-info btn-sm text-white"
                    :disabled="actionPending"
                    @click="doShortlist">
                    <span v-if="actionPending"
                          class="spinner-border
                                 spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-person-check me-1"></i>
                    Shortlist Candidate
                  </button>

                  <button
                    v-if="['Applied','Shortlisted']
                            .includes(application.status)"
                    class="btn btn-outline-primary btn-sm"
                    :disabled="actionPending"
                    @click="openInterviewModal">
                    <i class="bi bi-calendar-event me-1"></i>
                    {{ interview ? 'Reschedule Interview'
                                 : 'Schedule Interview' }}
                  </button>

                  <button
                    v-if="application.status === 'Shortlisted'"
                    class="btn btn-success btn-sm"
                    :disabled="actionPending"
                    @click="openSelectionModal('Selected')">
                    <i class="bi bi-check-circle me-1"></i>
                    Mark as Selected
                  </button>

                  <button
                    v-if="!['Rejected','Selected']
                             .includes(application.status)"
                    class="btn btn-outline-danger btn-sm"
                    :disabled="actionPending"
                    @click="openSelectionModal('Rejected')">
                    <i class="bi bi-x-circle me-1"></i>
                    Reject Applicant
                  </button>

                  <!-- ── Offer Letter buttons ──
                       Show Generate only when letter has never been saved.
                       Once saved (this session OR url exists from backend),
                       show View + Edit & Regenerate instead. -->
                  <template v-if="application.status === 'Selected'">

                    <!-- Not yet generated -->
                    <button
                      v-if="!offerLetterSaved &&
                            !application?.placement?.offer_letter_url"
                      class="btn btn-warning btn-sm"
                      @click="openOfferModal('edit')">
                      <i class="bi bi-file-earmark-text me-1"></i>
                      Generate Offer Letter
                    </button>

                    <!-- Already generated -->
                    <template v-else>
                      <button
                        class="btn btn-success btn-sm"
                        @click="openOfferModal('preview')">
                        <i class="bi bi-eye me-1"></i>
                        View Offer Letter
                      </button>
                      <button
                        class="btn btn-outline-warning btn-sm"
                        @click="openOfferModal('edit')">
                        <i class="bi bi-pencil me-1"></i>
                        Edit &amp; Regenerate
                      </button>
                    </template>

                  </template>

                </div>

                <!-- Group: Utility -->
                <p class="text-uppercase text-muted mb-2"
                   style="font-size:.65rem;letter-spacing:.07em;
                          font-weight:700">
                  Utilities
                </p>
                <div class="d-grid gap-2 mb-3">
                  <button
                    class="btn btn-outline-secondary btn-sm"
                    :disabled="actionPending"
                    @click="openNotesModal">
                    <i class="bi bi-chat-left-text me-1"></i>
                    {{ application.notes ? 'Edit Notes'
                                         : 'Add Internal Note' }}
                  </button>
                </div>

                <!-- Group: Undo / Revert -->
                <template v-if="['Shortlisted','Selected','Rejected']
                                  .includes(application.status)">
                  <p class="text-uppercase text-muted mb-2"
                     style="font-size:.65rem;letter-spacing:.07em;
                            font-weight:700">
                    Revert
                  </p>
                  <div class="d-grid gap-2">

                    <button
                      v-if="application.status === 'Shortlisted'"
                      class="btn btn-sm btn-light border"
                      :disabled="actionPending"
                      @click="doUndo(
                        'Applied',
                        'Move back to Applied? Shortlist will be undone.'
                      )">
                      <i class="bi bi-arrow-counterclockwise me-1
                                 text-muted"></i>
                      <span class="text-muted">Undo Shortlist</span>
                    </button>

                    <button
                      v-if="application.status === 'Selected'"
                      class="btn btn-sm btn-light border"
                      :disabled="actionPending"
                      @click="doUndo(
                        'Shortlisted',
                        'Undo selection? Student returns to Shortlisted.'
                      )">
                      <i class="bi bi-arrow-counterclockwise me-1
                                 text-muted"></i>
                      <span class="text-muted">Undo Selection</span>
                    </button>

                    <button
                      v-if="application.status === 'Rejected'"
                      class="btn btn-sm btn-light border"
                      :disabled="actionPending"
                      @click="doUndo(
                        'Applied',
                        'Restore applicant back to Applied?'
                      )">
                      <i class="bi bi-arrow-counterclockwise me-1
                                 text-muted"></i>
                      <span class="text-muted">Restore to Applied</span>
                    </button>

                  </div>
                </template>

              </div>
            </div>

            <!-- ── Interview Details card ── -->
            <div v-if="interview" class="card border-0 shadow-sm
                                         border-start border-info
                                         border-3">
              <div class="card-header bg-white border-bottom py-3
                          d-flex align-items-center
                          justify-content-between">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-calendar-check me-2
                             text-info"></i>Scheduled Interview
                </h6>
                <span class="badge bg-info text-dark">
                  {{ interview.interview_type }}
                </span>
              </div>
              <div class="card-body p-3">
                <ul class="list-unstyled mb-0 d-flex
                           flex-column gap-2">

                  <li class="d-flex align-items-start gap-2">
                    <i class="bi bi-camera-video text-muted
                               mt-1 flex-shrink-0"></i>
                    <div>
                      <small class="text-muted d-block">Mode</small>
                      <strong class="small">
                        {{ interview.interview_mode }}
                      </strong>
                    </div>
                  </li>

                  <li class="d-flex align-items-start gap-2">
                    <i class="bi bi-clock text-muted
                               mt-1 flex-shrink-0"></i>
                    <div>
                      <small class="text-muted d-block">
                        Date & Time
                      </small>
                      <strong class="small">
                        {{
                          formatDateTime(interview.interview_date)
                        }}
                      </strong>
                    </div>
                  </li>

                  <li v-if="interview.interview_link"
                      class="d-flex align-items-start gap-2">
                    <i class="bi bi-link-45deg text-muted
                               mt-1 flex-shrink-0"></i>
                    <div>
                      <small class="text-muted d-block">
                        {{
                          interview.interview_mode === 'Online'
                            ? 'Meeting Link'
                            : 'Venue'
                        }}
                      </small>
                      <a v-if="interview.interview_mode === 'Online'"
                         :href="interview.interview_link"
                         target="_blank"
                         class="small text-primary
                                text-break">
                        {{ interview.interview_link }}
                      </a>
                      <strong v-else class="small">
                        {{ interview.interview_link }}
                      </strong>
                    </div>
                  </li>

                  <li v-if="interview.interviewer"
                      class="d-flex align-items-start gap-2">
                    <i class="bi bi-person-badge text-muted
                               mt-1 flex-shrink-0"></i>
                    <div>
                      <small class="text-muted d-block">
                        Interviewer(s)
                      </small>
                      <strong class="small">
                        {{ interview.interviewer }}
                      </strong>
                    </div>
                  </li>

                  <li v-if="interview.instructions"
                      class="d-flex align-items-start gap-2">
                    <i class="bi bi-info-circle text-muted
                               mt-1 flex-shrink-0"></i>
                    <div>
                      <small class="text-muted d-block">
                        Instructions
                      </small>
                      <span class="small text-muted">
                        {{ interview.instructions }}
                      </span>
                    </div>
                  </li>

                </ul>

                <!-- Revoke interview -->
                <div class="mt-3 pt-3 border-top">
                  <button
                    class="btn btn-sm btn-outline-danger w-100"
                    :disabled="actionPending"
                    @click="doRevokeInterview">
                    <span v-if="actionPending"
                          class="spinner-border
                                 spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-calendar-x me-1"></i>
                    Revoke Interview
                  </button>
                </div>
              </div>
            </div>

            <!-- Resume card -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-file-earmark-pdf me-2
                             text-danger"></i>Resume
                </h6>
              </div>
              <div class="card-body d-grid gap-2">
                <template v-if="student.resume_filename">
                  <button class="btn btn-primary btn-sm"
                          :disabled="resumeDownloadBusy"
                          @click="viewResume">
                    <span v-if="resumeDownloadBusy"
                          class="spinner-border spinner-border-sm me-1"></span>
                    <i v-else class="bi bi-eye me-1"></i>View / Download Resume
                  </button>
                </template>
                <p v-else class="text-muted small mb-0">No resume uploaded.</p>
              </div>
            </div>

            <!-- Links -->
            <div class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-link-45deg me-2
                             text-info"></i>Links
                </h6>
              </div>
              <div class="card-body">
                <div class="d-flex flex-column gap-2">
                  <a v-if="student.linkedin_url"
                     :href="student.linkedin_url"
                     target="_blank"
                     class="btn btn-outline-primary btn-sm">
                    <i class="bi bi-linkedin me-1"></i>LinkedIn
                  </a>
                  <a v-if="student.github_url"
                     :href="student.github_url"
                     target="_blank"
                     class="btn btn-outline-dark btn-sm">
                    <i class="bi bi-github me-1"></i>GitHub
                  </a>
                  <a v-if="student.portfolio_url"
                     :href="student.portfolio_url"
                     target="_blank"
                     class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-globe2 me-1"></i>Portfolio
                  </a>
                  <p v-if="!student.linkedin_url &&
                            !student.github_url &&
                            !student.portfolio_url"
                     class="text-muted small mb-0">
                    No links added.
                  </p>
                </div>
              </div>
            </div>

            <!-- Recruiter Notes (read-only preview) -->
            <div v-if="application?.notes"
                 class="card border-0 shadow-sm">
              <div class="card-header bg-white border-bottom py-3
                          d-flex align-items-center
                          justify-content-between">
                <h6 class="mb-0 fw-bold">
                  <i class="bi bi-chat-left-text me-2
                             text-secondary"></i>
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
                  {{ application.notes }}
                </p>
              </div>
            </div>

          </div>
        </div>
      </template>
    </div>

    <!-- ══════════════════════════════════════════
         INTERVIEW MODAL
    ══════════════════════════════════════════ -->
    <div v-if="interviewModal.show"
         class="modal-backdrop-custom"
         @click.self="interviewModal.show = false">
      <div class="modal-card shadow-lg">
        <div class="modal-header-custom">
          <h6 class="fw-bold mb-0">
            <i class="bi bi-calendar-event me-2"></i>
            Schedule Interview — {{ student?.name }}
          </h6>
          <button class="btn-close btn-close-white"
                  @click="interviewModal.show = false"></button>
        </div>
        <div class="modal-body-custom">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Interview Type
                <span class="text-danger">*</span>
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
                Date & Time <span class="text-danger">*</span>
              </label>
              <input class="form-control form-control-sm"
                     type="datetime-local"
                     v-model="interviewForm.interview_date" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                {{
                  interviewForm.interview_mode === 'Online'
                    ? 'Meeting Link / URL'
                    : 'Venue / Location'
                }}
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interview_link"
                     :placeholder="interviewForm.interview_mode === 'Online'
                       ? 'https://meet.google.com/…'
                       : 'Room 101, Block A'" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Interviewer Name(s)
              </label>
              <input class="form-control form-control-sm"
                     v-model="interviewForm.interviewer"
                     placeholder="John Doe, Jane Smith" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Instructions for Candidate
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="interviewForm.instructions"
                        rows="2"
                        placeholder="Bring ID proof, join 5 min early…">
              </textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="interviewModal.show = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="interviewModal.saving"
                  @click="submitInterview">
            <span v-if="interviewModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            <i v-else class="bi bi-calendar-check me-1"></i>
            Schedule
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════
         SELECTION / REJECTION MODAL
    ══════════════════════════════════════════ -->
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
                ? 'Finalise Selection'
                : 'Reject Applicant' }}
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
              </div>
              <div class="col-md-6">
                <label class="form-label fw-semibold small">
                  Joining Date
                </label>
                <input class="form-control form-control-sm"
                       type="date"
                       v-model="selectionForm.joining_date" />
              </div>
            </template>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                {{
                  selectionModal.status === 'Rejected'
                    ? 'Rejection Feedback (optional)'
                    : 'Internal Notes (optional)'
                }}
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="selectionForm.notes"
                        rows="3"
                        :placeholder="selectionModal.status === 'Rejected'
                          ? 'e.g. Did not meet technical requirements…'
                          : 'Internal notes…'">
              </textarea>
            </div>
          </div>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="selectionModal.show = false">
            Cancel
          </button>
          <button class="btn btn-sm px-4"
                  :class="selectionModal.status === 'Selected'
                    ? 'btn-success' : 'btn-danger'"
                  :disabled="selectionModal.saving"
                  @click="submitSelection">
            <span v-if="selectionModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            <i v-else class="bi me-1"
               :class="selectionModal.status === 'Selected'
                 ? 'bi-check-circle' : 'bi-x-circle'"></i>
            Confirm {{ selectionModal.status }}
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════
         NOTES MODAL
    ══════════════════════════════════════════ -->
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
                    v-model="notesModal.text"
                    rows="5"
                    placeholder="Internal recruiter notes…">
          </textarea>
        </div>
        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="notesModal.show = false">
            Cancel
          </button>
          <button class="btn btn-primary btn-sm px-4"
                  :disabled="notesModal.saving"
                  @click="saveNotes">
            <span v-if="notesModal.saving"
                  class="spinner-border
                         spinner-border-sm me-1"></span>
            <i v-else class="bi bi-floppy me-1"></i>
            Save Notes
          </button>
        </div>
      </div>
    </div>

    <!-- ══════════════════════════════════════════
         OFFER LETTER MODAL (2-step)
    ══════════════════════════════════════════ -->
    <div v-if="offerModal.show"
         class="modal-backdrop-custom"
         @click.self="offerModal.show = false">
      <div class="modal-card shadow-lg" style="max-width:700px">

        <div class="modal-header-custom"
             style="background:#198754">
          <h6 class="fw-bold mb-0 text-white">
            <i class="bi bi-file-earmark-text me-2"></i>
            Offer Letter —
            {{ offerModal.step === 1
                ? 'Fill Details'
                : 'Preview & Save' }}
          </h6>
          <div class="d-flex align-items-center gap-2">
            <span class="badge"
                  :class="offerModal.step === 1
                    ? 'bg-white text-success'
                    : 'bg-success-subtle text-white'">
              1 Details
            </span>
            <i class="bi bi-chevron-right text-white-50"></i>
            <span class="badge"
                  :class="offerModal.step === 2
                    ? 'bg-white text-success'
                    : 'bg-success-subtle text-white'">
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
              <label class="form-label fw-semibold small">
                Candidate Name
              </label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.studentName" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Role / Position
              </label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.role" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Company Name
              </label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.companyName" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Letter Date
              </label>
              <input class="form-control form-control-sm"
                     type="date"
                     v-model="offerFields.letterDate" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Offered CTC (INR)
              </label>
              <input class="form-control form-control-sm"
                     type="number" min="0"
                     v-model.number="offerFields.salary" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Joining Date
              </label>
              <input class="form-control form-control-sm"
                     type="date"
                     v-model="offerFields.joiningDate" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Signatory Name
              </label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.hrName"
                     placeholder="e.g. Priya Sharma" />
            </div>
            <div class="col-md-6">
              <label class="form-label fw-semibold small">
                Signatory Designation
              </label>
              <input class="form-control form-control-sm"
                     v-model="offerFields.hrDesignation"
                     placeholder="e.g. HR Manager" />
            </div>
            <div class="col-12">
              <label class="form-label fw-semibold small">
                Additional Terms / Clauses
              </label>
              <textarea class="form-control form-control-sm"
                        v-model="offerFields.extraClauses"
                        rows="3"
                        placeholder="e.g. Offer subject to background verification…">
              </textarea>
            </div>
          </div>

          <!-- Step 2 — Print preview -->
          <div v-else
               id="offer-print-area"
               class="offer-preview border rounded p-4">
            <div class="text-center mb-4">
              <h4 class="fw-bold mb-0 text-uppercase
                          letter-spacing-1">
                {{ offerFields.companyName }}
              </h4>
              <p class="text-muted small mb-0">
                Offer of Employment
              </p>
              <hr class="my-3" />
            </div>

            <div class="d-flex justify-content-between
                        flex-wrap mb-4">
              <div>
                <strong>To,</strong><br />
                {{ offerFields.studentName }}<br />
                <span class="text-muted small">
                  {{ student?.email }}
                </span>
              </div>
              <div class="text-end">
                <small class="text-muted d-block">Date</small>
                <strong>
                  {{ formatDate(offerFields.letterDate) }}
                </strong>
              </div>
            </div>

            <p class="mb-4">
              <strong>
                Sub: Offer of Employment —
                {{ offerFields.role }}
              </strong>
            </p>

            <p>Dear <strong>{{ offerFields.studentName }}</strong>,</p>

            <p>
              We are delighted to offer you the position of
              <strong>{{ offerFields.role }}</strong> at
              <strong>{{ offerFields.companyName }}</strong>.
              After careful evaluation of your qualifications
              and interview performance, we are confident that
              you will be a valuable addition to our team.
            </p>

            <table class="table table-bordered table-sm
                           my-4 small">
              <tbody>
                <tr>
                  <th class="bg-light" style="width:40%">
                    Position
                  </th>
                  <td>{{ offerFields.role }}</td>
                </tr>
                <tr>
                  <th class="bg-light">Annual CTC</th>
                  <td>
                    ₹ {{
                      Number(offerFields.salary || 0)
                        .toLocaleString('en-IN')
                    }}
                  </td>
                </tr>
                <tr>
                  <th class="bg-light">Joining Date</th>
                  <td>
                    {{
                      formatDate(offerFields.joiningDate) || '—'
                    }}
                  </td>
                </tr>
              </tbody>
            </table>

            <p>
              Kindly confirm your acceptance by signing and
              returning a copy of this letter within
              <strong>7 working days</strong> from the date of
              this offer. Failure to do so will render this
              offer null and void.
            </p>

            <template v-if="offerFields.extraClauses">
              <p class="fw-semibold mb-1">
                Additional Terms &amp; Conditions:
              </p>
              <p class="text-muted small"
                 style="white-space:pre-wrap">
                {{ offerFields.extraClauses }}
              </p>
            </template>

            <div class="mt-5">
              <p class="mb-0">Yours sincerely,</p>
              <p class="mb-0 mt-4">
                <strong>
                  {{ offerFields.hrName || 'HR Team' }}
                </strong><br />
                {{ offerFields.hrDesignation || 'HR Department' }}<br />
                <strong>{{ offerFields.companyName }}</strong>
              </p>
            </div>

            <div class="mt-5 pt-3 border-top text-center
                        small text-muted">
              This is a system-generated offer letter.
              {{ offerFields.companyName }}
            </div>
          </div>

        </div>

        <div class="modal-footer-custom">
          <button class="btn btn-secondary btn-sm"
                  @click="offerModal.show = false">
            Close
          </button>

          <!-- Step 2: back to edit -->
          <button v-if="offerModal.step === 2"
                  class="btn btn-outline-secondary btn-sm"
                  :disabled="offerModal_saving"
                  @click="offerModal.step = 1">
            <i class="bi bi-pencil me-1"></i>Edit
          </button>

          <!-- Step 1: go to preview -->
          <button v-if="offerModal.step === 1"
                  class="btn btn-success btn-sm px-4"
                  @click="offerModal.step = 2">
            <i class="bi bi-eye me-1"></i>Preview Letter
          </button>

          <!-- Step 2: Save only — captures HTML → PDF Blob → uploads to backend -->
          <button v-if="offerModal.step === 2"
                  class="btn btn-primary btn-sm px-4"
                  :disabled="offerModal_saving"
                  @click="saveOfferLetter">
            <span v-if="offerModal_saving"
                  class="spinner-border spinner-border-sm me-1"></span>
            <i v-else class="bi bi-cloud-upload me-1"></i>
            {{ offerModal_saving ? 'Saving…' : 'Save Offer Letter' }}
          </button>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter, useRoute }  from 'vue-router'
import { useCompanyStore }      from '@/stores/companyStore'
import { useUserStore }         from '@/stores/userStore'

const router    = useRouter()
const route     = useRoute()
const store     = useCompanyStore()
const userStore = useUserStore()

// ── Route params ──────────────────────────────────────────────
const studentId = route.params.studentId

const driveId = route.query.driveId
  ? parseInt(route.query.driveId) : null
const applicationId = route.query.applicationId
  ? parseInt(route.query.applicationId) : null

const cid = computed(() => userStore.companyId)

// ── State ─────────────────────────────────────────────────────
const student           = ref(null)
const loading           = ref(true)
const error             = ref('')
const actionPending     = ref(false)
const offerLetterSaved  = ref(false)   // flips true after successful upload this session

const toast = reactive({ show: false, type: 'success', message: '' })

// ── Modal state ───────────────────────────────────────────────
const interviewModal = reactive({ show: false, saving: false })
const interviewForm  = reactive({
  interview_type: 'Technical', interview_mode: 'Online',
  interview_date: '', interview_link: '',
  interviewer: '', instructions: '',
})

const selectionModal = reactive({
  show: false, saving: false, status: 'Selected',
})
const selectionForm = reactive({
  salary: null, joining_date: '', notes: '',
})

const notesModal = reactive({ show: false, saving: false, text: '' })

const offerModal      = reactive({ show: false, step: 1 })
const offerModal_saving = ref(false)
const offerFields     = reactive({
  studentName: '', role: '', companyName: '',
  letterDate:  new Date().toISOString().slice(0, 10),
  salary: null, joiningDate: '',
  hrName: '', hrDesignation: 'HR Manager', extraClauses: '',
})

// ── Computed ──────────────────────────────────────────────────
const application = computed(() => {
  if (!driveId || !applicationId) return null
  return (store.applicants[driveId] || [])
    .find(a => a.id === applicationId) || null
})

const interview = computed(() =>
  applicationId ? store.getInterviewForApp(applicationId) : null
)

const skillList = computed(() =>
  (student.value?.skills || '')
    .split(',').map(s => s.trim()).filter(Boolean)
)

// ── Load ──────────────────────────────────────────────────────
async function loadStudent() {
  loading.value = true
  error.value   = ''
  try {
    const fetches = [store.fetchStudentProfile(studentId)]
    if (driveId) fetches.push(store.fetchApplicants(cid.value, driveId))
    ;[student.value] = await Promise.all(fetches)

    if (applicationId) {
      await store.fetchInterviewForApplication(cid.value, applicationId)
    }
  } catch (e) {
    error.value = e?.message ?? 'Student not found or access denied.'
  } finally {
    loading.value = false
  }
}

// ── Action: Shortlist ─────────────────────────────────────────
async function doShortlist() {
  actionPending.value = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId, applicationId, 'Shortlisted'
    )
    showToast('success', `${student.value?.name} shortlisted.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally {
    actionPending.value = false
  }
}

// ── Action: Undo / Revert ─────────────────────────────────────
async function doUndo(targetStatus, confirmMsg) {
  if (!confirm(confirmMsg)) return
  actionPending.value = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId, applicationId, targetStatus
    )
    showToast('success', `Reverted to ${targetStatus}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Revert failed.')
  } finally {
    actionPending.value = false
  }
}

// ── Action: Revoke interview ──────────────────────────────────
async function doRevokeInterview() {
  if (!confirm(
    'Revoke this interview? The candidate will need to be re-scheduled.'
  )) return
  actionPending.value = true
  try {
    await store.cancelInterview(cid.value, applicationId)
    showToast('success', 'Interview revoked successfully.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to revoke interview.')
  } finally {
    actionPending.value = false
  }
}

// ── Interview modal ───────────────────────────────────────────
function openInterviewModal() {
  const iv = interview.value
  Object.assign(interviewForm, {
    interview_type: iv?.interview_type ?? 'Technical',
    interview_mode: iv?.interview_mode ?? 'Online',
    interview_date: '',
    interview_link: iv?.interview_link ?? '',
    interviewer:    iv?.interviewer    ?? '',
    instructions:   iv?.instructions   ?? '',
  })
  interviewModal.show = true
}

async function submitInterview() {
  if (!interviewForm.interview_date) {
    showToast('danger', 'Interview date is required.')
    return
  }
  interviewModal.saving = true
  try {
    await store.scheduleInterview(cid.value, applicationId, {
      ...interviewForm,
      interview_date: new Date(
        interviewForm.interview_date
      ).toISOString(),
    })
    interviewModal.show = false
    showToast('success',
      `Interview scheduled for ${student.value?.name}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to schedule interview.')
  } finally {
    interviewModal.saving = false
  }
}

// ── Selection modal ───────────────────────────────────────────
function openSelectionModal(status) {
  selectionModal.status      = status
  selectionForm.salary       = null
  selectionForm.joining_date = ''
  selectionForm.notes        = ''
  selectionModal.show        = true
}

async function submitSelection() {
  selectionModal.saving = true
  try {
    const payload = {
      status: selectionModal.status,
      ...(selectionForm.notes && { notes: selectionForm.notes }),
      ...(selectionModal.status === 'Selected' && {
        ...(selectionForm.salary &&
          { salary: selectionForm.salary }),
        ...(selectionForm.joining_date &&
          { joining_date: selectionForm.joining_date }),
      }),
    }
    await store.finalizeSelection(cid.value, applicationId, payload)
    selectionModal.show = false
    showToast('success',
      `${student.value?.name} marked as ` +
      `${selectionModal.status.toLowerCase()}.`)
  } catch (e) {
    showToast('danger', e?.message ?? 'Action failed.')
  } finally {
    selectionModal.saving = false
  }
}

// ── Notes modal ───────────────────────────────────────────────
function openNotesModal() {
  notesModal.text = application.value?.notes || ''
  notesModal.show = true
}

async function saveNotes() {
  notesModal.saving = true
  try {
    await store.updateApplicationStatus(
      cid.value, driveId, applicationId,
      application.value.status,
      notesModal.text
    )
    notesModal.show = false
    showToast('success', 'Notes saved.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save notes.')
  } finally {
    notesModal.saving = false
  }
}

// ── Offer letter modal ────────────────────────────────────────
// mode: 'edit' → open at Step 1 (form)
// mode: 'preview' → open at Step 2 (read-only preview of current fields)
function openOfferModal(mode = 'edit') {
  // Pre-fill fields only when opening in edit mode (or first time)
  if (mode === 'edit') {
    const app   = application.value
    const drive = store.getDriveById(driveId)
    Object.assign(offerFields, {
      studentName:   student.value?.name || '',
      role:          drive?.title || drive?.role || '',
      companyName:   store.companyName,
      letterDate:    new Date().toISOString().slice(0, 10),
      salary:        app?.placement?.salary ?? null,
      joiningDate:   app?.placement?.joining_date
                       ? app.placement.joining_date.slice(0, 10) : '',
      hrName:        '',
      hrDesignation: 'HR Manager',
      extraClauses:  '',
    })
    offerModal.step = 1
  } else {
    // preview: jump straight to Step 2 — fields already populated from last save
    offerModal.step = 2
  }
  offerModal.show = true
}

// ── Save offer letter: html2pdf → Blob → FormData → POST /upload-offer ───────
async function saveOfferLetter() {
  offerModal_saving.value = true
  try {
    // Dynamically import html2pdf.js (must be installed: npm i html2pdf.js)
    const html2pdf = (await import('html2pdf.js')).default

    const element = document.getElementById('offer-print-area')
    if (!element) throw new Error('Offer letter preview element not found.')

    const opt = {
      margin:      [10, 15, 10, 15],   // mm: top, right, bottom, left
      filename:    `offer-letter-${studentId}.pdf`,
      image:       { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2, useCORS: true },
      jsPDF:       { unit: 'mm', format: 'a4', orientation: 'portrait' },
    }

    // Capture the exact HTML preview the recruiter sees → PDF Blob
    const pdfBlob = await html2pdf()
      .set(opt)
      .from(element)
      .output('blob')

    // Build FormData matching the backend endpoint
    const formData = new FormData()
    formData.append('student_id',    String(studentId))
    formData.append('application_id', String(applicationId))
    formData.append(
      'offer_letter',
      pdfBlob,
      `offer-letter-${studentId}.pdf`
    )

    const token = localStorage.getItem('token')
    const base  = import.meta.env.VITE_API_BASE_URL ?? ''

    const res = await fetch(`${base}/upload-offer`, {
      method:  'POST',
      headers: { 'Authentication-Token': token },
      body:    formData,
    })

    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body?.message ?? `Upload failed (${res.status})`)
    }

    const data = await res.json()

    // Patch the in-memory applicant record so button state survives without refresh
    const appRecord = (store.applicants[driveId] || [])
      .find(a => a.id === applicationId)
    if (appRecord) {
      if (!appRecord.placement) appRecord.placement = {}
      appRecord.placement.offer_letter_filename = data.offer_letter_filename
      appRecord.placement.offer_letter_url      = data.offer_letter_url
    }

    // Mark as generated this session → buttons switch to View / Edit
    offerLetterSaved.value = true
    offerModal.show        = false
    showToast('success', 'Offer letter saved successfully.')
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to save offer letter.')
  } finally {
    offerModal_saving.value = false
  }
}

// ── View / Download Resume (opens in new tab) ─────────────────────────────────
// FIX: revokeObjectURL was called immediately after click, before the browser
//      could render the blob. Now we open in a new tab and revoke after 60 s.
const resumeDownloadBusy = ref(false)
async function viewResume() {
  if (!student.value?.resume_filename) return
  resumeDownloadBusy.value = true
  try {
    const token    = localStorage.getItem('token')
    const base     = import.meta.env.VITE_API_BASE_URL ?? ''
    const filename = student.value.resume_filename
    const res = await fetch(`${base}/api/uploads/resumes/${filename}`, {
      headers: { 'Authentication-Token': token },
    })
    if (!res.ok) throw new Error(`Download failed (${res.status})`)
    const blob = await res.blob()

    // Create a blob URL with the correct MIME type so browsers render PDFs inline
    const pdfBlob = new Blob([blob], { type: 'application/pdf' })
    const url     = URL.createObjectURL(pdfBlob)

    // Open in new tab — browser will render the PDF natively
    window.open(url, '_blank')

    // Revoke after 60 s to free memory (browser has already loaded it by then)
    setTimeout(() => URL.revokeObjectURL(url), 60_000)
  } catch (e) {
    showToast('danger', e?.message ?? 'Failed to load resume.')
  } finally {
    resumeDownloadBusy.value = false
  }
}

// ── Helpers ───────────────────────────────────────────────────
function showToast(type, message, ms = 4000) {
  toast.show = true; toast.type = type; toast.message = message
  setTimeout(() => { toast.show = false }, ms)
}

function formatDate(d) {
  if (!d) return '—'
  return new Date(d).toLocaleDateString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
  })
}

function formatDateTime(d) {
  if (!d) return '—'
  return new Date(d).toLocaleString('en-IN', {
    day: 'numeric', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function initials(name) {
  return (name || '?')
    .split(' ').map(w => w[0]).join('').slice(0, 2).toUpperCase()
}

function statusBadgeClass(status) {
  return {
    Applied:     'bg-primary',
    Shortlisted: 'bg-info text-dark',
    Selected:    'bg-success',
    Rejected:    'bg-danger',
  }[status] ?? 'bg-secondary'
}

function statusIcon(status) {
  return {
    Applied:     'bi-send',
    Shortlisted: 'bi-person-check',
    Selected:    'bi-check-circle-fill',
    Rejected:    'bi-x-circle-fill',
  }[status] ?? 'bi-circle'
}

onMounted(loadStudent)
</script>

<style scoped>
.student-avatar {
  width: 68px; height: 68px; border-radius: 50%;
  background: linear-gradient(135deg, #0d6efd, #6610f2);
  color: #fff; display: flex; align-items: center;
  justify-content: center;
  font-size: 1.5rem; font-weight: 700; flex-shrink: 0;
}
.info-block {
  padding: .75rem; background: #f8f9fa;
  border-radius: 8px; height: 100%;
}
.timeline-item {
  padding: .4rem .75rem;
  background: #f8f9fa; border-radius: 8px;
}
.section-label {
  font-size: .7rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: .08em;
  color: #6c757d; padding-bottom: .5rem;
  border-bottom: 1px solid #dee2e6; margin-bottom: 1rem;
}
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
  position: sticky; bottom: 0;
  background: #fff; z-index: 1;
}
.offer-preview {
  font-family: 'Georgia', serif;
  font-size: .92rem; line-height: 1.9;
  background: #fff;
}
.toast-banner {
  border-radius: 10px;
}
.letter-spacing-1 { letter-spacing: .05em; }
.fade-enter-active, .fade-leave-active { transition: opacity .3s; }
.fade-enter-from,  .fade-leave-to      { opacity: 0; }
</style>