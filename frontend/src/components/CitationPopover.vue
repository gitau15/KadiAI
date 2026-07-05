<template>
  <Teleport to="body">
    <div class="fixed inset-0 z-50 flex items-end justify-center pb-6" @click.self="$emit('close')">
      <div class="bg-white border border-earth-300 rounded-2xl shadow-xl max-w-xl w-full mx-4 p-6 animate-fade-up">
        <div class="flex items-start justify-between mb-3">
          <div>
            <h4 class="font-semibold text-earth-800 text-sm">{{ citation.document }}</h4>
            <p class="text-xs text-earth-500">{{ citation.section }} · Page {{ citation.page }}</p>
          </div>
          <button
            @click="$emit('close')"
            class="text-earth-400 hover:text-earth-600 transition-colors"
          >
            <span class="text-lg">&times;</span>
          </button>
        </div>
        <div class="bg-sand-100 rounded-xl p-4 text-sm text-earth-700 leading-relaxed max-h-64 overflow-y-auto">
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
