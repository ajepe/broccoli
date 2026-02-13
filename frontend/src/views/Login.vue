<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="login-header">
          <h1>Odoo Cloud</h1>
          <p>Africa Platform</p>
        </div>
      </template>
      
      <el-form ref="formRef" :model="form" :rules="rules" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input 
            v-model="form.username" 
            placeholder="Username"
            prefix-icon="User"
            size="large"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="form.password" 
            type="password"
            placeholder="Password"
            prefix-icon="Lock"
            size="large"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            size="large" 
            :loading="loading" 
            native-type="submit"
            style="width: 100%"
          >
            Login
          </el-button>
        </el-form-item>
        
        <el-divider>OR</el-divider>
        
        <el-button 
          size="large" 
          class="demo-btn"
          @click="useDemo"
        >
          Try Demo Account
        </el-button>
      </el-form>
      
      <div class="login-links">
        <router-link to="/signup">Create an Account</router-link>
        <span class="divider">|</span>
        <router-link to="/pricing">View Pricing</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref(null)
const loading = ref(false)

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
    ElMessage.success('Login successful')
    router.push('/')
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Login failed')
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
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
}

.login-card {
  width: 400px;
}

.login-header {
  text-align: center;
}

.login-header h1 {
  color: #00d9ff;
  margin: 0;
  font-size: 2rem;
}

.login-header p {
  color: #909399;
  margin: 5px 0 0;
}

.login-links {
  text-align: center;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #e4e7ed;
}

.login-links a {
  color: #00d9ff;
  text-decoration: none;
}

.login-links a:hover {
  text-decoration: underline;
}

.login-links .divider {
  margin: 0 15px;
  color: #909399;
}

.demo-btn {
  width: 100%;
  background: transparent;
  border: 2px solid #00d9ff;
  color: #00d9ff;
}

.demo-btn:hover {
  background: #00d9ff;
  color: #fff;
}
</style>
