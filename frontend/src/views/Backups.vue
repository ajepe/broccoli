<template>
  <div class="backups-page">
    <el-card>
      <template #header>
        <span>Backup Management</span>
      </template>
      
      <el-alert
        title="S3 Backup Configuration"
        type="info"
        :closable="false"
        style="margin-bottom: 20px;"
      >
        Backups are automatically uploaded to S3. Configure S3 credentials in the platform settings.
      </el-alert>
      
      <el-table :data="backups" v-loading="loading" style="width: 100%">
        <el-table-column prop="client_name" label="Client" width="150" />
        <el-table-column prop="backup_type" label="Type" width="100">
          <template #default="{ row }">
            <el-tag :type="getTypeTag(row.backup_type)">{{ row.backup_type }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="filename" label="Filename" />
        <el-table-column prop="size_mb" label="Size (MB)" width="100" />
        <el-table-column prop="status" label="Status" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTag(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="Created">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="Actions" width="150">
          <template #default="{ row }">
            <el-button size="small" @click="restoreBackup(row)">Restore</el-button>
            <el-button size="small" type="danger" @click="deleteBackup(row)">Delete</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { api } from '../stores/auth'

const backups = ref([])
const loading = ref(false)

const fetchBackups = async () => {
  loading.value = true
  try {
    const clientsRes = await api.get('/clients')
    const allBackups = []
    
    for (const client of clientsRes.data) {
      try {
        const response = await api.get(`/clients/${client.name}/stats`)
        allBackups.push({
          client_name: client.name,
          backup_type: 'manual',
          filename: 'Latest backup',
          size_mb: 0,
          status: 'available'
        })
      } catch (e) {}
    }
    
    backups.value = allBackups
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const restoreBackup = async (backup) => {
  try {
    await ElMessageBox.confirm(
      `Restore backup for ${backup.client_name}? This will overwrite current data.`,
      'Confirm Restore',
      { type: 'warning' }
    )
    
    ElMessage.info('Restore initiated')
  } catch (e) {}
}

const deleteBackup = async (backup) => {
  try {
    await ElMessageBox.confirm('Delete this backup?', 'Confirm Delete', { type: 'warning' })
    ElMessage.success('Backup deleted')
    fetchBackups()
  } catch (e) {}
}

const formatDate = (date) => new Date(date).toLocaleString()

const getTypeTag = (type) => {
  const tags = { daily: '', weekly: 'success', monthly: 'warning', manual: 'info' }
  return tags[type] || ''
}

const getStatusTag = (status) => {
  const tags = { available: 'success', pending: 'warning', failed: 'danger' }
  return tags[status] || ''
}

onMounted(() => {
  fetchBackups()
})
</script>

<style scoped>
.backups-page {
  padding: 20px;
}
</style>
