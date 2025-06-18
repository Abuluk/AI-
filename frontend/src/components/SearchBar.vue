<template>
  <div class="search-bar">
    <i class="fas fa-search"></i>
    <input 
      type="text" 
      placeholder="搜索商品..." 
      v-model="searchQuery"
      @keyup.enter="search"
    >
  </div>
</template>

<script>
export default {
  data() {
    return {
      searchQuery: ''
    }
  },
  methods: {
    search() {
      if (this.searchQuery.trim()) {
        this.$router.push({ path: '/', query: { q: this.searchQuery } })
      }
    }
  }
}
</script>

<style scoped>
.search-bar {
  flex: 1;
  max-width: 500px;
  margin: 0 20px;
  position: relative;
}

.search-bar input {
  width: 100%;
  padding: 10px 15px 10px 40px;
  border-radius: 30px;
  border: 1px solid var(--border);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s;
}

.search-bar input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(52, 152, 219, 0.2);
}

.search-bar i {
  position: absolute;
  left: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-light);
}

@media (max-width: 768px) {
  .search-bar {
    margin: 0 10px;
  }
}
</style>