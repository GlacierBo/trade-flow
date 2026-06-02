<script setup>
import { ref, computed, onMounted } from 'vue'
import { useStockStore } from '../../stores/stock'

const store = useStockStore()
const resetTargetId = ref(null)
const resetResult = ref('')

const totalPages = computed(() => Math.max(1, Math.ceil(store.usersTotal / 20)))

onMounted(() => {
  store.loadUsers(1)
})

function goPage(p) {
  if (p < 1 || p > totalPages.value) return
  store.loadUsers(p)
  resetTargetId.value = null
  resetResult.value = ''
}

async function handleReset(userId) {
  resetResult.value = ''
  const pw = await store.resetUserPassword(userId)
  if (pw) {
    resetResult.value = pw
    resetTargetId.value = userId
  }
}
</script>

<template>
  <div>
    <div class="bg-gray-800/50 rounded-2xl border border-gray-700/50 overflow-hidden">
      <div class="p-4 border-b border-gray-700/50">
        <h2 class="text-lg font-black text-blue-400">用户管理</h2>
      </div>

      <div v-if="store.users.length === 0" class="text-center py-12 text-gray-500 text-sm">
        暂无用户
      </div>

      <div v-else class="p-4">
        <table class="w-full text-sm">
          <thead>
            <tr class="text-gray-500 text-xs uppercase tracking-wider border-b border-gray-700/50">
              <th class="text-left py-3 px-2 font-bold">ID</th>
              <th class="text-left py-3 px-2 font-bold">用户名</th>
              <th class="text-left py-3 px-2 font-bold">角色</th>
              <th class="text-left py-3 px-2 font-bold">注册时间</th>
              <th class="text-right py-3 px-2 font-bold">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-700/30">
            <tr v-for="u in store.users" :key="u.id" class="hover:bg-gray-700/10 transition-colors">
              <td class="py-3 px-2 text-gray-400 font-mono text-xs">{{ u.id }}</td>
              <td class="py-3 px-2">
                <span class="text-gray-100 font-bold">{{ u.username }}</span>
              </td>
              <td class="py-3 px-2">
                <span
                  :class="u.role === 'admin' ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30' : 'bg-gray-600/30 text-gray-400 border-gray-600/30'"
                  class="text-xs px-2 py-0.5 rounded font-bold border"
                >{{ u.role }}</span>
              </td>
              <td class="py-3 px-2 text-gray-400 text-xs">{{ u.created_at ? new Date(u.created_at).toLocaleString() : '-' }}</td>
              <td class="py-3 px-2 text-right">
                <button
                  @click="handleReset(u.id)"
                  class="bg-yellow-500/10 hover:bg-yellow-500/20 text-yellow-400 px-3 py-1.5 rounded-lg text-xs font-bold border border-yellow-500/30 transition-all active:scale-95"
                >重置密码</button>
              </td>
            </tr>
          </tbody>
        </table>

        <!-- 重置结果 -->
        <div v-if="resetResult" class="mt-4 p-3 bg-green-500/10 border border-green-500/30 rounded-lg text-center">
          <p class="text-green-400 text-sm font-bold mb-1">密码已重置</p>
          <p class="text-gray-300 font-mono text-lg font-black tracking-wider">{{ resetResult }}</p>
        </div>

        <!-- 分页 -->
        <div class="flex items-center justify-between mt-4 pt-4 border-t border-gray-700/50">
          <span class="text-xs text-gray-500">共 {{ store.usersTotal }} 位用户</span>
          <div class="flex items-center gap-2">
            <button
              @click="goPage(store.usersPage - 1)"
              :disabled="store.usersPage <= 1"
              class="bg-gray-700 hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed text-gray-300 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95"
            >上一页</button>
            <span class="text-xs text-gray-400 px-2">{{ store.usersPage }} / {{ totalPages }}</span>
            <button
              @click="goPage(store.usersPage + 1)"
              :disabled="store.usersPage >= totalPages"
              class="bg-gray-700 hover:bg-gray-600 disabled:opacity-30 disabled:cursor-not-allowed text-gray-300 px-3 py-1.5 rounded-lg text-xs font-bold transition-all active:scale-95"
            >下一页</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
