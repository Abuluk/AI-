<template>
  <div v-if="visible" class="image-preview-overlay" @click.self="close">
    <img :src="url" class="image-preview-img" />
    <button class="close-btn" @click="close">×</button>
  </div>
</template>
<script setup>
import { defineProps, defineEmits } from 'vue'
const props = defineProps({ url: String, visible: Boolean })
const emit = defineEmits(['close'])
function close() { emit('close') }
</script>
<style scoped>
.image-preview-overlay {
  position: fixed; left: 0; top: 0; width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 9999;
}
.image-preview-img {
  max-width: 90vw; max-height: 90vh; border-radius: 8px; box-shadow: 0 2px 16px #0008;
}
.close-btn {
  position: absolute; top: 30px; right: 40px; font-size: 2.5rem; color: #fff; background: none; border: none; cursor: pointer;
}
</style> 