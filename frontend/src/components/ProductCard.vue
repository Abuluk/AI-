<template>
  <router-link :to="`/item/${product.id}`" class="product-card">
    <img :src="product.image" :alt="product.title" class="product-image">
    <div class="product-info">
      <h3 class="product-title">{{ product.title }}</h3>
      <div class="product-price">¥{{ product.price }}</div>
      <div class="product-meta">
        <span>{{ product.location }}</span>
        <span>浏览: {{ product.views }}</span>
      </div>
    </div>
  </router-link>
</template>

<script>
export default {
  props: {
    product: {
      type: Object,
      required: true
    }
  }
}
</script>

<style scoped>
.product-card {
  background-color: var(--card-bg);
  border-radius: 10px;
  overflow: hidden;
  box-shadow: var(--shadow);
  transition: transform 0.3s, box-shadow 0.3s;
  cursor: pointer;
  text-decoration: none;
  color: inherit;
  display: block;
}

.product-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
}

.product-image {
  height: 200px;
  width: 100%;
  object-fit: cover;
  border-bottom: 1px solid var(--border);
}

.product-info {
  padding: 15px;
}

.product-title {
  font-weight: 600;
  margin-bottom: 8px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  min-height: 42px;
}

.product-price {
  color: var(--danger);
  font-weight: bold;
  font-size: 1.1rem;
  margin-bottom: 8px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  color: var(--text-light);
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .product-image {
    height: 160px;
  }
}
</style>