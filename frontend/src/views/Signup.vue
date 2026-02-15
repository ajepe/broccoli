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
          <h1>Create an account</h1>
          <p>Get started with Odoo Cloud Africa</p>
        </div>

        <el-steps :active="currentStep" finish-status="success" class="steps">
          <el-step title="Account" />
          <el-step title="Plan" />
          <el-step title="Configure" />
        </el-steps>

        <el-form ref="formRef" :model="form" :rules="rules" v-loading="loading">
          <!-- Step 1: Account -->
          <div v-show="currentStep === 0" class="step-content">
            <el-form-item prop="email">
              <el-input v-model="form.email" placeholder="Email Address" size="large" />
            </el-form-item>
            <el-form-item prop="username">
              <el-input v-model="form.username" placeholder="Username" size="large" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input v-model="form.password" type="password" placeholder="Password" size="large" show-password />
            </el-form-item>
          </div>

          <!-- Step 2: Plan -->
          <div v-show="currentStep === 1" class="step-content">
            <div class="plan-options">
              <div 
                v-for="plan in plans" 
                :key="plan.id"
                class="plan-option"
                :class="{ selected: form.plan === plan.id }"
                @click="form.plan = plan.id"
              >
                <div class="plan-icon">
                  <el-icon v-if="plan.id === 'basic'"><Monitor /></el-icon>
                  <el-icon v-else-if="plan.id === 'business'"><Briefcase /></el-icon>
                  <el-icon v-else><OfficeBuilding /></el-icon>
                </div>
                <div class="plan-info">
                  <span class="plan-name">{{ plan.name }}</span>
                  <span class="plan-price">₦{{ plan.price }}/mo</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Step 3: Configure -->
          <div v-show="currentStep === 2" class="step-content">
            <el-form-item prop="company_name">
              <el-input v-model="form.company_name" placeholder="Company Name" size="large" />
            </el-form-item>
            <el-form-item prop="subdomain">
              <el-input v-model="form.subdomain" placeholder="Subdomain" size="large">
                <template #append>.yourdomain.com</template>
              </el-input>
            </el-form-item>
          </div>

          <div class="form-actions">
            <el-button v-if="currentStep > 0" @click="currentStep--">Back</el-button>
            <el-button v-if="currentStep < 2" type="primary" @click="nextStep" size="large">
              Continue
            </el-button>
            <el-button v-if="currentStep === 2" type="primary" @click="submitForm" :loading="loading" size="large">
              Create Account
            </el-button>
          </div>
        </el-form>

        <div class="auth-footer">
          <p>Already have an account? <router-link to="/login">Sign in</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../stores/auth'

const router = useRouter()
const formRef = ref(null)
const currentStep = ref(0)
const loading = ref(false)

const form = reactive({
  email: '',
  username: '',
  password: '',
  plan: 'basic',
  company_name: '',
  subdomain: ''
})

const rules = {
  email: [{ required: true, message: 'Please enter email', trigger: 'blur' }],
  username: [{ required: true, message: 'Please enter username', trigger: 'blur' }],
  password: [{ required: true, message: 'Please enter password', trigger: 'blur' }],
  company_name: [{ required: true, message: 'Please enter company name', trigger: 'blur' }],
  subdomain: [{ required: true, message: 'Please enter subdomain', trigger: 'blur' }]
}

const plans = [
  { id: 'basic', name: 'Starter', price: '15,000' },
  { id: 'business', name: 'Business', price: '45,000' },
  { id: 'enterprise', name: 'Enterprise', price: '120,000' }
]

const nextStep = async () => {
  if (currentStep.value === 0) {
    const fields = ['email', 'username', 'password']
    const valid = await formRef.value.validateField(fields).catch(() => false)
    if (!valid) return
  }
  currentStep.value++
}

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  try {
    await api.post('/auth/register', {
      email: form.email,
      username: form.username,
      password: form.password
    })
    
    const loginForm = new FormData()
    loginForm.append('username', form.username)
    loginForm.append('password', form.password)
    const loginRes = await api.post('/auth/login', loginForm)
    localStorage.setItem('access_token', loginRes.data.access_token)
    
    const clientName = form.subdomain.toLowerCase().replace(/\s+/g, '-')
    
    await api.post('/clients', {
      name: clientName,
      domain: `${clientName}.yourdomain.com`,
      email: form.email,
      plan: form.plan
    })
    
    const paymentRes = await api.post('/payments/initialize', {
      plan: form.plan,
      billing_cycle: 'monthly'
    })
    
    ElMessage.success('Account created! Please complete payment to activate your instance.')
    router.push({ 
      path: '/payment', 
      query: { 
        plan: form.plan, 
        reference: paymentRes.data.reference,
        client: clientName
      } 
    })
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
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
  padding: 40px 20px;
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
  width: 100%;
  max-width: 480px;
  position: relative;
  z-index: 1;
}

.auth-card {
  background: white;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
}

.auth-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: inline-flex;
  margin-bottom: 20px;
}

.auth-header h1 {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.auth-header p {
  color: #6B7280;
  font-size: 0.9rem;
}

.steps {
  margin-bottom: 32px;
}

.step-content {
  min-height: 200px;
}

.plan-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.plan-option {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.plan-option:hover {
  border-color: #6366F1;
}

.plan-option.selected {
  border-color: #6366F1;
  background: rgba(99, 102, 241, 0.05);
}

.plan-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.1);
  color: #6366F1;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.plan-info {
  display: flex;
  flex-direction: column;
}

.plan-name {
  font-weight: 600;
  color: #111827;
}

.plan-price {
  font-size: 0.875rem;
  color: #6366F1;
}

.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 24px;
}

.form-actions .el-button {
  flex: 1;
  height: 44px;
  font-weight: 600;
  border-radius: 10px;
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
</style>
