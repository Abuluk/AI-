<template>
  <div id="app">
    <NavBar />
    <router-view />
    <BottomNav />
  </div>
</template>

<script>
import NavBar from '@/components/NavBar.vue'
import BottomNav from '@/components/BottomNav.vue'

export default {
  components: {
    NavBar,
    BottomNav
  }
}
</script>

<style>
:root {
  --primary: #3498db;
  --primary-dark: #2980b9;
  --secondary: #f1f2f6;
  --success: #2ecc71;
  --danger: #e74c3c;
  --text: #2c3e50;
  --text-light: #7f8c8d;
  --border: #dfe6e9;
  --card-bg: #ffffff;
  --shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

body {
  background-color: var(--secondary);
  color: var(--text);
  line-height: 1.6;
  padding-bottom: 60px; /* 为底部导航留空间 */
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 15px;
}

.page-title {
  font-size: 1.5rem;
  margin: 20px 0;
  font-weight: 600;
}

.card {
  background-color: var(--card-bg);
  border-radius: 10px;
  box-shadow: var(--shadow);
  padding: 20px;
  margin-bottom: 20px;
}

.btn {
  padding: 12px 20px;
  border-radius: 5px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary {
  background-color: var(--primary);
  color: white;
  flex: 1;
}

.btn-primary:hover {
  background-color: var(--primary-dark);
}

.btn-outline {
  background-color: transparent;
  border: 1px solid var(--primary);
  color: var(--primary);
}

.btn-outline:hover {
  background-color: rgba(52, 152, 219, 0.1);
}

@media (max-width: 768px) {
  .container {
    padding: 0 10px;
  }
}
</style>