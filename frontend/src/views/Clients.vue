<template>
  <div class="clients-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>All Clients</span>
          <el-button type="primary" @click="$router.push('/clients/new')">
            <el-icon><Plus /></el-icon>
            Create Client
          </el-button>
        </div>
      </template>
      
      <el-table :data="clients" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="Client Name" width="150">
          <template #default="{ row }">
            <router-link :to="`/clients/${row.name}`" class="client-link">
              {{ row.name }}
            </router-link>
          </template>
        </el-table-column>
        <el-table-column prop="domain" label="Domain" />
        <el-table-column prop="email" label="Email" />
        <el-table-column prop="plan" label="Plan" width="120">
          <template #default="{ row }">
            <el-tag :type="getPlanType(row.plan)">{{ row.plan }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="120">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="odoo_port" label="Port" width="80" />
        <el-table-column label="Actions" width="200">
          <template #default="{ row }">
            <el-button size="small" @click="viewClient(row)">View</el-button>
            <el-button 
              v-if="row.status === 'active'" 
              size="small" 
              type="warning"
              @click="suspendClient(row)"
            >
              Suspend
            </el-button>
            <el-button 
              v-if="row.status === 'suspended'" 
              size="small" 
              type="success"
              @click="resumeClient(row)"
            >
              Resume
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../stores/auth'

const router = useRouter()
const clients = ref([])
const loading = ref(false)

const fetchClients = async () => {
  loading.value = true
  try {
    const response = await api.get('/clients')
    clients.value = response.data
  } catch (error) {
    ElMessage.error('Failed to load clients')
  } finally {
    loading.value = false
  }
}

const viewClient = (client) => {
  router.push(`/clients/${client.name}`)
}

const suspendClient = async (client) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to suspend ${client.name}?`,
      'Confirm Suspend',
      { type: 'warning' }
    )
    
    await api.post(`/clients/${client.name}/suspend`)
    ElMessage.success('Client suspended')
    fetchClients()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Failed to suspend client')
    }
  }
}

const resumeClient = async (client) => {
  try {
    await api.post(`/clients/${client.name}/resume`)
    ElMessage.success('Client resumed')
    fetchClients()
  } catch (error) {
    ElMessage.error('Failed to resume client')
  }
}

const getPlanType = (plan) => {
  const types = { basic: '', business: 'success', enterprise: 'warning' }
  return types[plan] || ''
}

const getStatusType = (status) => {
  const types = { active: 'success', suspended: 'warning', pending: 'info' }
  return types[status] || ''
}

onMounted(() => {
  fetchClients()
})
</script>

<style scoped>
.clients-page {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.client-link {
  color: #409eff;
  text-decoration: none;
}

.client-link:hover {
  text-decoration: underline;
}
</style>
