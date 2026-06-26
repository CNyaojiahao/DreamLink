<script setup lang="ts">
import { ref } from 'vue'

const title = ref('')
const description = ref('')

const error = ref('')

function handleSubmit() {
  // TODO: 实现视频上传逻辑（里程碑 4）
  error.value = '上传功能尚未实现'
}
</script>

<template>
  <div class="upload-page">
    <h2>投稿</h2>
    <form class="upload-form glass" @submit.prevent="handleSubmit">
      <div class="form-group">
        <label>视频标题</label>
        <input v-model="title" type="text" required placeholder="请输入标题" maxlength="100" />
      </div>
      <div class="form-group">
        <label>视频简介</label>
        <textarea v-model="description" placeholder="请输入简介" rows="4" />
      </div>
      <div class="form-group">
        <label>视频文件</label>
        <input type="file" accept="video/mp4,video/webm" disabled />
        <p class="hint">上传功能即将上线</p>
      </div>
      <p v-if="error" class="error-msg">{{ error }}</p>
      <button type="submit" class="btn btn-primary" disabled>提交</button>
    </form>
  </div>
</template>

<style scoped>
.upload-page {
  max-width: 640px;
  margin: 0 auto;
  padding: 24px;
}

h2 {
  margin-bottom: 20px;
}

.upload-form {
  padding: 24px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--text-secondary);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  outline: none;
  font-family: inherit;
}

.form-group input:focus,
.form-group textarea:focus {
  border-color: var(--primary-color);
}

.hint {
  margin-top: 6px;
  font-size: 12px;
  color: var(--text-secondary);
}

.error-msg {
  color: #f85149;
  font-size: 14px;
  margin-bottom: 8px;
}
</style>
