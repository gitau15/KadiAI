<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-end justify-center pb-6" @click.self="$emit('close')">
      <div class="bg-white border border-surface-200 rounded-2xl shadow-xl max-w-xl w-full mx-4 p-6 animate-fade-up">
        <div class="flex items-start justify-between mb-4">
          <div>
            <h4 class="font-semibold text-surface-800 text-sm">{{ citation.document }}</h4>
            <p class="text-xs text-surface-400 mt-0.5">{{ citation.section }} · Page {{ citation.page }}</p>
          </div>
          <button
            @click="$emit('close')"
            class="text-surface-400 hover:text-surface-600 transition-colors ml-4"
          >
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
        <div class="bg-surface-50 rounded-xl p-4 text-sm text-surface-600 leading-relaxed max-h-64 overflow-y-auto border border-surface-100">
          {{ citation.chunk_text }}
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import type { Citation } from '@/types'

defineProps<{ citation: Citation }>()
defineEmits<{ close: [] }>()
</script>

<style scoped>
@keyframes fade-up {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
.animate-fade-up {
  animation: fade-up 0.2s ease-out;
}
</style>
