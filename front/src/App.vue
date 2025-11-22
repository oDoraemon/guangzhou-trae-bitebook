<script setup lang="ts"></script>

<template>
  <div class="layout">
    <main class="main">
      <div class="content">
        <router-view />
      </div>
    </main>
  </div>
  
</template>

<style scoped>
.layout { width: 100%; }
.header { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid #eee; }
.title { font-weight: 600; text-decoration: none; color: #333; }
.main { padding: 12px 16px; }
.content { width: 1024px; margin: 0 auto; }

@media (max-width: 960px) {
  .main { padding: 10px 14px; }
  .content { width: 960px; }
}
@media (max-width: 700px) {
  .main { padding: 8px 10px; }
  .content { width: 700px; }
}
</style>
