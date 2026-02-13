<template>
  <div class="app-wrapper">
    <header class="navbar" v-if="isAuthenticated">
      <div class="navbar-brand">
        <div class="logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <rect width="32" height="32" rx="8" fill="#6366F1"/>
            <path d="M8 16C8 11.5817 11.5817 8 16 8V8C20.4183 8 24 11.5817 24 16V16C24 20.4183 20.4183 24 16 24V24" stroke="white" stroke-width="3" stroke-linecap="round"/>
            <circle cx="16" cy="16" r="4" fill="white"/>
          </svg>
          <span class="brand-text">Odoo<span class="brand-accent">Cloud</span></span>
        </div>
      </div>
      
      <nav class="navbar-nav">
        <router-link to="/" class="nav-link" :class="{ active: currentRoute === '/' }">
          <el-icon><HomeFilled /></el-icon>
          <span>Dashboard</span>
        </router-link>
        <router-link to="/clients" class="nav-link" :class="{ active: currentRoute.startsWith('/clients') }">
          <el-icon><OfficeBuilding /></el-icon>
          <span>Clients</span>
        </router-link>
        <router-link to="/backups" class="nav-link" :class="{ active: currentRoute === '/backups' }">
          <el-icon><FolderOpened /></el-icon>
          <span>Backups</span>
        </router-link>
      </nav>
      
      <div class="navbar-actions">
        <el-dropdown @command="handleCommand" trigger="click">
          <div class="user-menu">
            <div class="avatar">{{ userInitials }}</div>
            <span class="username">{{ username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                Profile
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                Settings
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                Logout
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </header>
    
    <main class="main-content" :class="{ 'no-navbar': !isAuthenticated }">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
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

const userInitials = computed(() => {
  const name = username.value || 'Admin'
  return name.charAt(0).toUpperCase()
})

const handleCommand = (command) => {
  if (command === 'logout') {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #6366F1;
  --primary-dark: #4F46E5;
  --primary-light: #818CF8;
  --secondary: #10B981;
  --warning: #F59E0B;
  --danger: #EF4444;
  --dark: #1F2937;
  --dark-light: #374151;
  --gray: #6B7280;
  --gray-light: #9CA3AF;
  --gray-lighter: #F3F4F6;
  --white: #FFFFFF;
  --bg: #F9FAFB;
  --border: #E5E7EB;
  --shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --radius: 12px;
  --radius-sm: 8px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg);
  color: var(--dark);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
}

.app-wrapper {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  background: var(--white);
  border-bottom: 1px solid var(--border);
  padding: 0 24px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow);
}

.navbar-brand {
  display: flex;
  align-items: center;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.brand-text {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--dark);
}

.brand-accent {
  color: var(--primary);
}

.navbar-nav {
  display: flex;
  align-items: center;
  gap: 8px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-sm);
  color: var(--gray);
  text-decoration: none;
  font-weight: 500;
  font-size: 0.9rem;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background: var(--gray-lighter);
  color: var(--dark);
}

.nav-link.active {
  background: rgba(99, 102, 241, 0.1);
  color: var(--primary);
}

.navbar-actions {
  display: flex;
  align-items: center;
}

.user-menu {
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  padding: 6px 12px;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}

.user-menu:hover {
  background: var(--gray-lighter);
}

.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary) 0%, var(--primary-light) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.9rem;
}

.username {
  font-weight: 500;
  color: var(--dark);
}

.main-content {
  flex: 1;
  padding: 32px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.main-content.no-navbar {
  max-width: 100%;
  padding: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Override Element Plus */
.el-button--primary {
  --el-button-bg-color: var(--primary);
  --el-button-border-color: var(--primary);
  --el-button-hover-bg-color: var(--primary-dark);
  --el-button-hover-border-color: var(--primary-dark);
}

.el-card {
  --el-card-border-radius: var(--radius);
  border: 1px solid var(--border);
  box-shadow: var(--shadow);
}

.el-input__wrapper {
  border-radius: var(--radius-sm);
}

.el-input__wrapper:focus-within {
  box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
}

.el-menu-item:hover,
.el-menu-item.is-active {
  background: transparent !important;
}
</style>
