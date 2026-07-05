<template>
  <div class="max-w-4xl mx-auto px-6 py-6">
    <div class="flex flex-col h-[calc(100vh-9rem)]">
      <!-- Messages -->
      <div class="flex-1 overflow-y-auto space-y-5 mb-4 pr-1" ref="messagesContainer">
        <!-- Empty state -->
        <div v-if="chat.messages.length === 0" class="flex items-center justify-center h-full">
          <div class="text-center max-w-lg">
            <!-- Logo -->
            <div class="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-earth-600 to-terracotta-500
                        flex items-center justify-center shadow-lg shadow-earth-200">
              <span class="text-3xl font-bold text-white">K</span>
            </div>

            <h2 class="text-2xl font-bold bg-gradient-to-r from-earth-800 to-terracotta-600 bg-clip-text text-transparent mb-2">KadiAI</h2>
            <p class="text-sm text-earth-500 mb-8 max-w-sm mx-auto">
              Your Kenyan election law assistant. Ask about electoral laws, IEBC regulations, political party rules, and election petition case law.
            </p>

            <!-- Suggested questions -->
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5 text-left mb-4">
              <button
                v-for="(q, i) in displayedQuestions"
                :key="q"
                @click="chat.sendQuery(q)"
                class="group text-sm px-4 py-3 bg-white border border-earth-200 rounded-xl text-earth-700
                       hover:border-earth-400 hover:bg-earth-50 hover:shadow-sm
                       transition-all duration-200 text-left flex items-start gap-3"
                :style="{ animationDelay: `${i * 80}ms` }"
              >
                <svg class="w-4 h-4 text-earth-400 mt-0.5 shrink-0 group-hover:text-terracotta-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01"/>
                </svg>
                <span class="leading-snug">{{ q }}</span>
              </button>
            </div>

            <button
              @click="shuffleQuestions"
              class="text-xs text-earth-400 hover:text-earth-600 transition-colors inline-flex items-center gap-1"
            >
              <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/>
              </svg>
              Show different questions
            </button>
          </div>
        </div>

        <!-- Chat messages -->
        <TransitionGroup name="msg" tag="div" class="space-y-5">
          <ChatMessage
            v-for="msg in chat.messages"
            :key="msg.id"
            :message="msg"
            @citation-click="chat.selectCitation"
          />
        </TransitionGroup>

        <!-- Thinking animation -->
        <div v-if="chat.loading" class="flex gap-3 justify-start">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 mt-1
                      bg-gradient-to-br from-earth-600 to-terracotta-500 text-white shadow-sm">
            K
          </div>
          <div class="rounded-2xl rounded-bl-md px-5 py-4 bg-white border border-earth-200 shadow-sm max-w-sm">
            <div class="flex items-center gap-3">
              <div class="thinking-dots flex gap-1.5">
                <span class="w-2 h-2 rounded-full bg-earth-400"></span>
                <span class="w-2 h-2 rounded-full bg-earth-400"></span>
                <span class="w-2 h-2 rounded-full bg-earth-400"></span>
              </div>
              <span class="text-xs text-earth-500">{{ thinkingText }}</span>
            </div>
          </div>
        </div>

        <!-- Error display -->
        <div v-if="chat.error" class="flex justify-center">
          <div class="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-2.5 rounded-xl max-w-md">
            <span class="font-medium">Error:</span> {{ chat.error }}
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
    </div>

    <!-- Citation popover -->
    <CitationPopover
      v-if="chat.selectedCitation"
      :citation="chat.selectedCitation"
      @close="chat.selectCitation(null)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, nextTick, computed } from 'vue'
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

// Initial shuffle
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

<style scoped>
.msg-enter-active {
  transition: all 0.3s ease-out;
}
.msg-enter-from {
  opacity: 0;
  transform: translateY(8px);
}
</style>
