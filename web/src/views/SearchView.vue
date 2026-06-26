<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const videos = ref<any[]>([])
const loading = ref(false)
const total = ref(0)

async function search() {
  const q = route.query.q as string
  if (!q) return

  loading.value = true
  try {
    const res = await api.get('/search', { params: { q, page: 1, page_size: 20 } })
    videos.value = res.data.data?.items ?? []
    total.value = res.data.data?.total ?? 0
  } catch {
    videos.value = []
  } finally {
    loading.value = false
  }
}

onMounted(search)
watch(() => route.query.q, search)
</script>

<template>
  <div class="search-page">
    <h2>搜索：{{ route.query.q }}</h2>
    <p class="result-count" v-if="!loading">共 {{ total }} 条结果</p>

    <div v-if="loading" class="loading">搜索中...</div>

    <div v-else-if="videos.length === 0" class="empty">没有找到相关视频</div>

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
          <h3>{{ v.title }}</h3>
          <p class="meta">{{ v.author?.username }} · {{ v.view_count }} 播放</p>
        </div>
      </router-link>
    </div>
  </div>
</template>

<style scoped>
.search-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
}

@media (max-width: 480px) {
  .search-page {
    padding: 16px;
  }

  .video-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 12px;
  }
}

.result-count {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 20px;
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

.info h3 {
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

.loading, .empty {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}
</style>
