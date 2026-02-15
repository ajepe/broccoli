<template>
  <div class="clients-page">
    <div class="page-header">
      <div>
        <h1>Clients</h1>
        <p>Manage your Odoo cloud instances</p>
      </div>
      <el-button type="primary" @click="$router.push('/clients/new')">
        <el-icon><Plus /></el-icon>
        Add Client
      </el-button>
    </div>

    <el-card class="clients-card">
      <el-table :data="clients" v-loading="loading" style="width: 100%">
        <el-table-column prop="name" label="Client" min-width="180">
          <template #default="{ row }">
            <div class="client-info">
              <div class="client-avatar">{{ row.name.charAt(0).toUpperCase() }}</div>
              <div>
                <div class="client-name">{{ row.name }}</div>
                <div class="client-domain">{{ row.domain }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="email" label="Email" min-width="180" />
        <el-table-column prop="plan" label="Plan" width="120">
          <template #default="{ row }">
            <el-tag :type="getPlanType(row.plan)" size="small">{{ row.plan }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="Status" width="130">
          <template #default="{ row }">
            <div class="status-badge" :class="row.status">
              <span class="status-dot"></span>
              {{ row.status }}
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="odoo_port" label="Port" width="80" />
        <el-table-column label="Actions" width="180" fixed="right">
          <template #default="{ row }">
            <div class="action-buttons">
              <el-button size="small" @click="viewClient(row)">
                <el-icon><View /></el-icon>
              </el-button>
              <el-button 
                v-if="row.status === 'active'" 
                size="small" 
                type="warning"
                @click="suspendClient(row)"
              >
                <el-icon><Lock /></el-icon>
              </el-button>
              <el-button 
                v-if="row.status === 'suspended'" 
                size="small" 
                type="success"
                @click="resumeClient(row)"
              >
                <el-icon><Unlock /></el-icon>
              </el-button>
              <el-button size="small" type="danger" @click="deleteClient(row)">
                <el-icon><Delete /></el-icon>
              </el-button>
            </div>
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

const deleteClient = async (client) => {
  try {
    await ElMessageBox.confirm(
      `Are you sure you want to delete ${client.name}? The instance will be scheduled for deletion in 12 hours and can be restored by an admin before then.`,
      'Schedule Client Deletion',
      { type: 'warning', confirmButtonText: 'Schedule Delete', cancelButtonText: 'Cancel' }
    )
    await api.post(`/clients/${client.name}/schedule-delete?hours_until_deletion=12`)
    ElMessage.success(`Client "${client.name}" scheduled for deletion in 12 hours`)
    fetchClients()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error(error.response?.data?.detail || 'Failed to schedule deletion')
    }
  }
}

const getPlanType = (plan) => {
  const types = { basic: 'info', business: 'success', enterprise: 'warning' }
  return types[plan] || 'info'
}

onMounted(() => {
  fetchClients()
})
</script>

<style scoped>
.clients-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.page-header h1 {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
  margin-bottom: 4px;
}

.page-header p {
  color: #6B7280;
}

.clients-card {
  border-radius: 12px;
}

.client-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.client-avatar {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
}

.client-name {
  font-weight: 600;
  color: #111827;
}

.client-domain {
  font-size: 0.8rem;
  color: #9CA3AF;
}

.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.8rem;
  font-weight: 500;
  text-transform: capitalize;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.status-badge.active .status-dot {
  background: #10B981;
}

.status-badge.suspended .status-dot {
  background: #F59E0B;
}

.status-badge.pending .status-dot {
  background: #6B7280;
}

.action-buttons {
  display: flex;
  gap: 8px;
}
</style>
