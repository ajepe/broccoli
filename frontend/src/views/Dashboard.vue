<template>
  <div class="dashboard">
    <div class="page-header">
      <div>
        <h1>Dashboard</h1>
        <p>Overview of your Odoo cloud platform</p>
      </div>
      <el-button type="primary" @click="$router.push('/clients/new')">
        <el-icon><Plus /></el-icon>
        New Client
      </el-button>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #6366F1 0%, #818CF8 100%);">
          <el-icon :size="24"><OfficeBuilding /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.total_clients }}</span>
          <span class="stat-label">Total Clients</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #10B981 0%, #34D399 100%);">
          <el-icon :size="24"><CircleCheck /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.active_clients }}</span>
          <span class="stat-label">Active</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #F59E0B 0%, #FBBF24 100%);">
          <el-icon :size="24"><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ stats.suspended_clients }}</span>
          <span class="stat-label">Suspended</span>
        </div>
      </div>
      
      <div class="stat-card">
        <div class="stat-icon" style="background: linear-gradient(135deg, #8B5CF6 0%, #A78BFA 100%);">
          <el-icon :size="24"><HardDisk /></el-icon>
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ formatDisk(stats.total_disk_usage_mb) }}</span>
          <span class="stat-label">Total Storage</span>
        </div>
      </div>
    </div>

    <div class="content-grid">
      <el-card class="recent-clients">
        <template #header>
          <div class="card-header">
            <h3>Recent Clients</h3>
            <router-link to="/clients" class="view-all">View all</router-link>
          </div>
        </template>
        
        <el-table :data="recentClients" style="width: 100%" :row-class-name="tableRowClassName">
          <el-table-column prop="name" label="Name" min-width="150">
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
          <el-table-column prop="plan" label="Plan" width="120">
            <template #default="{ row }">
              <el-tag :type="getPlanType(row.plan)" size="small">{{ row.plan }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="status" label="Status" width="120">
            <template #default="{ row }">
              <div class="status-badge" :class="row.status">
                <span class="status-dot"></span>
                {{ row.status }}
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="Created" width="140">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="" width="80">
            <template #default="{ row }">
              <el-button size="small" circle @click="$router.push(`/clients/${row.name}`)">
                <el-icon><ArrowRight /></el-icon>
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <el-card class="quick-actions">
        <template #header>
          <h3>Quick Actions</h3>
        </template>
        
        <div class="actions-list">
          <div class="action-item" @click="$router.push('/clients/new')">
            <div class="action-icon" style="background: rgba(99, 102, 241, 0.1); color: #6366F1;">
              <el-icon><Plus /></el-icon>
            </div>
            <div class="action-text">
              <span class="action-title">Add New Client</span>
              <span class="action-desc">Provision a new Odoo instance</span>
            </div>
          </div>
          
          <div class="action-item" @click="$router.push('/backups')">
            <div class="action-icon" style="background: rgba(16, 185, 129, 0.1); color: #10B981;">
              <el-icon><Refresh /></el-icon>
            </div>
            <div class="action-text">
              <span class="action-title">Manage Backups</span>
              <span class="action-desc">View and restore backups</span>
            </div>
          </div>
          
          <div class="action-item">
            <div class="action-icon" style="background: rgba(245, 158, 11, 0.1); color: #F59E0B;">
              <el-icon><Monitor /></el-icon>
            </div>
            <div class="action-text">
              <span class="action-title">View Metrics</span>
              <span class="action-desc">Check system performance</span>
            </div>
          </div>
        </div>
      </el-card>
    </div>
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
  if (!mb || mb === 0) return '0 GB'
  if (mb >= 1024) return (mb / 1024).toFixed(1) + ' GB'
  return mb + ' MB'
}

const formatDate = (date) => {
  if (!date) return '-'
  return new Date(date).toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    year: 'numeric'
  })
}

const getPlanType = (plan) => {
  const types = { basic: 'info', business: 'success', enterprise: 'warning' }
  return types[plan] || 'info'
}

const tableRowClassName = ({ row }) => {
  return ''
}

onMounted(() => {
  fetchStats()
  fetchRecentClients()
})
</script>

<style scoped>
.dashboard {
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

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.stat-icon {
  width: 56px;
  height: 56px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #111827;
}

.stat-label {
  font-size: 0.875rem;
  color: #6B7280;
}

.content-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
}

.view-all {
  font-size: 0.875rem;
  color: #6366F1;
  text-decoration: none;
}

.view-all:hover {
  text-decoration: underline;
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
  font-size: 1rem;
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

.quick-actions h3 {
  font-size: 1.1rem;
  font-weight: 600;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.action-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s;
}

.action-item:hover {
  background: #F9FAFB;
}

.action-icon {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
}

.action-text {
  display: flex;
  flex-direction: column;
}

.action-title {
  font-weight: 600;
  color: #111827;
}

.action-desc {
  font-size: 0.8rem;
  color: #6B7280;
}

@media (max-width: 1200px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .content-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
