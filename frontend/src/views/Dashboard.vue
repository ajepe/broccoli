<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #409eff;">
            <el-icon :size="30"><OfficeBuilding /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ stats.total_clients }}</h3>
            <p>Total Clients</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #67c23a;">
            <el-icon :size="30"><CircleCheck /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ stats.active_clients }}</h3>
            <p>Active</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #e6a23c;">
            <el-icon :size="30"><Warning /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ stats.suspended_clients }}</h3>
            <p>Suspended</p>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon" style="background: #909399;">
            <el-icon :size="30"><HardDisk /></el-icon>
          </div>
          <div class="stat-content">
            <h3>{{ formatDisk(stats.total_disk_usage_mb) }}</h3>
            <p>Total Disk</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>Recent Clients</span>
              <el-button type="primary" @click="$router.push('/clients/new')">
                <el-icon><Plus /></el-icon>
                New Client
              </el-button>
            </div>
          </template>
          <el-table :data="recentClients" style="width: 100%">
            <el-table-column prop="name" label="Name" />
            <el-table-column prop="domain" label="Domain" />
            <el-table-column prop="plan" label="Plan">
              <template #default="{ row }">
                <el-tag :type="getPlanType(row.plan)">{{ row.plan }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="Status">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="Created">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
            <el-table-column label="Actions">
              <template #default="{ row }">
                <el-button size="small" @click="$router.push(`/clients/${row.name}`)">
                  View
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../stores/auth'

const stats = ref({
  total_clients: 0,
  active_clients: 0,
  suspended_clients: 0,
  total_disk_usage_mb: 0
})

const recentClients = ref([])

const fetchStats = async () => {
  try {
    const response = await api.get('/clients/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats:', error)
  }
}

const fetchRecentClients = async () => {
  try {
    const response = await api.get('/clients?limit=5')
    recentClients.value = response.data
  } catch (error) {
    console.error('Failed to fetch clients:', error)
  }
}

const formatDisk = (mb) => {
  if (mb >= 1024) {
    return (mb / 1024).toFixed(1) + ' GB'
  }
  return mb + ' MB'
}

const formatDate = (date) => {
  return new Date(date).toLocaleDateString()
}

const getPlanType = (plan) => {
  const types = {
    basic: '',
    business: 'success',
    enterprise: 'warning'
  }
  return types[plan] || ''
}

const getStatusType = (status) => {
  const types = {
    active: 'success',
    suspended: 'warning',
    pending: 'info'
  }
  return types[status] || ''
}

onMounted(() => {
  fetchStats()
  fetchRecentClients()
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.stat-content h3 {
  font-size: 1.8rem;
  margin: 0;
  color: #303133;
}

.stat-content p {
  margin: 0;
  color: #909399;
  font-size: 0.9rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
