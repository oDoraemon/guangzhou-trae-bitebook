<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchBook } from '../services/books'
import type { Book } from '../types/book'
import placeholder from '../assets/book-placeholder.svg'

const route = useRoute()
const router = useRouter()
const book = ref<Book | null>(null)
const error = ref('')
const loading = ref(false)

async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = Number(route.params.id)
    const res = await fetchBook(id)
    book.value = res
  } catch (e: any) {
    error.value = e?.message || 'Error'
  } finally {
    loading.value = false
  }
}

function back() {
  router.push('/books')
}

onMounted(load)

const previewList = computed(() => {
  const list = book.value?.preview_images || []
  const cover = book.value?.cover_url
  const arr = [...list]
  if (cover) arr.unshift(cover)
  return arr.length ? arr : [placeholder]
})
</script>

<template>
  <div class="container">
    <el-button class="back" @click="back">返回列表</el-button>
    <h1>图书详情</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <el-skeleton animated :loading="loading">
      <template #default>
        <div class="detail-grid" v-if="book">
          <div class="left">
            <el-card>
              <el-image :src="book.cover_url || placeholder" fit="cover" class="cover" :preview-src-list="previewList"/>
              <div class="thumbs">
                <el-image v-for="(src, i) in previewList" :key="i" :src="src" fit="cover" class="thumb" @click="() => {}"/>
              </div>
            </el-card>
          </div>
          <div class="right">
            <el-card>
              <el-descriptions title="基本信息" :column="1" border>
                <el-descriptions-item label="书名">{{ book.title }}</el-descriptions-item>
                <el-descriptions-item label="作者">{{ book.author }}</el-descriptions-item>
                <el-descriptions-item label="出版年">{{ book.published_year ?? '-' }}</el-descriptions-item>
                <el-descriptions-item label="ISBN">{{ book.isbn ?? '-' }}</el-descriptions-item>
                <el-descriptions-item label="简介">{{ book.description ?? '-' }}</el-descriptions-item>
                <el-descriptions-item label="ID">{{ book.id }}</el-descriptions-item>
              </el-descriptions>
            </el-card>
          </div>
        </div>
      </template>
      <template #template>
        <el-skeleton-item variant="rect" style="width: 100%; height: 280px" />
        <el-skeleton-item variant="text" />
        <el-skeleton-item variant="text" />
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.container { max-width: 100%; margin: 0 auto; padding: 16px 0; }
.back { margin-bottom: 12px; }
.error { color: #c00; margin: 8px 0; }

.detail-grid { display: grid; grid-template-columns: 60% 40%; gap: 16px; }
.cover { width: 100%; height: 320px; object-fit: cover; border-radius: 6px; }
.thumbs { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin-top: 10px; }
.thumb { width: 100%; aspect-ratio: 1/1; object-fit: cover; border-radius: 4px; }

@media (max-width: 960px) {
  .detail-grid { grid-template-columns: 60% 40%; gap: 12px; }
}
@media (max-width: 700px) {
  .detail-grid { grid-template-columns: 1fr; }
}
</style>
