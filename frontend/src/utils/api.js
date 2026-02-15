import axios from 'axios'

const BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api'

const http = axios.create({ baseURL: BASE, timeout: 30000 })

// ── Request: inject token ─────────────────────────────────────────────────────
http.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers['Authentication-Token'] = token
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']   // let browser set multipart boundary
  }
  return config
})

// ── Response: unwrap data, handle errors globally ─────────────────────────────
http.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response) {
      const { status, data } = err.response

      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        if (window.$router) window.$router.push('/login')
        else window.location.href = '/login'
      }

      const message = data?.message || data?.error || `HTTP ${status}`
      const error   = new Error(message)
      error.status  = status
      error.errors  = data?.errors || {}
      return Promise.reject(error)
    }
    return Promise.reject(new Error('Network error. Check your connection.'))
  }
)

// ── Public API ────────────────────────────────────────────────────────────────
const api = {
  get:    (url, cfg = {})       => http.get(url, cfg),
  post:   (url, data, cfg = {}) => http.post(url, data, cfg),
  put:    (url, data, cfg = {}) => http.put(url, data, cfg),
  patch:  (url, data, cfg = {}) => http.patch(url, data, cfg),
  delete: (url, cfg = {})       => http.delete(url, cfg),

  upload(url, files, extra = {}) {
    const fd = new FormData()
    if (files instanceof File) {
      fd.append('file', files)
    } else {
      Object.entries(files).forEach(([k, v]) => fd.append(k, v))
    }
    Object.entries(extra).forEach(([k, v]) =>
      fd.append(k, typeof v === 'object' ? JSON.stringify(v) : v)
    )
    return http.post(url, fd)
  },

  async download(url, filename) {
    const data = await http.get(url, { responseType: 'blob' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(new Blob([data]))
    a.download = filename
    a.click()
    URL.revokeObjectURL(a.href)
  },
}

export default api