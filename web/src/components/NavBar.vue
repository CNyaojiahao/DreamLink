<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()
const searchKeyword = ref('')

function handleSearch() {
  const q = searchKeyword.value.trim()
  if (q) {
    router.push({ path: '/search', query: { q } })
  }
}
</script>

<template>
  <nav class="navbar glass">
    <div class="navbar-left">
      <router-link to="/" class="logo">DreamLink</router-link>
    </div>

    <div class="navbar-center">
      <form class="search-box" @submit.prevent="handleSearch">
        <input
          v-model="searchKeyword"
          type="text"
          placeholder="搜索视频..."
          class="search-input"
        />
        <button type="submit" class="search-btn">搜索</button>
      </form>
    </div>

    <div class="navbar-right">
      <router-link to="/upload" class="btn btn-primary">投稿</router-link>

      <template v-if="userStore.isLoggedIn">
        <router-link :to="`/user/${userStore.user?.id}`" class="user-info">
          <span>{{ userStore.user?.username }}</span>
        </router-link>
        <button class="btn" @click="userStore.logout(); router.push('/')">退出</button>
      </template>

      <template v-else>
        <router-link to="/login" class="btn">登录</router-link>
        <router-link to="/register" class="btn btn-primary">注册</router-link>
      </template>
    </div>
  </nav>
</template>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  height: 56px;
  gap: 16px;
}

.logo {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
  flex-shrink: 0;
}

.search-box {
  display: flex;
  flex: 1;
  max-width: 400px;
}

.search-input {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px 0 0 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  min-width: 0;
}

.search-input:focus {
  border-color: var(--primary-color);
}

.search-btn {
  padding: 6px 16px;
  border: none;
  border-radius: 0 8px 8px 0;
  background: var(--primary-color);
  color: white;
  cursor: pointer;
  font-size: 14px;
  flex-shrink: 0;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.user-info {
  color: var(--text-primary);
  font-size: 14px;
}

@media (max-width: 768px) {
  .navbar {
    padding: 0 12px;
    gap: 8px;
  }

  .search-box {
    max-width: 200px;
  }

  .navbar-right .btn {
    padding: 6px 10px;
    font-size: 13px;
  }

  .user-info span {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar {
    flex-wrap: wrap;
    height: auto;
    padding: 8px 12px;
    gap: 8px;
  }

  .navbar-left {
    order: 1;
  }

  .navbar-right {
    order: 2;
    gap: 8px;
  }

  .navbar-center {
    order: 3;
    width: 100%;
  }

  .search-box {
    max-width: 100%;
    width: 100%;
  }
}
</style>
