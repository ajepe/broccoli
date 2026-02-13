<template>
  <el-container class="app-container">
    <el-aside v-if="isAuthenticated" width="220px" class="sidebar">
      <div class="logo">
        <h2>Odoo Cloud</h2>
        <span>Africa Platform</span>
      </div>
      <el-menu
        :default-active="currentRoute"
        class="el-menu-vertical"
        :router="true"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </el-menu-item>
        <el-menu-item index="/clients">
          <el-icon><OfficeBuilding /></el-icon>
          <span>Clients</span>
        </el-menu-item>
        <el-menu-item index="/backups">
          <el-icon><FolderOpened /></el-icon>
          <span>Backups</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    
    <el-container>
      <el-header v-if="isAuthenticated" class="header">
        <div class="header-left">
          <h3>{{ pageTitle }}</h3>
        </div>
        <div class="header-right">
          <el-dropdown @command="handleCommand">
            <span class="user-info">
              <el-icon><User /></el-icon>
              <span>{{ username }}</span>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="logout">Logout</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>
      
      <el-main class="main-content">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)
const username = computed(() => authStore.user?.username || 'Admin')
const currentRoute = computed(() => route.path)

const pageTitle = computed(() => {
  const titles = {
    '/': 'Dashboard',
    '/clients': 'Client Management',
    '/clients/new': 'Create Client',
    '/backups': 'Backup Management'
  }
  if (route.params.name) {
    return `Client: ${route.params.name}`
  }
  return titles[route.path] || 'Odoo Cloud'
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
}

.app-container {
  height: 100%;
}

.sidebar {
  background: #1a1a2e;
  color: #fff;
}

.logo {
  padding: 20px;
  text-align: center;
  border-bottom: 1px solid #16213e;
}

.logo h2 {
  color: #00d9ff;
  font-size: 1.5rem;
}

.logo span {
  color: #a0a0a0;
  font-size: 0.8rem;
}

.el-menu-vertical {
  border: none;
  background: #1a1a2e;
}

.el-menu-item {
  color: #fff;
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background: #16213e !important;
  color: #00d9ff !important;
}

.header {
  background: #fff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  border-bottom: 1px solid #e4e7ed;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.header-left h3 {
  color: #303133;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.main-content {
  background: #f5f7fa;
  min-height: calc(100vh - 60px);
}
</style>
