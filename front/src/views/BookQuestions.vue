<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchQuestions, type QuestionItem } from '../services/questions'

const route = useRoute()
const router = useRouter()
const items = ref<QuestionItem[]>([])
const total = ref(0)
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const id = Number(route.params.id)
    const res = await fetchQuestions(id, { start: 0, limit: 100 })
    items.value = res.items
    total.value = res.total
  } catch (e: any) {
    error.value = e?.message || 'Error'
  } finally {
    loading.value = false
  }
}

function back() { router.push(`/books/${route.params.id}`) }

onMounted(load)
</script>

<template>
  <div class="container">
    <div class="toolbar">
      <el-button @click="back">返回详情</el-button>
      <h2>难题列表</h2>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-loading="loading">
      <el-empty v-if="!items.length && !loading" description="暂无数据" />
      <el-card v-for="q in items" :key="q.id" class="qcard" shadow="hover">
        <div class="row">
          <el-tag type="info">页面：{{ q.page_number ?? '-' }}</el-tag>
        </div>
        <div class="qtext">{{ q.text }}</div>
        <div class="exp" v-if="q.explanation">解析：{{ q.explanation }}</div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.container { max-width: 100%; margin: 0 auto; padding: 16px 0; }
.toolbar { display: flex; align-items: center; gap: 12px; }
.error { color: #c00; margin: 8px 0; }
.qcard { margin-bottom: 12px; }
.row { margin-bottom: 6px; }
.qtext { font-weight: 600; margin-bottom: 6px; }
.exp { color: #444; }
</style>

