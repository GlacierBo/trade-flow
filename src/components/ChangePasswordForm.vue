<script setup>
import { ref } from 'vue'
import { useStockStore } from '../stores/stock'

const store = useStockStore()

const oldPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  if (!oldPassword.value || !newPassword.value) {
    error.value = '请填写完整'
    return
  }
  if (newPassword.value.length < 6) {
    error.value = '新密码至少6位'
    return
  }
  if (newPassword.value !== confirmPassword.value) {
    error.value = '两次密码不一致'
    return
  }
  loading.value = true
  try {
    await store.changePassword(oldPassword.value, newPassword.value)
  } catch {
    error.value = '修改失败'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="bg-gray-800 rounded-2xl max-w-sm w-full p-5 shadow-2xl border border-gray-700 animate-fadeIn">
    <h3 class="text-lg font-black text-blue-400 mb-4">修改密码</h3>
    <div class="space-y-3">
      <div>
        <label class="block text-xs font-bold text-gray-400 mb-1">原密码</label>
        <input
          v-model="oldPassword"
          type="password"
          placeholder="输入原密码"
          class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
        >
      </div>
      <div>
        <label class="block text-xs font-bold text-gray-400 mb-1">新密码</label>
        <input
          v-model="newPassword"
          type="password"
          placeholder="至少6位"
          class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
        >
      </div>
      <div>
        <label class="block text-xs font-bold text-gray-400 mb-1">确认新密码</label>
        <input
          v-model="confirmPassword"
          type="password"
          placeholder="再次输入新密码"
          class="w-full bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 outline-none focus:border-blue-500 text-gray-100 text-sm placeholder-gray-500"
        >
      </div>
      <div v-if="error" class="text-red-400 text-xs text-center">{{ error }}</div>
    </div>
    <div class="flex gap-3 mt-5">
      <button
        @click="store.closePasswordModal()"
        class="flex-1 bg-gray-700 hover:bg-gray-600 py-2.5 rounded-xl text-gray-300 font-bold text-sm transition"
      >取消</button>
      <button
        @click="submit"
        :disabled="loading"
        :class="[
          'flex-1 py-2.5 rounded-xl text-white font-black text-sm shadow-lg transition',
          loading
            ? 'bg-gray-500 cursor-not-allowed opacity-50'
            : 'bg-gradient-to-r from-blue-500 to-blue-400 hover:from-blue-400 hover:to-blue-300 shadow-blue-500/30'
        ]"
      >{{ loading ? '提交中...' : '确认修改' }}</button>
    </div>
  </div>
</template>
