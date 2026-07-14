<template>
  <div class="stat-cards">
    <div v-for="card in cards" :key="card.label" class="stat-card">
      <div class="label">{{ card.label }}</div>
      <div class="value" :style="{ color: card.color }">{{ card.value }}</div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  cards: { type: Array, default: () => [] },
})
</script>