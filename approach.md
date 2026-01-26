User enters email/password
 ↓
Login.vue calls userStore.loginWithCredentials()
 ↓
api.js sends POST /api/auth/login
 ↓
Flask verifies credentials
 ↓
Flask returns token + user info
 ↓
Pinia stores token + user
 ↓
api.js uses token automatically
 ↓
User is authenticated



Frontend Workflow (Big Picture)

Vue Page
  ↓
Pinia Store
  ↓
api.js (Axios)
  ↓
Flask Backend
  ↓
Response
  ↓
Store updates state
  ↓
Vue auto re-renders


userStore → WHO am I?
studentStore → WHAT can student do?
companyStore → WHAT can company do?
adminStore → WHO controls system?