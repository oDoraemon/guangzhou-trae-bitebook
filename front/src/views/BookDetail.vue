<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchBook } from '../services/books'
import type { Book } from '../types/book'

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
</script>

<template>
  <div class="container">
    <el-button class="back" @click="back">返回列表</el-button>
    <h1>图书详情</h1>
    <div v-if="error" class="error">{{ error }}</div>
    <el-skeleton animated :loading="loading">
      <template #template>
        <el-skeleton-item variant="h1" style="width: 40%" />
        <el-skeleton-item variant="text" />
        <el-skeleton-item variant="text" />
      </template>
      <template #default>
        <el-card v-if="book">
          <el-descriptions title="基本信息" :column="1" border>
            <el-descriptions-item label="书名">{{ book.title }}</el-descriptions-item>
            <el-descriptions-item label="作者">{{ book.author }}</el-descriptions-item>
            <el-descriptions-item label="出版年">{{ book.published_year ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="ISBN">{{ book.isbn ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="简介">{{ book.description ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="ID">{{ book.id }}</el-descriptions-item>
          </el-descriptions>
        </el-card>
      </template>
    </el-skeleton>
  </div>
</template>

<style scoped>
.container { max-width: 100%; margin: 0 auto; padding: 16px 0; }
.back { margin-bottom: 12px; }
.error { color: #c00; margin: 8px 0; }
</style>
