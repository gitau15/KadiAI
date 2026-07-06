<template>
  <div class="max-w-5xl mx-auto px-6 py-8">
    <!-- Header -->
    <div class="mb-8">
      <h1 class="text-2xl font-semibold text-surface-800 mb-1">Source Documents</h1>
      <p class="text-sm text-surface-400">
        {{ sources.length }} documents in the knowledge base
      </p>
    </div>

    <!-- Stats bar -->
    <div class="grid grid-cols-3 gap-4 mb-8">
      <div
        class="bg-white rounded-xl border border-surface-200 p-4 text-center shadow-sm cursor-pointer transition-all hover:shadow-md"
        :class="{ 'ring-2 ring-green-400 border-green-400': filter === 'all' }"
        @click="filter = 'all'"
      >
        <div class="text-2xl font-bold text-surface-800">{{ sources.length }}</div>
        <div class="text-xs text-surface-400 mt-1">All Documents</div>
      </div>
      <div
        class="bg-white rounded-xl border border-surface-200 p-4 text-center shadow-sm cursor-pointer transition-all hover:shadow-md"
        :class="{ 'ring-2 ring-green-400 border-green-400': filter === 'statute' }"
        @click="filter = 'statute'"
      >
        <div class="text-2xl font-bold text-green-600">{{ statuteCount }}</div>
        <div class="text-xs text-surface-400 mt-1">Statutes & Acts</div>
      </div>
      <div
        class="bg-white rounded-xl border border-surface-200 p-4 text-center shadow-sm cursor-pointer transition-all hover:shadow-md"
        :class="{ 'ring-2 ring-green-400 border-green-400': filter === 'case_law' }"
        @click="filter = 'case_law'"
      >
        <div class="text-2xl font-bold text-green-700">{{ caseLawCount }}</div>
        <div class="text-xs text-surface-400 mt-1">Case Law</div>
      </div>
    </div>

    <!-- Search and sort bar -->
    <div class="flex gap-3 mb-6">
      <div class="flex-1 relative">
        <svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input
          v-model="search"
          type="text"
          placeholder="Search documents..."
          class="w-full pl-10 pr-4 py-2.5 rounded-xl border border-surface-200 bg-white text-sm text-surface-800
                 focus:outline-none focus:ring-2 focus:ring-green-200 focus:border-green-300 transition-all
                 placeholder:text-surface-400"
        />
      </div>
      <select
        v-model="sortBy"
        class="px-4 py-2.5 rounded-xl border border-surface-200 bg-white text-sm text-surface-700
               focus:outline-none focus:ring-2 focus:ring-green-200 cursor-pointer"
      >
        <option value="name">Sort by Name</option>
        <option value="date">Sort by Date</option>
        <option value="pages">Sort by Pages</option>
        <option value="type">Sort by Type</option>
      </select>
    </div>

    <!-- Auto-update scheduler card -->
    <div class="mb-6 bg-white rounded-xl border border-surface-200 shadow-sm p-4 flex items-center gap-4">
      <div class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
           :class="schedulerStatus?.enabled ? 'bg-green-50 text-green-600' : 'bg-surface-100 text-surface-400'">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
        </svg>
      </div>
      <div class="flex-1 min-w-0">
        <div class="flex items-center gap-2">
          <h3 class="text-sm font-semibold text-surface-800">Auto-Update</h3>
          <span class="text-[10px] px-1.5 py-0.5 rounded-full font-medium"
                :class="schedulerStatus?.enabled
                  ? 'bg-green-100 text-green-700'
                  : 'bg-surface-100 text-surface-500'">
            {{ schedulerStatus?.enabled ? 'Active' : 'Inactive' }}
          </span>
          <span v-if="schedulerStatus?.is_running"
                class="text-[10px] px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-700 font-medium animate-pulse">
            Running now...
          </span>
        </div>
        <p class="text-xs text-surface-400 mt-0.5">
          {{ schedulerStatus?.schedule || 'Every Friday at 19:00 EAT' }}
          <span v-if="schedulerStatus?.next_run" class="text-surface-300">
            · Next: {{ formatSchedulerDate(schedulerStatus.next_run) }}
          </span>
          <span v-if="schedulerStatus?.last_run" class="text-surface-300">
            · Last: {{ formatSchedulerDate(schedulerStatus.last_run) }}
          </span>
        </p>
      </div>
      <button
        @click="triggerScrape"
        :disabled="triggering || schedulerStatus?.is_running"
        class="px-3 py-1.5 text-xs font-medium rounded-lg border transition-all shrink-0
               disabled:opacity-40 disabled:cursor-not-allowed"
        :class="triggering
          ? 'bg-surface-100 border-surface-200 text-surface-500'
          : 'bg-white border-surface-200 text-surface-700 hover:bg-surface-50 hover:border-surface-300'"
      >
        {{ triggering ? 'Running...' : 'Run Now' }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-16">
      <div class="thinking-dots flex gap-1.5 justify-center mb-3">
        <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
        <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
        <span class="w-2.5 h-2.5 rounded-full bg-green-400"></span>
      </div>
      <p class="text-sm text-surface-400">Loading documents...</p>
    </div>

    <!-- Empty state -->
    <div v-else-if="filteredSources.length === 0" class="text-center py-16">
      <svg class="w-16 h-16 mx-auto text-surface-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <p class="text-surface-400">
        {{ search ? 'No documents match your search.' : 'No documents ingested yet.' }}
      </p>
      <button
        v-if="search"
        @click="search = ''"
        class="mt-3 text-sm text-green-600 hover:text-green-700 underline"
      >
        Clear search
      </button>
    </div>

    <!-- Document list -->
    <div v-else class="space-y-3">
      <div class="text-xs text-surface-400 mb-1">
        Showing {{ filteredSources.length }} of {{ sources.length }} documents
      </div>

      <TransitionGroup name="list" tag="div" class="space-y-3">
        <div
          v-for="doc in filteredSources"
          :key="doc.id"
          class="bg-white rounded-xl border border-surface-200 shadow-sm overflow-hidden
                 hover:shadow-md transition-all duration-200"
        >
          <!-- Card header -->
          <button
            @click="toggleExpand(doc.id)"
            class="w-full px-5 py-4 flex items-center gap-4 text-left group"
          >
            <!-- Type icon -->
            <div
              class="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
              :class="doc.document_type === 'statute'
                ? 'bg-green-50 text-green-600'
                : 'bg-surface-100 text-surface-500'"
            >
              <svg v-if="doc.document_type === 'statute'" class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"/>
              </svg>
              <svg v-else class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"/>
              </svg>
            </div>

            <!-- Title and metadata -->
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-surface-800 truncate group-hover:text-green-700 transition-colors">
                {{ cleanTitle(doc.title) }}
              </h3>
              <div class="flex items-center gap-2 mt-1 text-xs text-surface-400">
                <span
                  class="px-1.5 py-0.5 rounded text-[10px] font-medium uppercase tracking-wide"
                  :class="doc.document_type === 'statute'
                    ? 'bg-green-50 text-green-600'
                    : 'bg-surface-100 text-surface-500'"
                >
                  {{ doc.document_type === 'statute' ? 'Statute' : 'Case Law' }}
                </span>
                <span>{{ doc.page_count }} pages</span>
                <span class="text-surface-300">|</span>
                <span>{{ formatDate(doc.ingested_at) }}</span>
              </div>
            </div>

            <!-- Expand arrow -->
            <svg
              class="w-5 h-5 text-surface-300 shrink-0 transition-transform duration-200"
              :class="{ 'rotate-180': expandedIds.has(doc.id) }"
              fill="none" stroke="currentColor" viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
            </svg>
          </button>

          <!-- Expanded details -->
          <Transition name="expand">
            <div v-if="expandedIds.has(doc.id)" class="px-5 pb-4 border-t border-surface-100">
              <div class="pt-4 grid grid-cols-2 gap-4">
                <div>
                  <dt class="text-[10px] uppercase tracking-wide text-surface-400 font-medium">Full Title</dt>
                  <dd class="text-sm text-surface-700 mt-0.5">{{ doc.title }}</dd>
                </div>
                <div>
                  <dt class="text-[10px] uppercase tracking-wide text-surface-400 font-medium">Document ID</dt>
                  <dd class="text-sm text-surface-700 mt-0.5 font-mono">{{ doc.id }}</dd>
                </div>
                <div>
                  <dt class="text-[10px] uppercase tracking-wide text-surface-400 font-medium">Ingested</dt>
                  <dd class="text-sm text-surface-700 mt-0.5">{{ formatFullDate(doc.ingested_at) }}</dd>
                </div>
                <div v-if="doc.source_url">
                  <dt class="text-[10px] uppercase tracking-wide text-surface-400 font-medium">Source URL</dt>
                  <dd class="text-sm mt-0.5">
                    <a :href="doc.source_url" target="_blank" class="text-green-600 hover:underline truncate block">
                      {{ doc.source_url }}
                    </a>
                  </dd>
                </div>
              </div>
            </div>
          </Transition>
        </div>
      </TransitionGroup>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { listSources, getSchedulerStatus, triggerManualScrape } from '@/services/api'
import type { SchedulerStatus } from '@/services/api'
import type { SourceDocument } from '@/types'

const sources = ref<SourceDocument[]>([])
const loading = ref(true)
const search = ref('')
const filter = ref<'all' | 'statute' | 'case_law'>('all')
const sortBy = ref('name')
const expandedIds = ref(new Set<string>())
const schedulerStatus = ref<SchedulerStatus | null>(null)
const triggering = ref(false)

const statuteCount = computed(() => sources.value.filter(s => s.document_type === 'statute').length)
const caseLawCount = computed(() => sources.value.filter(s => s.document_type === 'case_law').length)

const filteredSources = computed(() => {
  let result = [...sources.value]

  if (filter.value !== 'all') {
    result = result.filter(s => s.document_type === filter.value)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    result = result.filter(s =>
      s.title.toLowerCase().includes(q) ||
      s.id.toLowerCase().includes(q)
    )
  }

  switch (sortBy.value) {
    case 'name':
      result.sort((a, b) => a.title.localeCompare(b.title))
      break
    case 'date':
      result.sort((a, b) => new Date(b.ingested_at).getTime() - new Date(a.ingested_at).getTime())
      break
    case 'pages':
      result.sort((a, b) => b.page_count - a.page_count)
      break
    case 'type':
      result.sort((a, b) => a.document_type.localeCompare(b.document_type))
      break
  }

  return result
})

function toggleExpand(id: string) {
  const s = new Set(expandedIds.value)
  if (s.has(id)) {
    s.delete(id)
  } else {
    s.add(id)
  }
  expandedIds.value = s
}

function cleanTitle(title: string): string {
  return title.replace(/\.pdf$/i, '')
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return 'Unknown'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
}

function formatFullDate(dateStr: string | null): string {
  if (!dateStr) return 'Unknown'
  const d = new Date(dateStr)
  return d.toLocaleString('en-GB', {
    day: 'numeric', month: 'long', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  })
}

function formatSchedulerDate(dateStr: string): string {
  const d = new Date(dateStr)
  return d.toLocaleString('en-GB', {
    weekday: 'short', day: 'numeric', month: 'short',
    hour: '2-digit', minute: '2-digit',
  })
}

async function triggerScrape() {
  triggering.value = true
  try {
    await triggerManualScrape()
    setTimeout(async () => {
      schedulerStatus.value = await getSchedulerStatus().catch(() => null)
    }, 2000)
  } catch {
    triggering.value = false
  }
}

onMounted(async () => {
  try {
    sources.value = await listSources()
  } catch {
    sources.value = []
  } finally {
    loading.value = false
  }

  try {
    schedulerStatus.value = await getSchedulerStatus()
  } catch {
    schedulerStatus.value = null
  }
})
</script>

<style scoped>
.list-enter-active,
.list-leave-active {
  transition: all 0.3s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
.list-move {
  transition: transform 0.3s ease;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease;
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  padding-top: 0;
  padding-bottom: 0;
}
.expand-enter-to,
.expand-leave-from {
  opacity: 1;
  max-height: 200px;
}
</style>
