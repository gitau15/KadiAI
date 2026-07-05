import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ChatMessage, Citation } from '@/types'
import { askQuery } from '@/services/api'

export const useChatStore = defineStore('chat', () => {
  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedCitation = ref<Citation | null>(null)

  function addMessage(role: 'user' | 'assistant', content: string, citations?: Citation[]) {
    messages.value.push({
      id: crypto.randomUUID(),
      role,
      content,
      citations,
      timestamp: Date.now(),
    })
  }

  async function sendQuery(text: string) {
    addMessage('user', text)
    loading.value = true
    error.value = null

    try {
      const res = await askQuery(text)
      addMessage('assistant', res.answer, res.citations)
    } catch (e: any) {
      error.value = e?.message || 'Failed to get an answer.'
      addMessage('assistant', 'Sorry, something went wrong. Please try again.')
    } finally {
      loading.value = false
    }
  }

  function selectCitation(citation: Citation | null) {
    selectedCitation.value = citation
  }

  function clearChat() {
    messages.value = []
    error.value = null
    selectedCitation.value = null
  }

  return { messages, loading, error, selectedCitation, sendQuery, selectCitation, clearChat }
})
