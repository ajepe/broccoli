<template>
  <div class="client-detail">
    <el-page-header @back="$router.push('/clients')" :title="clientName">
      <template #content>
        <span class="detail-header">{{ clientName }}</span>
      </template>
    </el-page-header>
    
    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card>
          <template #header>
            <span>Instance Details</span>
          </template>
          <el-descriptions :column="2" border v-loading="loading">
            <el-descriptions-item label="Domain">{{ client?.domain }}</el-descriptions-item>
            <el-descriptions-item label="Status">
              <el-tag :type="getStatusType(client?.status)">{{ client?.status }}</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Plan">{{ client?.plan }}</el-descriptions-item>
            <el-descriptions-item label="Odoo Port">{{ client?.odoo_port }}</el-descriptions-item>
            <el-descriptions-item label="RAM Limit">{{ client?.memory_limit }}</el-descriptions-item>
            <el-descriptions-item label="DB RAM">{{ client?.db_memory_limit }}</el-descriptions-item>
            <el-descriptions-item label="CPU">{{ client?.cpu_limit }} cores</el-descriptions-item>
            <el-descriptions-item label="Redis">
              <el-tag v-if="client?.redis_enabled" type="success">Enabled</el-tag>
              <el-tag v-else type="info">Disabled</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="Disk Usage">
              {{ formatDisk(client?.disk_usage_mb) }}
            </el-descriptions-item>
            <el-descriptions-item label="Last Backup">
              {{ client?.last_backup ? formatDate(client.last_backup) : 'Never' }}
            </el-descriptions-item>
          </el-descriptions>
          
          <div style="margin-top: 20px;">
            <el-button type="primary" @click="openOdoo">Open Odoo</el-button>
            <el-button @click="triggerBackup">Run Backup</el-button>
            <el-button 
              v-if="client?.status === 'active'" 
              type="warning" 
              @click="suspendClient"
            >
              Suspend
            </el-button>
            <el-button 
              v-if="client?.status === 'suspended'" 
              type="success" 
              @click="resumeClient"
            >
              Resume
            </el-button>
          </div>
        </el-card>
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <span>Resource Usage</span>
          </template>
          <el-table :data="containerStats" v-loading="statsLoading">
            <el-table-column prop="name" label="Container" />
            <el-table-column prop="status" label="Status" />
            <el-table-column prop="cpu_percent" label="CPU %" />
            <el-table-column prop="memory_usage" label="Memory" />
          </el-table>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>Connection Info</span>
          </template>
          <el-form label-width="100px">
            <el-form-item label="Database">
              <el-input :model-value="client?.db_name" readonly>
                <template #append>
                  <el-button @click="copyToClipboard(client?.db_name)">Copy</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="User">
              <el-input :model-value="client?.db_user" readonly>
                <template #append>
                  <el-button @click="copyToClipboard(client?.db_user)">Copy</el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="Password">
              <el-input :model-value="showPassword ? client?.db_password : '••••••••'" readonly>
                <template #append>
                  <el-button @click="showPassword = !showPassword">
                    {{ showPassword ? 'Hide' : 'Show' }}
                  </el-button>
                </template>
              </el-input>
            </el-form-item>
            <el-form-item label="URL">
              <el-input :model-value="`https://${client?.domain}`" readonly>
                <template #append>
                  <el-button @click="openOdoo">Open</el-button>
                </template>
              </el-input>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../stores/auth'

const route = useRoute()
const clientName = route.params.name

const client = ref(null)
const containerStats = ref([])
const loading = ref(true)
const statsLoading = ref(true)
const showPassword = ref(false)

const fetchClient = async () => {
  loading.value = true
  try {
    const response = await api.get(`/clients/${clientName}`)
    client.value = response.data
  } catch (error) {
    ElMessage.error('Failed to load client')
  } finally {
    loading.value = false
  }
}

const fetchStats = async () => {
  statsLoading.value = true
  try {
    const response = await api.get(`/clients/${clientName}/stats`)
    containerStats.value = response.data.containers || []
  } catch (error) {
    console.error('Failed to load stats')
  } finally {
    statsLoading.value = false
  }
}

const triggerBackup = async () => {
  try {
    await api.post(`/clients/${clientName}/backup`)
    ElMessage.success('Backup started')
  } catch (error) {
    ElMessage.error('Failed to start backup')
  }
}

const suspendClient = async () => {
  try {
    await ElMessageBox.confirm('Suspend this client?', 'Confirm')
    await api.post(`/clients/${clientName}/suspend`)
    ElMessage.success('Client suspended')
    fetchClient()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('Failed')
  }
}

const resumeClient = async () => {
  try {
    await api.post(`/clients/${clientName}/resume`)
    ElMessage.success('Client resumed')
    fetchClient()
  } catch (error) {
    ElMessage.error('Failed to resume')
  }
}

const openOdoo = () => {
  window.open(`https://${client.value?.domain}`, '_blank')
}

const copyToClipboard = (text) => {
  navigator.clipboard.writeText(text)
  ElMessage.success('Copied')
}

const formatDisk = (mb) => {
  if (!mb) return '0 MB'
  return mb >= 1024 ? (mb / 1024).toFixed(1) + ' GB' : mb + ' MB'
}

const formatDate = (date) => new Date(date).toLocaleString()

const getStatusType = (status) => {
  const types = { active: 'success', suspended: 'warning', pending: 'info' }
  return types[status] || ''
}

onMounted(() => {
  fetchClient()
  fetchStats()
})
</script>

<style scoped>
.client-detail {
  padding: 20px;
}

.detail-header {
  font-size: 1.2rem;
  font-weight: bold;
}
</style>
