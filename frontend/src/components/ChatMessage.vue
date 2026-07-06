<template>
  <div class="message-enter">
    <!-- User message -->
    <div v-if="message.role === 'user'" class="flex justify-end">
      <div class="max-w-[75%] bg-surface-100 rounded-2xl rounded-br-md px-5 py-3 text-sm text-surface-800 leading-relaxed">
        <div class="whitespace-pre-wrap">{{ message.content }}</div>
      </div>
    </div>

    <!-- Assistant message -->
    <div v-else class="flex gap-3 items-start">
      <!-- AI avatar -->
      <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 bg-green-600 text-white mt-0.5">
        <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
        </svg>
      </div>

      <!-- Content -->
      <div class="flex-1 min-w-0">
        <!-- Rendered answer -->
        <div class="text-sm text-surface-700 leading-relaxed assistant-content" v-html="renderedContent"></div>

        <!-- Actions row -->
        <div class="flex items-center gap-3 mt-3">
          <!-- Copy button -->
          <button
            @click="copyAnswer"
            class="inline-flex items-center gap-1 text-xs text-surface-400 hover:text-green-600 transition-colors"
          >
            <svg v-if="!copied" class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
            </svg>
            <svg v-else class="w-3.5 h-3.5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>
            </svg>
            <span>{{ copied ? 'Copied' : 'Copy' }}</span>
          </button>

          <!-- Timestamp -->
          <span class="text-[10px] text-surface-300">{{ formatTime(message.timestamp) }}</span>
        </div>

        <!-- Citation badges -->
        <div v-if="message.citations && message.citations.length" class="mt-3 pt-3 border-t border-surface-100">
          <p class="text-[11px] text-surface-400 mb-2 font-medium uppercase tracking-wider flex items-center gap-1">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            Sources
          </p>
          <div class="flex flex-wrap gap-1.5">
            <button
              v-for="(cit, i) in message.citations"
              :key="i"
              @click="$emit('citationClick', cit)"
              class="text-xs px-2.5 py-1.5 bg-green-50 text-green-700 rounded-lg border border-green-100
                     hover:bg-green-100 hover:border-green-200 transition-all text-left max-w-[240px] truncate"
            >
              <span class="font-medium">{{ cleanDocName(cit.document) }}</span>
              <span v-if="cit.section" class="text-green-500"> · {{ cit.section }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ChatMessage, Citation } from '@/types'

const props = defineProps<{
  message: ChatMessage
}>()

defineEmits<{
  citationClick: [citation: Citation]
}>()

const copied = ref(false)

function copyAnswer() {
  navigator.clipboard.writeText(props.message.content).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

function formatTime(ts: number): string {
  const d = new Date(ts)
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function cleanDocName(name: string): string {
  return name.replace(/\.pdf$/i, '').replace(/_/g, ' ')
}

const renderedContent = computed(() => {
  let text = props.message.content

  // Escape HTML
  text = text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

  // Bold: **text**
  text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')

  // Numbered lists
  text = text.replace(/^(\d+)\.\s/gm, '<span class="text-green-600 font-semibold">$1.</span> ')

  // Highlight citation patterns: [Source: ...]
  text = text.replace(
    /\[Source:\s*([^\]]+)\]/g,
    '<span class="inline-flex items-center gap-1 text-green-700 font-medium text-xs bg-green-50 border border-green-100 px-2 py-0.5 rounded-md my-1">📄 $1</span>'
  )

  // Line breaks
  text = text.replace(/\n\n/g, '</p><p class="mt-2">')
  text = text.replace(/\n/g, '<br/>')
  text = `<p>${text}</p>`

  return text
})
</script>

<style scoped>
.assistant-content :deep(p) {
  margin: 0;
}
.assistant-content :deep(strong) {
  @apply text-surface-800 font-semibold;
}
</style>
