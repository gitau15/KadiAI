<template>
  <div
    class="flex gap-3 message-enter"
    :class="message.role === 'user' ? 'justify-end' : 'justify-start'"
  >
    <!-- Avatar (AI only for assistant, skip for user) -->
    <div
      v-if="message.role === 'assistant'"
      class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-1
             bg-gradient-to-br from-earth-600 to-terracotta-500 text-white shadow-sm"
    >
      K
    </div>

    <!-- Bubble -->
    <div
      class="max-w-[80%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed relative group"
      :class="message.role === 'user'
        ? 'bg-earth-700 text-white rounded-br-md shadow-sm'
        : 'bg-white border border-earth-200 text-earth-800 rounded-bl-md shadow-sm'"
    >
      <!-- Rendered answer with clickable citations -->
      <div v-if="message.role === 'assistant'" class="assistant-content" v-html="renderedContent"></div>
      <div v-else class="whitespace-pre-wrap">{{ message.content }}</div>

      <!-- Timestamp and actions -->
      <div class="flex items-center justify-between mt-2 gap-2"
           :class="message.role === 'user' ? 'text-earth-300' : 'text-earth-400'">
        <span class="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity">
          {{ formatTime(message.timestamp) }}
        </span>
        <button
          v-if="message.role === 'assistant'"
          @click="copyAnswer"
          class="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity hover:underline text-earth-400"
        >
          {{ copied ? 'Copied!' : 'Copy' }}
        </button>
      </div>

      <!-- Citation badges -->
      <div v-if="message.citations && message.citations.length"
           class="mt-3 pt-3 border-t"
           :class="message.role === 'user' ? 'border-earth-600' : 'border-earth-100'">
        <p class="text-xs text-earth-500 mb-2 font-medium flex items-center gap-1">
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
            class="text-xs px-2.5 py-1.5 bg-sand-100 text-earth-700 rounded-lg border border-earth-100
                   hover:bg-earth-100 hover:border-earth-200 transition-all text-left max-w-[240px] truncate"
          >
            <span class="font-medium">{{ cleanDocName(cit.document) }}</span>
            <span v-if="cit.section" class="text-earth-500"> · {{ cit.section }}</span>
          </button>
        </div>
      </div>
    </div>

    <!-- User avatar -->
    <div
      v-if="message.role === 'user'"
      class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-1
             bg-earth-200 text-earth-700"
    >
      You
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

  // Numbered lists: "1. " at start of line
  text = text.replace(/^(\d+)\.\s/gm, '<span class="text-terracotta-500 font-semibold">$1.</span> ')

  // Highlight citation patterns: [Source: ...]
  text = text.replace(
    /\[Source:\s*([^\]]+)\]/g,
    '<span class="inline-flex items-center gap-1 text-earth-600 font-medium text-xs bg-sand-100 border border-earth-100 px-2 py-0.5 rounded-md my-1">📄 $1</span>'
  )

  // Line breaks
  text = text.replace(/\n\n/g, '</p><p class="mt-2">')
  text = text.replace(/\n/g, '<br/>')
  text = `<p>${text}</p>`

  return text
})
</script>

<style scoped>
.message-enter {
  animation: msg-in 0.3s ease-out;
}
@keyframes msg-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: translateY(0); }
}

.assistant-content :deep(p) {
  margin: 0;
}
.assistant-content :deep(strong) {
  @apply text-earth-900 font-semibold;
}
</style>
