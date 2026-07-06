<template>
  <div class="pb-4 pt-2">
    <div class="flex items-end gap-2 bg-surface-50 border border-surface-200 rounded-2xl
                focus-within:border-green-300 focus-within:ring-2 focus-within:ring-green-100
                transition-all px-4 py-3 shadow-sm">
      <textarea
        v-model="input"
        @keydown.enter.exact.prevent="handleSend"
        placeholder="Ask about Kenyan election law..."
        rows="1"
        :disabled="loading"
        class="flex-1 resize-none bg-transparent text-sm text-surface-800
               focus:outline-none
               disabled:opacity-50 disabled:cursor-not-allowed
               placeholder-surface-400 py-0.5 max-h-32"
        ref="textareaRef"
        @input="autoResize"
      ></textarea>

      <div class="flex items-center gap-1.5 shrink-0">
        <!-- Clear chat button -->
        <button
          v-if="hasMessages"
          @click="handleClear"
          class="p-2 text-surface-400 hover:text-surface-600 transition-colors rounded-lg hover:bg-surface-200"
          title="Clear conversation"
        >
          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
          </svg>
        </button>

        <!-- Send button -->
        <button
          @click="handleSend"
          :disabled="!input.trim() || loading"
          class="w-8 h-8 flex items-center justify-center rounded-xl
                 bg-green-600 text-white
                 hover:bg-green-700 disabled:bg-surface-200 disabled:text-surface-400 disabled:cursor-not-allowed
                 transition-all duration-200 shrink-0"
        >
          <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h14M12 5l7 7-7 7"/>
          </svg>
          <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
          </svg>
        </button>
      </div>
    </div>

    <p class="text-[10px] text-surface-300 text-center mt-2">
      Press <kbd class="px-1 py-0.5 bg-surface-100 rounded text-surface-400 font-mono text-[10px]">Enter</kbd> to send
      · <kbd class="px-1 py-0.5 bg-surface-100 rounded text-surface-400 font-mono text-[10px]">Shift+Enter</kbd> for new line
    </p>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

const props = defineProps<{ loading: boolean; hasMessages: boolean }>()
const emit = defineEmits<{ send: [text: string]; clear: [] }>()

const input = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

function autoResize() {
  nextTick(() => {
    const el = textareaRef.value
    if (el) {
      el.style.height = 'auto'
      el.style.height = Math.min(el.scrollHeight, 128) + 'px'
    }
  })
}

function handleSend() {
  const text = input.value.trim()
  if (!text || props.loading) return
  emit('send', text)
  input.value = ''
  nextTick(autoResize)
}

function handleClear() {
  input.value = ''
  emit('clear')
}
</script>
