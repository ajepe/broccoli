<template>
  <div class="signup-container">
    <el-card class="signup-card">
      <template #header>
        <div class="signup-header">
          <h1>Get Started</h1>
          <p>Deploy your Odoo instance in minutes</p>
        </div>
      </template>
      
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="Account" />
        <el-step title="Plan" />
        <el-step title="Configure" />
      </el-steps>

      <el-form ref="formRef" :model="form" :rules="rules" v-loading="loading">
        <!-- Step 1: Account -->
        <div v-show="currentStep === 0">
          <el-form-item prop="email">
            <el-input v-model="form.email" placeholder="Email Address" prefix-icon="Message" size="large" />
          </el-form-item>
          <el-form-item prop="username">
            <el-input v-model="form.username" placeholder="Username" prefix-icon="User" size="large" />
          </el-form-item>
          <el-form-item prop="password">
            <el-input v-model="form.password" type="password" placeholder="Password" prefix-icon="Lock" size="large" show-password />
          </el-form-item>
          <el-form-item prop="full_name">
            <el-input v-model="form.full_name" placeholder="Full Name (Optional)" prefix-icon="UserFilled" size="large" />
          </el-form-item>
        </div>

        <!-- Step 2: Plan -->
        <div v-show="currentStep === 1">
          <div class="plan-cards">
            <div 
              v-for="plan in plans" 
              :key="plan.id"
              class="plan-card"
              :class="{ selected: form.plan === plan.id }"
              @click="form.plan = plan.id"
            >
              <div class="plan-header">
                <h3>{{ plan.name }}</h3>
                <span class="price">{{ plan.price }}<small>/mo</small></span>
              </div>
              <ul>
                <li v-for="feature in plan.features" :key="feature">✓ {{ feature }}</li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Step 3: Configure -->
        <div v-show="currentStep === 2">
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
            Create Account & Deploy
          </el-button>
        </div>
      </el-form>

      <div class="login-link">
        Already have an account? <router-link to="/login">Login</router-link>
      </div>
    </el-card>
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
  full_name: '',
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
  {
    id: 'basic',
    name: 'Starter',
    price: '₦15,000',
    features: ['2 GB RAM', '1 CPU Core', '10 GB Storage', 'Daily Backups', 'Email Support']
  },
  {
    id: 'business',
    name: 'Business',
    price: '₦45,000',
    features: ['4 GB RAM', '2 CPU Cores', '25 GB Storage', 'Hourly Backups', 'Redis Cache', 'Priority Support']
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: '₦120,000',
    features: ['8 GB RAM', '4 CPU Cores', '100 GB Storage', 'Hourly Backups', 'Redis Cache', '24/7 Support', 'Custom Domain']
  }
]

const nextStep = async () => {
  if (currentStep.value === 0) {
    const fields = ['email', 'username', 'password']
    const valid = await formRef.value.validateField(fields).catch(() => false)
    if (!valid) return
  } else if (currentStep.value === 1) {
    if (!form.plan) {
      ElMessage.warning('Please select a plan')
      return
    }
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
      password: form.password,
      full_name: form.full_name
    })
    
    await api.post('/auth/login', null, {
      params: { username: form.username, password: form.password }
    })
    
    const loginForm = new FormData()
    loginForm.append('username', form.username)
    loginForm.append('password', form.password)
    const loginRes = await api.post('/auth/login', loginForm)
    localStorage.setItem('access_token', loginRes.data.access_token)
    
    await api.post('/clients', {
      name: form.subdomain.toLowerCase().replace(/\s+/g, '-'),
      domain: `${form.subdomain.toLowerCase()}.yourdomain.com`,
      email: form.email,
      plan: form.plan
    })
    
    ElMessage.success('Account created and Odoo instance deployed!')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Registration failed')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.signup-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 20px;
}

.signup-card {
  width: 600px;
  max-width: 100%;
}

.signup-header {
  text-align: center;
}

.signup-header h1 {
  color: #00d9ff;
  margin: 0;
}

.signup-header p {
  color: #909399;
  margin: 5px 0 0;
}

.plan-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 15px;
  margin: 20px 0;
}

.plan-card {
  border: 2px solid #dcdfe6;
  border-radius: 8px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
}

.plan-card:hover {
  border-color: #409eff;
}

.plan-card.selected {
  border-color: #00d9ff;
  background: #f0f9ff;
}

.plan-header {
  text-align: center;
}

.plan-header h3 {
  margin: 0;
  color: #303133;
}

.price {
  font-size: 1.5rem;
  color: #00d9ff;
  font-weight: bold;
}

.price small {
  font-size: 0.8rem;
  color: #909399;
}

.plan-card ul {
  list-style: none;
  padding: 0;
  margin: 10px 0 0;
}

.plan-card li {
  font-size: 0.8rem;
  color: #606266;
  padding: 3px 0;
}

.form-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 20px;
}

.login-link {
  text-align: center;
  margin-top: 20px;
  color: #909399;
}

.login-link a {
  color: #00d9ff;
  text-decoration: none;
}
</style>
