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
        
        <el-card style="margin-top: 20px;">
          <template #header>
            <div style="display: flex; justify-content: space-between; align-items: center;">
              <span>Custom Domains</span>
              <el-button type="primary" size="small" @click="showAddDomainDialog = true">
                Add Domain
              </el-button>
            </div>
          </template>
          <div v-if="!client?.custom_domains?.length" style="color: #909399; text-align: center; padding: 20px;">
            No custom domains added yet
          </div>
          <el-table v-else :data="client.custom_domains">
            <el-table-column prop="domain" label="Domain">
              <template #default="{ row }">
                <el-link type="primary" :href="`https://${row}`" target="_blank">
                  {{ row }}
                </el-link>
              </template>
            </el-table-column>
            <el-table-column label="Action" width="100">
              <template #default="{ row }">
                <el-button type="danger" size="small" text @click="removeDomain(row)">
                  Remove
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
    
    <el-dialog v-model="showAddDomainDialog" title="Add Custom Domain" width="400px">
      <el-form @submit.prevent="addDomain">
        <el-form-item label="Domain">
          <el-input v-model="newDomain" placeholder="e.g. erp.yourcompany.com" />
        </el-form-item>
        <el-alert 
          type="info" 
          :closable="false"
          style="margin-bottom: 15px;"
        >
          <template #title>
            <div style="font-size: 12px;">
              <p>Add these DNS records to point your domain:</p>
              <p><strong>CNAME:</strong> {{ newDomain || 'your-domain.com' }} → {{ client?.domain }}</p>
              <p><strong>or A Record:</strong> {{ newDomain || 'your-domain.com' }} → [Your Server IP]</p>
            </div>
          </template>
        </el-alert>
      </el-form>
      <template #footer>
        <el-button @click="showAddDomainDialog = false">Cancel</el-button>
        <el-button type="primary" @click="addDomain" :loading="addingDomain">Add Domain</el-button>
      </template>
    </el-dialog>
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
const showAddDomainDialog = ref(false)
const newDomain = ref('')
const addingDomain = ref(false)

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

const addDomain = async () => {
  if (!newDomain.value.trim()) {
    ElMessage.warning('Please enter a domain')
    return
  }
  
  const domainRegex = /^[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]?(\.[a-zA-Z]{2,})+$/
  if (!domainRegex.test(newDomain.value.trim())) {
    ElMessage.warning('Invalid domain format')
    return
  }
  
  addingDomain.value = true
  try {
    await api.post(`/clients/${clientName}/domains?domain=${encodeURIComponent(newDomain.value.trim())}`)
    ElMessage.success('Domain added. SSL certificate will be provisioned automatically.')
    showAddDomainDialog.value = false
    newDomain.value = ''
    fetchClient()
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || 'Failed to add domain')
  } finally {
    addingDomain.value = false
  }
}

const removeDomain = async (domain) => {
  try {
    await ElMessageBox.confirm(`Remove domain "${domain}"?`, 'Confirm')
    await api.delete(`/clients/${clientName}/domains/${domain}`)
    ElMessage.success('Domain removed')
    fetchClient()
  } catch (error) {
    if (error !== 'cancel') ElMessage.error('Failed to remove domain')
  }
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
