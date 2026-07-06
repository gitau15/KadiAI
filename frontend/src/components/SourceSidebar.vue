<template>
  <aside class="w-80 border-l border-surface-200 bg-white p-5 overflow-y-auto">
    <h3 class="text-sm font-semibold text-surface-800 mb-4">Sources in this answer</h3>

    <div v-if="!store.selectedCitation" class="text-xs text-surface-400">
      Click a source badge to view its full context.
    </div>

    <div v-else class="space-y-4">
      <div class="bg-surface-50 rounded-xl p-4 border border-surface-100">
        <h4 class="text-sm font-medium text-surface-800">{{ store.selectedCitation.document }}</h4>
        <p class="text-xs text-surface-400 mt-1">
          {{ store.selectedCitation.section }} · Page {{ store.selectedCitation.page }}
        </p>
        <p class="text-sm text-surface-600 mt-3 leading-relaxed whitespace-pre-wrap">
          {{ store.selectedCitation.chunk_text }}
        </p>
      </div>
    </div>
  </aside>
</template>

<script setup lang="ts">
import { useChatStore } from '@/stores/chat'

const store = useChatStore()
</script>
