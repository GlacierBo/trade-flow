<script setup>
import { ref } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const tab = ref('login')
const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

const generatedPassword = ref('')
const registeredUsername = ref('')

function isValidUsername(v) {
  return /^[a-zA-Z0-9]+$/.test(v)
}

async function handleLogin() {
  error.value = ''
  if (!username.value.trim() || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  if (!isValidUsername(username.value.trim())) {
    error.value = '用户名只能包含字母和数字'
    return
  }
  loading.value = true
  try {
    const ok = await store.login(username.value.trim(), password.value)
    if (ok) {
      window.location.reload()
    } else {
      error.value = '用户名或密码错误'
    }
  } catch {
    error.value = '登录失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  error.value = ''
  if (!username.value.trim()) {
    error.value = '请填写用户名'
    return
  }
  if (!isValidUsername(username.value.trim())) {
    error.value = '用户名只能包含字母和数字'
    return
  }
  loading.value = true
  try {
    const pw = await store.register(username.value.trim())
    if (pw) {
      generatedPassword.value = pw
      registeredUsername.value = username.value.trim()
    }
  } catch {
    error.value = '注册失败，请稍后重试'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-gray-900 flex">
    <!-- Left: Brand Panel -->
    <div class="hidden lg:flex lg:w-1/2 relative overflow-hidden items-center justify-center bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500 rounded-full blur-3xl"></div>
        <div class="absolute bottom-1/4 right-1/4 w-64 h-64 bg-purple-500 rounded-full blur-3xl"></div>
      </div>
      <div class="relative z-10 text-center px-12">
        <div class="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-3xl shadow-2xl shadow-blue-500/30 mb-8">
          <svg class="w-14 h-14 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
          </svg>
        </div>
        <h1 class="text-5xl font-black text-white mb-3 tracking-tight">TradeFlow</h1>
        <p class="text-blue-400 text-base uppercase tracking-[0.3em] font-bold mb-8">Smart Trading Management</p>
        <p class="text-gray-400 text-lg leading-relaxed max-w-sm mx-auto">
          高效管理您的每一笔交易，<br>让投资决策更清晰、更从容。
        </p>
      </div>
    </div>

    <!-- Right: Login Form -->
    <div class="flex-1 flex items-center justify-center p-8">
      <div class="w-full max-w-md">
        <!-- Mobile Logo -->
        <div class="lg:hidden text-center mb-10">
          <div class="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-2xl shadow-blue-500/30 mb-4">
            <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <h1 class="text-3xl font-black text-white mb-1">TradeFlow</h1>
          <p class="text-gray-400 text-xs uppercase tracking-widest font-bold">Smart Trading Management</p>
        </div>

        <h2 class="text-2xl font-black text-white mb-2">欢迎回来</h2>
        <p class="text-gray-500 text-sm mb-8">请输入您的账号信息登录系统</p>

        <!-- Tabs -->
        <div class="flex mb-6 bg-gray-800/50 rounded-lg p-1">
          <button
            @click="tab = 'login'; error = ''"
            :class="['flex-1 py-2 rounded-md text-sm font-black transition-all', tab === 'login' ? 'bg-blue-500 text-white shadow' : 'text-gray-400 hover:text-gray-200']"
          >登录</button>
          <button
            @click="tab = 'register'; error = ''; generatedPassword = ''"
            :class="['flex-1 py-2 rounded-md text-sm font-black transition-all', tab === 'register' ? 'bg-blue-500 text-white shadow' : 'text-gray-400 hover:text-gray-200']"
          >注册</button>
        </div>

        <!-- Error -->
        <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm text-center">
          {{ error }}
        </div>

        <!-- Register Success -->
        <div v-if="generatedPassword" class="mb-4 p-4 bg-green-500/10 border border-green-500/30 rounded-lg text-center">
          <p class="text-green-400 text-sm font-bold mb-2">注册成功！</p>
          <p class="text-gray-300 text-xs mb-2">用户名：{{ registeredUsername }}</p>
          <div class="bg-gray-900/50 rounded-lg px-4 py-3">
            <p class="text-gray-500 text-xs mb-1">临时密码</p>
            <p class="text-white font-mono text-lg font-black tracking-wider">{{ generatedPassword }}</p>
          </div>
          <p class="text-gray-500 text-xs mt-3">请用此密码登录，登录后可在用户菜单中修改密码</p>
          <button
            @click="tab = 'login'; generatedPassword = ''; username = registeredUsername"
            class="mt-3 text-blue-400 text-sm font-bold hover:text-blue-300 transition"
          >前往登录</button>
        </div>

        <!-- Login Form -->
        <form v-else-if="tab === 'login'" @submit.prevent="handleLogin" class="space-y-5">
          <div>
            <label class="block text-sm font-bold text-gray-300 mb-2">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="字母和数字"
              class="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              :disabled="loading"
              required
            >
          </div>
          <div>
            <label class="block text-sm font-bold text-gray-300 mb-2">密码</label>
            <input
              v-model="password"
              type="password"
              placeholder="请输入密码"
              class="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              :disabled="loading"
              required
            >
          </div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 disabled:from-gray-600 disabled:to-gray-500 text-white font-black py-3.5 rounded-xl shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:cursor-not-allowed disabled:shadow-none mt-2"
          >
            <span v-if="!loading">登 录</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              登录中...
            </span>
          </button>
        </form>

        <!-- Register Form -->
        <form v-else @submit.prevent="handleRegister" class="space-y-5">
          <div>
            <label class="block text-sm font-bold text-gray-300 mb-2">用户名</label>
            <input
              v-model="username"
              type="text"
              placeholder="字母和数字，不支持特殊符号"
              class="w-full bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-500 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              :disabled="loading"
              required
            >
          </div>
          <p class="text-xs text-gray-500">注册后系统将自动生成密码，请妥善保管</p>
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 disabled:from-gray-600 disabled:to-gray-500 text-white font-black py-3.5 rounded-xl shadow-lg shadow-blue-500/30 transition-all active:scale-95 disabled:cursor-not-allowed disabled:shadow-none mt-2"
          >
            <span v-if="!loading">注 册</span>
            <span v-else class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              注册中...
            </span>
          </button>
        </form>
      </div>
    </div>
  </div>
</template>
