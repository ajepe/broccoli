import { defineStore } from 'pinia'
import axios from 'axios'

const API_URL = '/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('access_token') || null,
    user: null
  }),
  
  getters: {
    isAuthenticated: (state) => !!state.token
  },
  
  actions: {
    async login(username, password) {
      const formData = new FormData()
      formData.append('username', username)
      formData.append('password', password)
      
      const response = await axios.post(`${API_URL}/auth/login`, formData)
      
      this.token = response.data.access_token
      localStorage.setItem('access_token', this.token)
      
      return true
    },
    
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },
    
    setUser(user) {
      this.user = user
    }
  }
})

export const api = axios.create({
  baseURL: API_URL
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
