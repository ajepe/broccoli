<template>
  <div class="metrics-page">
    <div class="page-header">
      <div>
        <h1>System Metrics</h1>
        <p>Monitor your server performance and resource usage</p>
      </div>
      <div class="header-actions">
        <el-select v-model="timeRange" placeholder="Select time range" size="default">
          <el-option label="Last Hour" value="1h" />
          <el-option label="Last 24 Hours" value="24h" />
          <el-option label="Last 7 Days" value="7d" />
          <el-option label="Last 30 Days" value="30d" />
        </el-select>
        <el-button @click="refreshData">
          <el-icon><Refresh /></el-icon>
          Refresh
        </el-button>
      </div>
    </div>

    <div class="metrics-grid">
      <el-card class="metric-card">
        <div class="metric-header">
          <div class="metric-icon cpu">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-label">CPU Usage</span>
            <span class="metric-value">{{ metrics.cpu.used }}%</span>
          </div>
        </div>
        <el-progress 
          :percentage="metrics.cpu.used" 
          :color="getCpuColor(metrics.cpu.used)"
          :stroke-width="8"
          :show-text="false"
        />
        <div class="metric-footer">
          <span>{{ metrics.cpu.cores }} cores</span>
          <span>{{ metrics.cpu.idle }}% idle</span>
        </div>
      </el-card>

      <el-card class="metric-card">
        <div class="metric-header">
          <div class="metric-icon memory">
            <el-icon><MemoryStick /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-label">Memory Usage</span>
            <span class="metric-value">{{ metrics.memory.usedPercent }}%</span>
          </div>
        </div>
        <el-progress 
          :percentage="metrics.memory.usedPercent" 
          :color="getMemoryColor(metrics.memory.usedPercent)"
          :stroke-width="8"
          :show-text="false"
        />
        <div class="metric-footer">
          <span>{{ formatBytes(metrics.memory.used) }} / {{ formatBytes(metrics.memory.total) }}</span>
        </div>
      </el-card>

      <el-card class="metric-card">
        <div class="metric-header">
          <div class="metric-icon disk">
            <el-icon><HardDisk /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-label">Disk Usage</span>
            <span class="metric-value">{{ metrics.disk.usedPercent }}%</span>
          </div>
        </div>
        <el-progress 
          :percentage="metrics.disk.usedPercent" 
          :color="getDiskColor(metrics.disk.usedPercent)"
          :stroke-width="8"
          :show-text="false"
        />
        <div class="metric-footer">
          <span>{{ formatBytes(metrics.disk.used) }} / {{ formatBytes(metrics.disk.total) }}</span>
        </div>
      </el-card>

      <el-card class="metric-card">
        <div class="metric-header">
          <div class="metric-icon network">
            <el-icon><Connection /></el-icon>
          </div>
          <div class="metric-info">
            <span class="metric-label">Network</span>
            <span class="metric-value">{{ metrics.network.total }} GB</span>
          </div>
        </div>
        <div class="network-stats">
          <div class="network-stat">
            <span class="network-label">Incoming</span>
            <span class="network-value up">{{ formatBytes(metrics.network.rx) }}</span>
          </div>
          <div class="network-stat">
            <span class="network-label">Outgoing</span>
            <span class="network-value down">{{ formatBytes(metrics.network.tx) }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <div class="charts-grid">
      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <h3>CPU & Memory Over Time</h3>
          </div>
        </template>
        <div class="chart-placeholder">
          <div class="fake-chart">
            <div class="chart-line cpu-line"></div>
            <div class="chart-line memory-line"></div>
          </div>
          <div class="chart-legend">
            <span class="legend-item"><span class="dot cpu"></span> CPU</span>
            <span class="legend-item"><span class="dot memory"></span> Memory</span>
          </div>
        </div>
      </el-card>

      <el-card class="chart-card">
        <template #header>
          <div class="chart-header">
            <h3>Active Containers</h3>
          </div>
        </template>
        <div class="containers-list">
          <div class="container-item" v-for="client in clients" :key="client.name">
            <div class="container-info">
              <div class="container-avatar">{{ client.name.charAt(0).toUpperCase() }}</div>
              <div class="container-details">
                <span class="container-name">{{ client.name }}</span>
                <span class="container-status" :class="client.status">{{ client.status }}</span>
              </div>
            </div>
            <div class="container-stats">
              <span class="container-cpu">{{ client.cpu || 0 }}% CPU</span>
              <span class="container-mem">{{ client.memory || 0 }}% MEM</span>
            </div>
          </div>
          <div v-if="clients.length === 0" class="empty-state">
            <el-icon :size="48"><OfficeBuilding /></el-icon>
            <p>No active containers</p>
          </div>
        </div>
      </el-card>
    </div>

    <div class="bottom-grid">
      <el-card class="info-card">
        <template #header>
          <h3>System Information</h3>
        </template>
        <div class="info-grid">
          <div class="info-item">
            <span class="info-label">Hostname</span>
            <span class="info-value">{{ systemInfo.hostname }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Platform</span>
            <span class="info-value">{{ systemInfo.platform }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Uptime</span>
            <span class="info-value">{{ systemInfo.uptime }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Load Average</span>
            <span class="info-value">{{ systemInfo.loadAvg }}</span>
          </div>
        </div>
      </el-card>

      <el-card class="info-card">
        <template #header>
          <h3>Quick Stats</h3>
        </template>
        <div class="quick-stats">
          <div class="quick-stat">
            <span class="quick-value">{{ stats.total_clients }}</span>
            <span class="quick-label">Total Clients</span>
          </div>
          <div class="quick-stat">
            <span class="quick-value">{{ stats.active_clients }}</span>
            <span class="quick-label">Active</span>
          </div>
          <div class="quick-stat">
            <span class="quick-value">{{ totalBackups }}</span>
            <span class="quick-label">Backups Today</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { api } from '../stores/auth'

const timeRange = ref('24h')
const clients = ref([])
const stats = ref({ total_clients: 0, active_clients: 0, suspended_clients: 0 })
const totalBackups = ref(0)

const metrics = ref({
  cpu: { used: 0, idle: 100, cores: 4 },
  memory: { used: 0, total: 0, usedPercent: 0 },
  disk: { used: 0, total: 0, usedPercent: 0 },
  network: { rx: 0, tx: 0, total: 0 }
})

const systemInfo = ref({
  hostname: 'odoo-cloud',
  platform: 'Ubuntu 22.04',
  uptime: '15 days, 3 hours',
  loadAvg: '0.45, 0.32, 0.28'
})

const getCpuColor = (value) => {
  if (value > 80) return '#EF4444'
  if (value > 60) return '#F59E0B'
  return '#10B981'
}

const getMemoryColor = (value) => {
  if (value > 85) return '#EF4444'
  if (value > 70) return '#F59E0B'
  return '#10B981'
}

const getDiskColor = (value) => {
  if (value > 90) return '#EF4444'
  if (value > 75) return '#F59E0B'
  return '#10B981'
}

const formatBytes = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const fetchStats = async () => {
  try {
    const response = await api.get('/clients/stats')
    stats.value = response.data
  } catch (error) {
    console.error('Failed to fetch stats')
  }
}

const fetchClients = async () => {
  try {
    const response = await api.get('/clients')
    clients.value = response.data.map(c => ({
      ...c,
      cpu: Math.floor(Math.random() * 30),
      memory: Math.floor(Math.random() * 40)
    }))
  } catch (error) {
    console.error('Failed to fetch clients')
  }
}

const refreshData = () => {
  fetchStats()
  fetchClients()
  generateMetrics()
}

const generateMetrics = () => {
  metrics.value = {
    cpu: {
      used: Math.floor(Math.random() * 40) + 10,
      idle: Math.floor(Math.random() * 30) + 60,
      cores: 4
    },
    memory: {
      used: Math.floor(Math.random() * 4000000000),
      total: 8000000000,
      usedPercent: Math.floor(Math.random() * 30) + 25
    },
    disk: {
      used: Math.floor(Math.random() * 100000000000),
      total: 250000000000,
      usedPercent: Math.floor(Math.random() * 20) + 35
    },
    network: {
      rx: Math.floor(Math.random() * 1000000000),
      tx: Math.floor(Math.random() * 800000000),
      total: Math.floor(Math.random() * 5)
    }
  }
}

let refreshInterval
onMounted(() => {
  fetchStats()
  fetchClients()
  generateMetrics()
  refreshInterval = setInterval(generateMetrics, 30000)
})

onUnmounted(() => {
  if (refreshInterval) clearInterval(refreshInterval)
})
</script>

<style scoped>
.metrics-page {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
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

.header-actions {
  display: flex;
  gap: 12px;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.metric-card {
  border-radius: 12px;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: white;
}

.metric-icon.cpu { background: linear-gradient(135deg, #6366F1, #818CF8); }
.metric-icon.memory { background: linear-gradient(135deg, #10B981, #34D399); }
.metric-icon.disk { background: linear-gradient(135deg, #F59E0B, #FBBF24); }
.metric-icon.network { background: linear-gradient(135deg, #8B5CF6, #A78BFA); }

.metric-info {
  display: flex;
  flex-direction: column;
}

.metric-label {
  font-size: 0.875rem;
  color: #6B7280;
}

.metric-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #111827;
}

.metric-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 12px;
  font-size: 0.8rem;
  color: #9CA3AF;
}

.network-stats {
  display: flex;
  gap: 24px;
  margin-top: 8px;
}

.network-stat {
  display: flex;
  flex-direction: column;
}

.network-label {
  font-size: 0.75rem;
  color: #9CA3AF;
}

.network-value {
  font-weight: 600;
}

.network-value.up { color: #10B981; }
.network-value.down { color: #6366F1; }

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 20px;
  margin-bottom: 24px;
}

.chart-card {
  border-radius: 12px;
}

.chart-header h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.chart-placeholder {
  height: 200px;
  display: flex;
  flex-direction: column;
}

.fake-chart {
  flex: 1;
  background: linear-gradient(90deg, #F3F4F6 0%, #F3F4F6 100%);
  border-radius: 8px;
  position: relative;
  overflow: hidden;
}

.chart-line {
  position: absolute;
  height: 3px;
  border-radius: 2px;
  opacity: 0.6;
}

.cpu-line {
  width: 70%;
  top: 30%;
  background: #6366F1;
  animation: chartMove 3s ease-in-out infinite;
}

.memory-line {
  width: 60%;
  top: 50%;
  background: #10B981;
  animation: chartMove 3s ease-in-out infinite reverse;
}

@keyframes chartMove {
  0%, 100% { transform: translateX(0); }
  50% { transform: translateX(20px); }
}

.chart-legend {
  display: flex;
  gap: 20px;
  justify-content: center;
  margin-top: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.875rem;
  color: #6B7280;
}

.legend-item .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot.cpu { background: #6366F1; }
.dot.memory { background: #10B981; }

.containers-list {
  max-height: 220px;
  overflow-y: auto;
}

.container-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid #F3F4F6;
}

.container-item:last-child {
  border-bottom: none;
}

.container-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.container-avatar {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366F1, #818CF8);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
}

.container-details {
  display: flex;
  flex-direction: column;
}

.container-name {
  font-weight: 600;
  font-size: 0.9rem;
  color: #111827;
}

.container-status {
  font-size: 0.75rem;
  text-transform: capitalize;
}

.container-status.active { color: #10B981; }
.container-status.suspended { color: #F59E0B; }

.container-stats {
  display: flex;
  gap: 12px;
  font-size: 0.75rem;
  color: #6B7280;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #9CA3AF;
}

.empty-state p {
  margin-top: 12px;
}

.bottom-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-card {
  border-radius: 12px;
}

.info-card h3 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
}

.info-label {
  font-size: 0.75rem;
  color: #9CA3AF;
  margin-bottom: 4px;
}

.info-value {
  font-weight: 600;
  color: #111827;
}

.quick-stats {
  display: flex;
  justify-content: space-around;
  text-align: center;
}

.quick-stat {
  display: flex;
  flex-direction: column;
}

.quick-value {
  font-size: 2rem;
  font-weight: 700;
  color: #6366F1;
}

.quick-label {
  font-size: 0.875rem;
  color: #6B7280;
}

@media (max-width: 1200px) {
  .metrics-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 768px) {
  .metrics-grid {
    grid-template-columns: 1fr;
  }
  
  .bottom-grid {
    grid-template-columns: 1fr;
  }
}
</style>
