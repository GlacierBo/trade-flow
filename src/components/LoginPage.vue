<script setup>
import { ref } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const handleLogin = () => {
  error.value = ''
  loading.value = true

  // 模拟网络延迟
  setTimeout(() => {
    const success = store.login(username.value, password.value)
    
    if (success) {
      // 登录成功，页面会自动跳转到主应用
      window.location.reload()
    } else {
      error.value = '用户名或密码错误'
      loading.value = false
    }
  }, 500)
}

const handleKeyPress = (event) => {
  if (event.key === 'Enter') {
    handleLogin()
  }
}
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-4">
    <div class="w-full max-w-md">
      <!-- Logo and Title -->
      <div class="text-center mb-8">
        <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-2xl shadow-blue-500/30 mb-4">
          <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
          </svg>
        </div>
        <h1 class="text-4xl font-black text-white mb-2">TradeFlow</h1>
        <p class="text-gray-400 text-sm uppercase tracking-widest font-bold">Smart Trading Management</p>
      </div>

      <!-- Login Card -->
      <div class="bg-gray-800/50 backdrop-blur-xl rounded-2xl border border-gray-700/50 p-8 shadow-2xl">
        <h2 class="text-2xl font-black text-white mb-6 text-center">欢迎回来</h2>

        <!-- Error Message -->
        <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm text-center">
          {{ error }}
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-sm font-bold text-gray-300 mb-2">用户名</label>
            <input
              v-model="username"
              type="text"
              @keypress="handleKeyPress"
              placeholder="请输入用户名"
              class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              :disabled="loading"
              required
            >
          </div>

          <!-- Password -->
          <div>
            <label class="block text-sm font-bold text-gray-300 mb-2">密码</label>
            <input
              v-model="password"
              type="password"
              @keypress="handleKeyPress"
              placeholder="请输入密码"
              class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              :disabled="loading"
              required
            >
          </div>

          <!-- Login Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 disabled:from-gray-600 disabled:to-gray-500 text-white font-black py-3 rounded-xl shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:cursor-not-allowed disabled:shadow-none mt-6"
          >
            <span v-if="!loading">登 录</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              登录中...
            </span>
          </button>
        </form>

        <!-- Hint -->
        <div class="mt-6 pt-6 border-t border-gray-700/50">
          <p class="text-xs text-gray-500 text-center">
            默认账号：<span class="text-gray-400 font-mono">admin</span> / <span class="text-gray-400 font-mono">admin</span>
          </p>
        </div>
      </div>

      <!-- Footer -->
      <div class="text-center mt-6">
        <p class="text-xs text-gray-600">© 2024 TradeFlow. All rights reserved.</p>
      </div>
    </div>
  </div>
</template>
