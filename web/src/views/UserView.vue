<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const user = ref<any>(null)
const videos = ref<any[]>([])
const loading = ref(true)

onMounted(async () => {
  try {
    const [userRes, videosRes] = await Promise.all([
      api.get(`/users/${route.params.id}`),
      api.get(`/users/${route.params.id}/videos`)
    ])
    user.value = userRes.data.data
    videos.value = videosRes.data.data?.items ?? []
  } catch {
    // 静默失败
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="user-page">
    <div v-if="loading" class="loading">加载中...</div>
    <template v-else-if="user">
      <div class="user-header glass">
        <div class="avatar">
          <img v-if="user.avatar" :src="user.avatar" :alt="user.username" />
          <div v-else class="avatar-placeholder">{{ user.username?.[0] }}</div>
        </div>
        <div class="user-meta">
          <h2>{{ user.username }}</h2>
          <p class="bio">{{ user.bio || '这个人很懒，什么都没写' }}</p>
        </div>
      </div>

      <h3 class="section-title">投稿 ({{ videos.length }})</h3>
      <div class="video-grid">
        <router-link
          v-for="v in videos"
          :key="v.id"
          :to="`/video/${v.id}`"
          class="video-card glass"
        >
          <div class="cover">
            <img :src="v.cover" :alt="v.title" loading="lazy" />
          </div>
          <div class="info">
            <h4>{{ v.title }}</h4>
            <p class="meta">{{ v.view_count }} 播放</p>
          </div>
        </router-link>
      </div>
    </template>
    <div v-else class="loading">用户不存在</div>
  </div>
</template>

<style scoped>
.user-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  padding: 24px;
  margin-bottom: 24px;
}

.avatar img, .avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  font-size: 32px;
  font-weight: 700;
}

.user-meta h2 {
  font-size: 20px;
}

.bio {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.section-title {
  margin-bottom: 16px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

.video-card {
  display: block;
  overflow: hidden;
  transition: transform 0.2s;
}

.video-card:hover {
  transform: translateY(-4px);
}

.cover {
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: var(--bg-secondary);
}

.cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.info {
  padding: 12px;
}

.info h4 {
  font-size: 14px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.loading {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}
</style>
