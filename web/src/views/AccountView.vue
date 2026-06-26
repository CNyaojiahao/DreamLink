<script setup lang="ts">
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { onMounted } from 'vue'

const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  if (!userStore.isLoggedIn) {
    router.push('/login')
  }
})
</script>

<template>
  <div class="account-page">
    <h2>个人中心</h2>
    <div v-if="userStore.user" class="account-content glass">
      <div class="section">
        <h3>基本信息</h3>
        <p>用户名：{{ userStore.user.username }}</p>
        <p>邮箱：{{ userStore.user.email }}</p>
        <p>简介：{{ userStore.user.bio || '暂无简介' }}</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.account-page {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.account-content {
  padding: 24px;
  margin-top: 16px;
}

.section h3 {
  margin-bottom: 12px;
}

.section p {
  margin-bottom: 8px;
  color: var(--text-secondary);
}
</style>
