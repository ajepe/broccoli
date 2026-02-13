<template>
  <div class="create-client">
    <el-card>
      <template #header>
        <span>Create New Client</span>
      </template>
      
      <el-form 
        ref="formRef"
        :model="form" 
        :rules="rules" 
        label-width="150px"
        v-loading="loading"
      >
        <el-form-item label="Client Name" prop="name">
          <el-input v-model="form.name" placeholder="e.g., acme-corp">
            <template #append>.yourdomain.com</template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="Full Domain" prop="domain">
          <el-input v-model="form.domain" placeholder="acme-corp.yourdomain.com" />
        </el-form-item>
        
        <el-form-item label="Email" prop="email">
          <el-input v-model="form.email" type="email" placeholder="admin@clientdomain.com" />
        </el-form-item>
        
        <el-form-item label="Plan" prop="plan">
          <el-radio-group v-model="form.plan">
            <el-radio label="basic">Basic</el-radio>
            <el-radio label="business">Business</el-radio>
            <el-radio label="enterprise">Enterprise</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="Redis Cache">
          <el-switch v-model="form.redis_enabled" />
        </el-form-item>
        
        <el-divider />
        
        <el-form-item>
          <el-button type="primary" @click="submitForm" :loading="loading">
            Create Client
          </el-button>
          <el-button @click="$router.push('/clients')">Cancel</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="plan-info" v-if="form.plan">
      <template #header>
        <span>Plan Details</span>
      </template>
      <el-descriptions :column="2" border>
        <el-descriptions-item label="RAM">{{ getPlanDetails.ram }}</el-descriptions-item>
        <el-descriptions-item label="Database RAM">{{ getPlanDetails.dbRam }}</el-descriptions-item>
        <el-descriptions-item label="CPU">{{ getPlanDetails.cpu }} cores</el-descriptions-item>
        <el-descriptions-item label="Backups">{{ getPlanDetails.backups }}</el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { api } from '../stores/auth'

const router = useRouter()
const formRef = ref(null)
const loading = ref(false)

const form = ref({
  name: '',
  domain: '',
  email: '',
  plan: 'basic',
  redis_enabled: false
})

const rules = {
  name: [
    { required: true, message: 'Please enter client name', trigger: 'blur' },
    { pattern: /^[a-z0-9][a-z0-9-]*[a-z0-9]$/, message: 'Use lowercase letters, numbers, and hyphens only', trigger: 'blur' }
  ],
  domain: [
    { required: true, message: 'Please enter domain', trigger: 'blur' }
  ],
  email: [
    { required: true, message: 'Please enter email', trigger: 'blur' },
    { type: 'email', message: 'Please enter valid email', trigger: 'blur' }
  ]
}

const planDetails = {
  basic: { ram: '2 GB', dbRam: '1 GB', cpu: '1', backups: 'Daily' },
  business: { ram: '4 GB', dbRam: '2 GB', cpu: '2', backups: 'Hourly' },
  enterprise: { ram: '8 GB', dbRam: '4 GB', cpu: '4', backups: 'Hourly + Priority' }
}

const getPlanDetails = computed(() => planDetails[form.value.plan] || planDetails.basic)

const submitForm = async () => {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  
  loading.value = true
  
  try {
    const payload = {
      name: form.value.name.toLowerCase().replace(/\s+/g, '-'),
      domain: form.value.domain,
      email: form.value.email,
      plan: form.value.plan,
      redis_enabled: form.value.redis_enabled
    }
    
    const response = await api.post('/clients', payload)
    
    ElMessage.success('Client created successfully!')
    router.push(`/clients/${response.data.name}`)
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Failed to create client')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.create-client {
  padding: 20px;
  max-width: 800px;
}

.plan-info {
  margin-top: 20px;
}
</style>
