<template>
  <div class="min-h-screen flex flex-col bg-white">
    <!-- Header -->
    <header class="sticky top-0 z-40 bg-white/80 backdrop-blur-xl border-b border-surface-100">
      <nav class="max-w-5xl mx-auto px-6 h-14 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-2.5">
          <div class="w-7 h-7 rounded-lg bg-green-600 flex items-center justify-center">
            <svg class="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"/>
            </svg>
          </div>
          <span class="text-base font-semibold text-surface-800">KadiAI</span>
        </router-link>

        <div class="flex items-center">
          <div class="flex bg-surface-100 rounded-lg p-0.5">
            <router-link
              to="/"
              class="px-3.5 py-1.5 rounded-md text-sm font-medium transition-all duration-200"
              :class="$route.name === 'chat' ? 'bg-white text-surface-800 shadow-sm' : 'text-surface-500 hover:text-surface-700'"
            >
              Chat
            </router-link>
            <router-link
              to="/sources"
              class="px-3.5 py-1.5 rounded-md text-sm font-medium transition-all duration-200"
              :class="$route.name === 'sources' ? 'bg-white text-surface-800 shadow-sm' : 'text-surface-500 hover:text-surface-700'"
            >
              Sources
            </router-link>
          </div>
        </div>
      </nav>
    </header>

    <!-- Main content -->
    <main class="flex-1 flex flex-col">
      <router-view />
    </main>

    <!-- Footer -->
    <footer class="text-center text-[11px] text-surface-400 py-3 border-t border-surface-50">
      KadiAI is an AI research tool, not legal advice.
    </footer>
  </div>
</template>

<script setup lang="ts">
</script>
