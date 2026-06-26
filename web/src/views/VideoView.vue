<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api'

const route = useRoute()
const video = ref<any>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const res = await api.get(`/videos/${route.params.id}`)
    video.value = res.data.data
  } catch (e: any) {
    error.value = e.response?.data?.error?.message ?? '视频不存在'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="video-view">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <template v-else-if="video">
      <div class="player-area">
        <video controls :src="video.parts?.[0]?.file_path" class="player" />
      </div>

      <div class="video-info">
        <h1>{{ video.title }}</h1>
        <p class="meta">
          {{ video.author?.username }} · {{ video.view_count }} 播放 · {{ video.created_at }}
        </p>
        <p class="desc">{{ video.description }}</p>
      </div>
    </template>
  </div>
</template>

<style scoped>
.video-view {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
}

.player {
  width: 100%;
  border-radius: 12px;
  background: #000;
}

.video-info {
  margin-top: 16px;
}

.video-info h1 {
  font-size: 20px;
}

.meta {
  margin-top: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.desc {
  margin-top: 12px;
  color: var(--text-primary);
  font-size: 14px;
  line-height: 1.6;
}

.loading, .error {
  text-align: center;
  padding: 60px 0;
  color: var(--text-secondary);
}
</style>
