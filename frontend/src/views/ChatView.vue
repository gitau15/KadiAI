<template>
  <div class="flex-1 flex flex-col max-w-4xl mx-auto w-full px-6">
    <!-- Messages area -->
    <div class="flex-1 overflow-y-auto py-6" ref="messagesContainer">
      <!-- Empty state -->
      <div v-if="chat.messages.length === 0" class="flex items-center justify-center h-full">
        <div class="text-center max-w-2xl w-full">
          <!-- Logo & greeting -->
          <div class="mb-10">
            <div class="w-14 h-14 mx-auto mb-5 rounded-2xl bg-green-600 flex items-center justify-center shadow-lg shadow-green-600/20">
              <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
              </svg>
            </div>
            <h1 class="text-2xl font-semibold text-surface-800 mb-2">How can I help you today?</h1>
            <p class="text-sm text-surface-400 max-w-md mx-auto">
              Ask about Kenyan electoral laws, IEBC regulations, election petitions, and political party rules.
            </p>
          </div>

          <!-- Suggested questions -->
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-left max-w-xl mx-auto">
            <button
              v-for="(q, i) in displayedQuestions"
              :key="q"
              @click="chat.sendQuery(q)"
              class="group text-sm px-4 py-3.5 bg-surface-50 border border-surface-200 rounded-xl
                     hover:bg-green-50 hover:border-green-200 hover:text-surface-800
                     transition-all duration-200 text-left flex items-start gap-3 text-surface-600"
              :style="{ animationDelay: `${i * 60}ms` }"
            >
              <svg class="w-4 h-4 text-surface-300 mt-0.5 shrink-0 group-hover:text-green-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z"/>
              </svg>
              <span class="leading-relaxed">{{ q }}</span>
            </button>
          </div>

          <button
            @click="shuffleQuestions"
            class="mt-5 text-xs text-surface-400 hover:text-green-600 transition-colors inline-flex items-center gap-1.5"
          >
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
            </svg>
            Show different questions
          </button>
        </div>
      </div>

      <!-- Chat messages -->
      <div v-else class="space-y-6">
        <ChatMessage
          v-for="msg in chat.messages"
          :key="msg.id"
          :message="msg"
          @citation-click="chat.selectCitation"
        />

        <!-- Thinking indicator -->
        <div v-if="chat.loading" class="flex gap-3 items-start">
          <div class="w-7 h-7 rounded-lg flex items-center justify-center shrink-0 bg-green-600 text-white">
            <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
          <div class="bg-surface-50 border border-surface-200 rounded-2xl rounded-tl-md px-5 py-3.5 max-w-sm">
            <div class="flex items-center gap-3">
              <div class="thinking-dots flex gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
                <span class="w-1.5 h-1.5 rounded-full bg-green-400"></span>
              </div>
              <span class="text-xs text-surface-400">{{ thinkingText }}</span>
            </div>
          </div>
        </div>

        <!-- Error display -->
        <div v-if="chat.error" class="flex justify-center">
          <div class="bg-red-50 border border-red-100 text-red-600 text-sm px-4 py-2.5 rounded-xl max-w-md">
            {{ chat.error }}
          </div>
        </div>
      </div>
    </div>

    <!-- Input -->
    <ChatInput
      :loading="chat.loading"
      :has-messages="chat.messages.length > 0"
      @send="chat.sendQuery"
      @clear="chat.clearChat"
    />

    <!-- Citation popover -->
    <CitationPopover
      v-if="chat.selectedCitation"
      :citation="chat.selectedCitation"
      @close="chat.selectCitation(null)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import ChatMessage from '@/components/ChatMessage.vue'
import ChatInput from '@/components/ChatInput.vue'
import CitationPopover from '@/components/CitationPopover.vue'

const chat = useChatStore()
const messagesContainer = ref<HTMLElement>()

// Large pool of suggested questions
const allQuestions = [
  'What are the grounds for nullifying a presidential election in Kenya?',
  'What is the role of IEBC in voter registration?',
  'What constitutes an election offense under Kenyan law?',
  'How does the Supreme Court handle presidential election petitions?',
  'What are the qualifications for election as President?',
  'What are the requirements for an independent presidential candidate?',
  'How are members of Parliament elected in Kenya?',
  'What is the procedure for voter registration?',
  'What are the powers of IEBC regarding election disputes?',
  'How are county governors elected and what are their qualifications?',
  'What are the rules for political party nominations?',
  'What is the timeline for filing an election petition?',
  'How does Kenya regulate campaign financing?',
  'What are the obligations of a returning officer?',
  'What are the grounds for disqualifying a candidate from elections?',
  'How does the Elections Act define electoral malpractice?',
  'What remedies are available for election petition losers?',
  'How are election results declared and gazetted?',
  'What is the role of election observers in Kenya?',
  'What technology requirements does IEBC follow for elections?',
  'How are party list members of Parliament selected?',
  'What are the rules for coalition building before elections?',
  'What penalties apply for voter bribery or undue influence?',
  'How does the law protect the secrecy of the ballot?',
  'What are the rights of voters with disabilities?',
]

// Randomly pick 4 questions
const displayedQuestions = ref<string[]>([])

function shuffleQuestions() {
  const shuffled = [...allQuestions].sort(() => Math.random() - 0.5)
  displayedQuestions.value = shuffled.slice(0, 4)
}

shuffleQuestions()

// Rotating thinking text
const thinkingTexts = [
  'Searching legal documents...',
  'Analyzing relevant statutes...',
  'Finding case law precedents...',
  'Cross-referencing citations...',
  'Composing answer with sources...',
]
const thinkingText = ref(thinkingTexts[0])
let thinkingInterval: ReturnType<typeof setInterval> | null = null

watch(() => chat.loading, (isLoading) => {
  if (isLoading) {
    thinkingText.value = thinkingTexts[Math.floor(Math.random() * thinkingTexts.length)]
    let idx = 0
    thinkingInterval = setInterval(() => {
      idx = (idx + 1) % thinkingTexts.length
      thinkingText.value = thinkingTexts[idx]
    }, 4000)
  } else {
    if (thinkingInterval) {
      clearInterval(thinkingInterval)
      thinkingInterval = null
    }
  }
})

// Auto-scroll when messages change or loading starts
watch(
  () => [chat.messages.length, chat.loading],
  () => {
    nextTick(() => {
      if (messagesContainer.value) {
        messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
      }
    })
  },
)
</script>
