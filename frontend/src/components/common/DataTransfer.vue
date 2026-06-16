<script setup>
import { ref } from 'vue'

const props = defineProps({
  pageName: { type: String, default: '' },
  getExportData: { type: Function, required: true },
  onImport: { type: Function, required: true },
})

const emit = defineEmits(['imported'])
const showImport = ref(false)
const importText = ref('')
const importError = ref('')
const importing = ref(false)
const copied = ref(false)

async function handleExport() {
  const data = props.getExportData()
  const json = JSON.stringify(data, null, 2)
  try {
    await navigator.clipboard.writeText(json)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  } catch {
    // Fallback for non-HTTPS
    const ta = document.createElement('textarea')
    ta.value = json
    document.body.appendChild(ta)
    ta.select()
    document.execCommand('copy')
    document.body.removeChild(ta)
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  }
}

function openImport() {
  importText.value = ''
  importError.value = ''
  showImport.value = true
}

async function handleImport() {
  importError.value = ''
  importing.value = true
  try {
    let data
    try {
      data = JSON.parse(importText.value)
    } catch {
      throw new Error('JSON 格式错误，请检查后重试')
    }
    if (!data || typeof data !== 'object') {
      throw new Error('无效的 JSON 数据')
    }
    await props.onImport(data)
    showImport.value = false
    emit('imported')
  } catch (e) {
    importError.value = e.message || '导入失败'
  } finally {
    importing.value = false
  }
}
</script>

<template>
  <div class="flex items-center gap-2">
    <!-- Export button -->
    <button
      class="relative w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700/50 transition-all active:scale-90"
      @click="handleExport"
      :title="copied ? '已复制!' : '导出 JSON'"
      aria-label="导出 JSON"
    >
      <svg v-if="copied" class="w-4 h-4 text-green-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <polyline points="20 6 9 17 4 12" />
      </svg>
      <svg v-else class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="7 10 12 15 17 10" />
        <line x1="12" y1="15" x2="12" y2="3" />
      </svg>
    </button>

    <!-- Import button -->
    <button
      class="w-7 h-7 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700/50 transition-all active:scale-90"
      @click="openImport"
      aria-label="导入数据"
    >
      <svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
        <polyline points="17 8 12 3 7 8" />
        <line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    </button>

    <!-- Import modal -->
    <Teleport to="body">
      <div
        v-if="showImport"
        class="fixed inset-0 bg-black/70 backdrop-blur-sm flex items-center justify-center p-4 z-50 overscroll-contain"

      >
        <div class="bg-gray-800 border border-gray-700 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl animate-fadeIn">
          <div class="flex items-center justify-between px-5 py-4 border-b border-gray-700/50">
            <h3 class="text-base font-black text-gray-100">导入{{ pageName }}数据</h3>
            <button
              class="w-8 h-8 flex items-center justify-center rounded-lg text-gray-400 hover:text-gray-100 hover:bg-gray-700 transition-colors"
              @click="showImport = false"
            >
              <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </button>
          </div>
          <div class="p-5">
            <label class="text-xs text-gray-400 font-bold mb-2 block">粘贴 JSON 数据</label>
            <textarea
              v-model="importText"
              class="w-full bg-gray-700/50 border border-gray-600 rounded-xl px-4 py-3 text-sm text-gray-100 placeholder-gray-500 outline-none focus:border-blue-500 resize-y font-mono"
              :class="{ 'border-red-500/50': importError }"
              rows="14"
              placeholder='请粘贴从导出功能复制的 JSON 数据…
例如：
{
  "contracts": [
    { "code": "IF2406", "name": "沪深300主力" }
  ]
}'
              spellcheck="false"
            ></textarea>
            <p v-if="importError" class="text-red-400 text-xs mt-1.5 flex items-center gap-1">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" class="flex-shrink-0">
                <circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {{ importError }}
            </p>
          </div>
          <div class="flex gap-3 px-5 pb-5">
            <button
              class="flex-1 py-2.5 bg-gray-700 hover:bg-gray-600 rounded-xl text-gray-300 font-bold text-sm transition-all"
              @click="showImport = false"
            >取消</button>
            <button
              class="flex-1 py-2.5 bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-500 hover:to-blue-400 rounded-xl text-white font-bold text-sm transition-all disabled:opacity-50"
              :disabled="!importText.trim() || importing"
              @click="handleImport"
            >
              {{ importing ? '导入中…' : '确定导入' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>
