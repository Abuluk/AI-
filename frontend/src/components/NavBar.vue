<template>
  <header>
    <div class="navbar">
      <router-link to="/" class="logo">
        <i class="fas fa-fish"></i>
        <span>Goofish</span>
      </router-link>
      
      <SearchBar />
      
      <div class="nav-icons">
        <router-link to="/messages" class="nav-icon">
          <i class="fas fa-comment-alt"></i>
          <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
        </router-link>
        <router-link to="/profile" class="nav-icon">
          <i class="fas fa-user-circle"></i>
        </router-link>
        <router-link to="/publish" class="nav-icon">
          <i class="fas fa-plus-circle"></i>
        </router-link>
      </div>
    </div>
  </header>
</template>

<script>
import SearchBar from './SearchBar.vue'

export default {
  components: {
    SearchBar
  },
  data() {
    return {
      unreadCount: 3
    }
  }
}
</script>

<style scoped>
header {
  background-color: var(--card-bg);
  box-shadow: var(--shadow);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 0;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 1.5rem;
  font-weight: bold;
  color: var(--primary);
  text-decoration: none;
}

.logo i {
  margin-right: 8px;
}

.nav-icons {
  display: flex;
  gap: 20px;
}

.nav-icon {
  position: relative;
  color: var(--text);
  font-size: 1.2rem;
  text-decoration: none;
}

.nav-icon i {
  transition: color 0.3s;
}

.nav-icon:hover i,
.nav-icon.router-link-active i {
  color: var(--primary);
}

.badge {
  position: absolute;
  top: -5px;
  right: -8px;
  background-color: var(--danger);
  color: white;
  font-size: 0.7rem;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .navbar {
    padding: 10px 0;
  }
}
</style>