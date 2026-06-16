<script setup>
import { ref } from 'vue'
import { useStockStore } from '../../stores/stock'

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
  <div class="min-h-screen bg-gray-900 flex relative overflow-hidden">
    <!-- Animated background grid -->
    <div class="fixed inset-0 pointer-events-none opacity-[0.03]">
      <div
        class="absolute inset-0"
        style="background-image: linear-gradient(rgba(96,165,250,1) 1px, transparent 1px), linear-gradient(90deg, rgba(96,165,250,1) 1px, transparent 1px); background-size: 60px 60px;"
      />
    </div>

    <!-- Ambient glow orbs -->
    <div class="fixed inset-0 pointer-events-none overflow-hidden">
      <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-float" />
      <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl animate-float" style="animation-delay: 2s;" />
      <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-400/5 rounded-full blur-3xl animate-spin-slow" />
    </div>

    <!-- Left: Brand Panel -->
    <div class="hidden lg:flex lg:w-1/2 relative items-center justify-center">
      <div class="relative z-10 text-center px-12">
        <!-- Logo icon with glow -->
        <div class="relative inline-flex mb-8">
          <div class="w-24 h-24 bg-gradient-to-br from-blue-500 via-blue-400 to-purple-600 rounded-3xl shadow-2xl shadow-blue-500/30 flex items-center justify-center relative overflow-hidden">
            <div class="absolute inset-0 bg-white/10 rounded-3xl" />
            <svg class="w-14 h-14 text-white relative z-10" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
            </svg>
          </div>
          <!-- Glow ring -->
          <div class="absolute -inset-3 rounded-3xl bg-gradient-to-br from-blue-400/20 to-purple-500/20 blur-xl -z-10" />
        </div>

        <h1 class="text-5xl font-black text-white mb-3 tracking-tight">TradeFlow</h1>
        <p class="text-transparent bg-clip-text bg-gradient-to-r from-blue-300 to-purple-300 text-base uppercase tracking-[0.3em] font-bold mb-8">
          Smart Trading Management
        </p>

        <!-- Feature highlights -->
        <div class="space-y-4 max-w-xs mx-auto">
          <div class="flex items-center gap-3 text-left">
            <div class="w-8 h-8 rounded-lg bg-blue-500/10 border border-blue-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
            </div>
            <p class="text-gray-400 text-sm">网格交易策略管理</p>
          </div>
          <div class="flex items-center gap-3 text-left">
            <div class="w-8 h-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" /></svg>
            </div>
            <p class="text-gray-400 text-sm">实时持仓盈亏追踪</p>
          </div>
          <div class="flex items-center gap-3 text-left">
            <div class="w-8 h-8 rounded-lg bg-purple-500/10 border border-purple-500/20 flex items-center justify-center flex-shrink-0">
              <svg class="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" /></svg>
            </div>
            <p class="text-gray-400 text-sm">自选股价格实时监控</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Right: Login Form -->
    <div class="flex-1 flex items-center justify-center p-8 relative z-10">
      <div class="w-full max-w-md">
        <!-- Mobile Logo -->
        <div class="lg:hidden text-center mb-10">
          <div class="relative inline-flex mb-4">
            <div class="w-20 h-20 bg-gradient-to-br from-blue-500 via-blue-400 to-purple-600 rounded-2xl shadow-2xl shadow-blue-500/30 flex items-center justify-center">
              <svg class="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" style="filter: drop-shadow(0 2px 4px rgba(0,0,0,0.3));">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
              </svg>
            </div>
          </div>
          <h1 class="text-3xl font-black text-white mb-1">TradeFlow</h1>
          <p class="text-gray-400 text-xs uppercase tracking-widest font-bold">Smart Trading Management</p>
        </div>

        <!-- Form Card -->
        <div class="bg-gray-800/40 backdrop-blur-xl border border-gray-700/30 rounded-3xl p-8 shadow-2xl shadow-black/30">
          <h2 class="text-2xl font-black text-white mb-1">
            {{ tab === 'login' ? '欢迎回来' : '创建账户' }}
          </h2>
          <p class="text-gray-500 text-sm mb-6">
            {{ tab === 'login' ? '请输入您的账号信息登录系统' : '注册后系统将自动生成密码' }}
          </p>

          <!-- Tabs -->
          <div class="flex mb-6 bg-gray-800/60 rounded-xl p-1 border border-gray-700/20">
            <button
              @click="tab = 'login'; error = ''"
              :class="[
                'flex-1 py-2.5 rounded-lg text-sm font-black transition-all duration-200',
                tab === 'login'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-400 text-white shadow-lg shadow-blue-500/25'
                  : 'text-gray-400 hover:text-gray-200'
              ]"
            >登录</button>
            <button
              @click="tab = 'register'; error = ''; generatedPassword = ''"
              :class="[
                'flex-1 py-2.5 rounded-lg text-sm font-black transition-all duration-200',
                tab === 'register'
                  ? 'bg-gradient-to-r from-blue-500 to-blue-400 text-white shadow-lg shadow-blue-500/25'
                  : 'text-gray-400 hover:text-gray-200'
              ]"
            >注册</button>
          </div>

          <!-- Error -->
          <transition name="msg">
            <div v-if="error" class="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400 text-sm text-center">
              {{ error }}
            </div>
          </transition>

          <!-- Register Success -->
          <transition name="msg">
            <div v-if="generatedPassword" class="mb-4 p-5 bg-gradient-to-br from-green-500/10 to-emerald-500/5 border border-green-500/20 rounded-2xl text-center">
              <div class="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-3">
                <svg class="w-6 h-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12" /></svg>
              </div>
              <p class="text-green-400 text-sm font-bold mb-2">注册成功！</p>
              <p class="text-gray-300 text-xs mb-2">用户名：<span class="font-bold font-mono">{{ registeredUsername }}</span></p>
              <div class="bg-gray-900/60 backdrop-blur-sm rounded-xl px-4 py-3 border border-gray-700/30">
                <p class="text-gray-500 text-xs mb-1">临时密码</p>
                <p class="text-white font-mono text-lg font-black tracking-wider">{{ generatedPassword }}</p>
              </div>
              <p class="text-gray-500 text-xs mt-3">请用此密码登录，登录后可在用户菜单中修改密码</p>
              <button
                @click="tab = 'login'; generatedPassword = ''; username = registeredUsername"
                class="mt-3 text-blue-400 text-sm font-bold hover:text-blue-300 transition-colors inline-flex items-center gap-1"
              >
                前往登录
                <svg class="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
              </button>
            </div>
          </transition>

          <!-- Login Form -->
          <form v-if="tab === 'login' && !generatedPassword" @submit.prevent="handleLogin" class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-gray-300 mb-2">用户名</label>
              <input
                v-model="username"
                type="text"
                placeholder="字母和数字"
                class="w-full bg-gray-700/30 border border-gray-600/40 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none transition-all duration-200 focus:border-blue-500/50 focus:bg-gray-700/50 focus:ring-0"
                :disabled="loading"
                required
                autocomplete="username"
              >
            </div>
            <div>
              <label class="block text-sm font-bold text-gray-300 mb-2">密码</label>
              <input
                v-model="password"
                type="password"
                placeholder="请输入密码"
                class="w-full bg-gray-700/30 border border-gray-600/40 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none transition-all duration-200 focus:border-blue-500/50 focus:bg-gray-700/50"
                :disabled="loading"
                required
                autocomplete="current-password"
              >
            </div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 disabled:from-gray-600 disabled:to-gray-500 text-white font-black py-3.5 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 active:scale-[0.98] disabled:cursor-not-allowed disabled:shadow-none mt-2 relative overflow-hidden group"
            >
              <span class="relative z-10">
                <span v-if="!loading" class="inline-flex items-center gap-2">
                  登 录
                  <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
                </span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  登录中…
                </span>
              </span>
              <!-- Shimmer overlay -->
              <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            </button>
          </form>

          <!-- Register Form -->
          <form v-if="tab === 'register' && !generatedPassword" @submit.prevent="handleRegister" class="space-y-5">
            <div>
              <label class="block text-sm font-bold text-gray-300 mb-2">用户名</label>
              <input
                v-model="username"
                type="text"
                placeholder="字母和数字，不支持特殊符号"
                class="w-full bg-gray-700/30 border border-gray-600/40 rounded-xl px-4 py-3.5 text-white placeholder-gray-500 outline-none transition-all duration-200 focus:border-blue-500/50 focus:bg-gray-700/50"
                :disabled="loading"
                required
              >
            </div>
            <div class="bg-blue-500/5 border border-blue-500/20 rounded-xl p-3">
              <p class="text-xs text-gray-400 flex items-start gap-2">
                <svg class="w-3.5 h-3.5 text-blue-400 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg>
                <span>注册后系统将自动生成密码，请妥善保管</span>
              </p>
            </div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 disabled:from-gray-600 disabled:to-gray-500 text-white font-black py-3.5 rounded-xl shadow-lg shadow-blue-500/30 transition-all duration-200 active:scale-[0.98] disabled:cursor-not-allowed disabled:shadow-none mt-2 relative overflow-hidden group"
            >
              <span class="relative z-10">
                <span v-if="!loading" class="inline-flex items-center gap-2">
                  注 册
                  <svg class="w-4 h-4 transition-transform group-hover:translate-x-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" /></svg>
                </span>
                <span v-else class="flex items-center justify-center">
                  <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  注册中…
                </span>
              </span>
              <div class="absolute inset-0 -translate-x-full group-hover:translate-x-full transition-transform duration-700 bg-gradient-to-r from-transparent via-white/10 to-transparent" />
            </button>
          </form>
        </div>

        <!-- Footer -->
        <p class="text-center text-gray-600 text-xs mt-6">
          TradeFlow v2.0 &mdash; Smart Trading Management
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.msg-enter-active,
.msg-leave-active {
  transition: all 0.3s ease;
}
.msg-enter-from,
.msg-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
