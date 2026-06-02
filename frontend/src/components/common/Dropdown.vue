<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  modelValue: { type: String, default: '' },
  options: { type: Array, default: () => [] },
  placeholder: { type: String, default: '请选择' },
  disabled: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'change'])

const isOpen = ref(false)
const dropdownRef = ref(null)

const selectedLabel = computed(() => {
  const option = props.options.find(o => o.value === props.modelValue)
  return option ? option.label : ''
})

function toggle() {
  if (!props.disabled) {
    isOpen.value = !isOpen.value
  }
}

function select(value) {
  emit('update:modelValue', value)
  emit('change', value)
  isOpen.value = false
}

function handleClickOutside(e) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <div ref="dropdownRef" class="relative">
    <!-- 触发按钮 -->
    <button
      type="button"
      @click="toggle"
      :class="[
        'w-full flex items-center justify-between px-3 py-2.5 rounded-lg border text-sm transition-all',
        isOpen
          ? 'bg-gray-700/60 border-blue-500/50 ring-1 ring-blue-500/20'
          : 'bg-gray-700/50 border-gray-600/50 hover:border-gray-500/50',
        disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
      ]"
    >
      <span :class="selectedLabel ? 'text-gray-100' : 'text-gray-500'">
        {{ selectedLabel || placeholder }}
      </span>
      <svg
        class="w-4 h-4 text-gray-400 transition-transform"
        :class="isOpen ? 'rotate-180' : ''"
        fill="none" stroke="currentColor" viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <!-- 下拉列表 -->
    <Transition
      enter-active-class="transition duration-150 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-1"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition duration-100 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-1"
    >
      <div
        v-if="isOpen"
        class="absolute z-50 w-full mt-1.5 bg-gray-800 border border-gray-600/50 rounded-xl shadow-xl shadow-black/30 overflow-hidden"
      >
        <div class="max-h-60 overflow-y-auto py-1">
          <div
            v-if="options.length === 0"
            class="px-3 py-2.5 text-sm text-gray-500 text-center"
          >
            暂无数据
          </div>
          <button
            v-for="option in options"
            :key="option.value"
            type="button"
            @click="select(option.value)"
            :class="[
              'w-full px-3 py-2.5 text-left text-sm transition-colors flex items-center justify-between',
              modelValue === option.value
                ? 'bg-blue-500/15 text-blue-400'
                : 'text-gray-200 hover:bg-gray-700/60'
            ]"
          >
            <span>{{ option.label }}</span>
            <svg
              v-if="modelValue === option.value"
              class="w-4 h-4 text-blue-400"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </button>
        </div>
      </div>
    </Transition>
  </div>
</template>
