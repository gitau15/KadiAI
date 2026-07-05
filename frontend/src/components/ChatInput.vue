<template>
  <div class="border-t border-earth-200 bg-white/80 backdrop-blur-sm px-6 py-3">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-end gap-2.5 bg-sand-100 rounded-2xl border border-earth-200
                  focus-within:border-earth-400 focus-within:ring-2 focus-within:ring-earth-200
                  transition-all px-4 py-2.5 shadow-sm">
        <textarea
          v-model="input"
          @keydown.enter.exact.prevent="handleSend"
          placeholder="Ask KadiAI about Kenyan election law..."
          rows="1"
          :disabled="loading"
          class="flex-1 resize-none bg-transparent text-sm text-earth-800
                 focus:outline-none
                 disabled:opacity-50 disabled:cursor-not-allowed
                 placeholder-earth-400 py-1 max-h-32"
          ref="textareaRef"
          @input="autoResize"
        ></textarea>

        <div class="flex items-center gap-2 shrink-0">
          <!-- Clear chat button -->
          <button
            v-if="hasMessages"
            @click="handleClear"
            class="p-2 text-earth-400 hover:text-earth-600 transition-colors rounded-lg hover:bg-earth-100"
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
            class="w-9 h-9 flex items-center justify-center rounded-xl
                   bg-earth-700 text-white
                   hover:bg-earth-800 disabled:opacity-30 disabled:cursor-not-allowed
                   transition-all duration-200 shrink-0"
          >
            <svg v-if="!loading" class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
            </svg>
            <svg v-else class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"/>
            </svg>
          </button>
        </div>
      </div>

      <p class="text-[10px] text-earth-400 text-center mt-2">
        Press <kbd class="px-1 py-0.5 bg-earth-100 rounded text-earth-500 font-mono">Enter</kbd> to send
        · <kbd class="px-1 py-0.5 bg-earth-100 rounded text-earth-500 font-mono">Shift+Enter</kbd> for new line
      </p>
    </div>
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
