<template>
  <div class="auth-page">
    <div class="auth-background">
      <div class="bg-gradient"></div>
      <div class="bg-pattern"></div>
    </div>
    
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <div class="logo">
            <svg width="48" height="48" viewBox="0 0 32 32" fill="none">
              <rect width="32" height="32" rx="8" fill="#6366F1"/>
              <path d="M8 16C8 11.5817 11.5817 8 16 8V8C20.4183 8 24 11.5817 24 16V16C24 20.4183 20.4183 24 16 24V24" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <circle cx="16" cy="16" r="4" fill="white"/>
            </svg>
          </div>
          <h1>Welcome back</h1>
          <p>Sign in to your account to continue</p>
        </div>

        <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
          <el-form-item prop="username">
            <el-input 
              v-model="form.username" 
              placeholder="Username or email"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input 
              v-model="form.password" 
              type="password"
              placeholder="Password"
              size="large"
              :prefix-icon="Lock"
              show-password
            />
          </el-form-item>

          <div class="form-options">
            <el-checkbox v-model="rememberMe">Remember me</el-checkbox>
            <a href="#" class="forgot-link">Forgot password?</a>
          </div>
          
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            native-type="submit"
            class="login-btn"
          >
            Sign In
          </el-button>
        </el-form>

        <div class="demo-section">
          <el-divider>Try without account</el-divider>
          <el-button size="large" class="demo-btn" @click="useDemo">
            <el-icon><Lightning /></el-icon>
            Use Demo Account
          </el-button>
        </div>

        <div class="auth-footer">
          <p>Don't have an account? <router-link to="/signup">Create one</router-link></p>
        </div>
      </div>

      <div class="auth-branding">
        <h2>Manage Your Odoo Instances</h2>
        <p>Powerful, scalable cloud hosting for African businesses. Deploy, monitor, and scale your Odoo ERP with ease.</p>
        <div class="features-list">
          <div class="feature">
            <el-icon><Check /></el-icon>
            <span>Instant Odoo Deployment</span>
          </div>
          <div class="feature">
            <el-icon><Check /></el-icon>
            <span>Automated Backups</span>
          </div>
          <div class="feature">
            <el-icon><Check /></el-icon>
            <span>24/7 Monitoring</span>
          </div>
          <div class="feature">
            <el-icon><Check /></el-icon>
            <span>SSL Certificates</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { User, Lock, Lightning, Check } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)
const rememberMe = ref(false)

const form = ref({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  
  try {
    await authStore.login(form.value.username, form.value.password)
    ElMessage.success('Welcome back!')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Invalid credentials')
  } finally {
    loading.value = false
  }
}

const useDemo = () => {
  form.value.username = 'demo'
  form.value.password = 'demo123'
  handleLogin()
}
</script>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

.auth-background {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.bg-gradient {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #6366F1 100%);
}

.bg-pattern {
  position: absolute;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

.auth-container {
  display: flex;
  width: 100%;
  max-width: 1000px;
  margin: 20px;
  position: relative;
  z-index: 1;
}

.auth-card {
  flex: 1;
  background: white;
  border-radius: 16px;
  padding: 48px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: inline-flex;
  margin-bottom: 24px;
}

.auth-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.auth-header p {
  color: #6B7280;
  font-size: 0.95rem;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.forgot-link {
  color: #6366F1;
  font-size: 0.875rem;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 1rem;
  font-weight: 600;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366F1 0%, #4F46E5 100%);
  border: none;
  transition: transform 0.2s, box-shadow 0.2s;
}

.login-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
}

.demo-section {
  margin-top: 24px;
}

.demo-btn {
  width: 100%;
  height: 48px;
  border-radius: 10px;
  border: 2px solid #E5E7EB;
  background: transparent;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  transition: all 0.2s;
}

.demo-btn:hover {
  border-color: #6366F1;
  color: #6366F1;
  background: rgba(99, 102, 241, 0.05);
}

.auth-footer {
  text-align: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #E5E7EB;
}

.auth-footer p {
  color: #6B7280;
  font-size: 0.875rem;
}

.auth-footer a {
  color: #6366F1;
  font-weight: 600;
  text-decoration: none;
}

.auth-footer a:hover {
  text-decoration: underline;
}

.auth-branding {
  flex: 1;
  padding: 48px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  color: white;
}

.auth-branding h2 {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 16px;
}

.auth-branding > p {
  font-size: 1.1rem;
  opacity: 0.9;
  line-height: 1.7;
  margin-bottom: 32px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.feature {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 1rem;
}

.feature .el-icon {
  width: 24px;
  height: 24px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .auth-container {
    flex-direction: column;
  }
  
  .auth-branding {
    display: none;
  }
  
  .auth-card {
    padding: 32px 24px;
  }
}
</style>
