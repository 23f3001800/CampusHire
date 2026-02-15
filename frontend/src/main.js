import { createApp } from 'vue'
import { createPinia } from 'pinia'
import router from './router'
import App from './App.vue'

import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const app   = createApp(App)
const pinia = createPinia()

app.use(pinia)
app.use(router)

// Make router available to axios interceptor for redirects
window.$router = router

app.mount('#app')
