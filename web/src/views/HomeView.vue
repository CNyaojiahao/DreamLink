<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/api'

interface VideoItem {
  id: number
  title: string
  cover: string
  author: { id: number; username: string }
  view_count: number
  created_at: string
}

const videos = ref<VideoItem[]>([])
const loading = ref(false)

onMounted(async () => {
  loading.value = true
  try {
    const res = await api.get('/videos', { params: { page: 1, page_size: 20 } })
    videos.value = res.data.data?.items ?? []
  } catch {
    // 后端未就绪时静默失败
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="home">
    <h2>推荐视频</h2>

    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="videos.length === 0" class="empty">
      暂无视频，<router-link to="/upload">去投稿</router-link>
    </div>

    <div v-else class="video-grid">
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
          <h3 class="title">{{ v.title }}</h3>
          <p class="meta">{{ v.author?.username }} · {{ v.view_count }} 播放</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.home {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

h2 {
  margin-bottom: 20px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}

@media (max-width: 480px) {
  .home {
    padding: 16px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
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

.title {
  font-size: 14px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.meta {
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.loading, .empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}
</style>
