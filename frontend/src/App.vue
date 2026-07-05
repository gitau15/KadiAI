<template>
  <div class="min-h-screen flex flex-col">
    <header class="bg-white border-b border-earth-200 shadow-sm">
      <nav class="max-w-5xl mx-auto px-6 py-3 flex items-center justify-between">
        <router-link to="/" class="flex items-center gap-3">
          <span class="text-xl font-bold bg-gradient-to-r from-earth-800 to-terracotta-600 bg-clip-text text-transparent">KadiAI</span>
          <span class="text-xs text-earth-500 bg-sand-200 px-2 py-0.5 rounded-full">Kenya</span>
        </router-link>
        <div class="flex gap-4 text-sm font-medium">
          <router-link
            to="/"
            class="px-3 py-1.5 rounded-lg transition-colors"
            :class="$route.name === 'chat' ? 'bg-earth-100 text-earth-800' : 'text-earth-600 hover:text-earth-800'"
          >
            Ask
          </router-link>
          <router-link
            to="/sources"
            class="px-3 py-1.5 rounded-lg transition-colors"
            :class="$route.name === 'sources' ? 'bg-earth-100 text-earth-800' : 'text-earth-600 hover:text-earth-800'"
          >
            Sources
          </router-link>
        </div>
      </nav>
    </header>

    <main class="flex-1">
      <router-view />
    </main>

    <footer class="text-center text-xs text-earth-400 py-4">
      This is an AI research tool, not legal advice.
    </footer>
  </div>
</template>

<script setup lang="ts">
</script>
