<template>
  <nav class="bottom-nav">
    <div class="nav-items">
      <router-link to="/" class="nav-item" exact-active-class="active">
        <i class="fas fa-home"></i>
        <span>首页</span>
      </router-link>
      <router-link to="/discover" class="nav-item" active-class="active">
        <i class="fas fa-search"></i>
        <span>发现</span>
      </router-link>
      <router-link to="/publish" class="nav-item" active-class="active">
        <i class="fas fa-plus-circle"></i>
        <span>发布</span>
      </router-link>
      <router-link to="/messages" class="nav-item" active-class="active">
        <i class="fas fa-comment-alt"></i>
        <span>消息</span>
      </router-link>
      <router-link to="/profile" class="nav-item" active-class="active">
        <i class="fas fa-user"></i>
        <span>我的</span>
      </router-link>
    </div>
  </nav>
</template>

<script>
export default {}
</script>

<style scoped>
.bottom-nav {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  background-color: var(--card-bg);
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  padding: 10px 0;
  z-index: 100;
}

.nav-items {
  display: flex;
  justify-content: space-around;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--text-light);
  font-size: 0.8rem;
  text-decoration: none;
}

.nav-item.active {
  color: var(--primary);
}

.nav-item i {
  font-size: 1.2rem;
  margin-bottom: 4px;
}

@media (min-width: 769px) {
  .bottom-nav {
    display: none;
  }
}
</style>