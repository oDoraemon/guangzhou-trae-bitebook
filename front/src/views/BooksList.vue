<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchBooks } from '../services/books'
import type { Book } from '../types/book'
import placeholder from '../assets/book-placeholder.svg'

const router = useRouter()
const items = ref<Book[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const q = ref('')
const loading = ref(false)
const error = ref('')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const res = await fetchBooks({ q: q.value || undefined, page: page.value, page_size: pageSize.value })
    items.value = res.items
    total.value = res.total
  } catch (e: any) {
    error.value = e?.message || 'Error'
  } finally {
    loading.value = false
  }
}

function onSearch() {
  page.value = 1
  load()
}

function toDetail(id: number) {
  router.push(`/books/${id}`)
}

onMounted(load)
watch([page, pageSize], load)
</script>

<template>
  <div class="container">
    <h1>图书列表</h1>
    <div class="toolbar">
      <el-input v-model="q" placeholder="搜索标题/作者/ISBN" clearable style="max-width: 340px" />
      <el-button type="primary" @click="onSearch">搜索</el-button>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
    <div v-loading="loading" class="grid">
      <el-card v-for="b in items" :key="b.id" class="card" shadow="hover" @click="toDetail(b.id)">
        <el-image :src="b.cover_url || placeholder" fit="cover" class="cover" />
        <div class="meta">
          <div class="title" :title="b.title">{{ b.title }}</div>
          <div class="sub">{{ b.author }}</div>
          <div class="sub">{{ b.published_year ?? '-' }}</div>
        </div>
      </el-card>
    </div>
    <div class="pager">
      <el-pagination
        background
        layout="prev, pager, next, sizes, total"
        :total="total"
        :page-size="pageSize"
        :current-page="page"
        @size-change="(s:number)=>{pageSize=s}"
        @current-change="(p:number)=>{page=p}"
      />
    </div>
  </div>
  
</template>

<style scoped>
.container { max-width: 100%; margin: 0 auto; padding: 16px 0; }
.toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.card { cursor: pointer; }
.cover { width: 100%; aspect-ratio: 2/3; object-fit: cover; border-radius: 6px; }
.meta { margin-top: 8px; }
.title { font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.sub { color: #666; font-size: 12px; }
.pager { display: flex; justify-content: flex-end; margin-top: 12px; }
.error { color: #c00; margin: 8px 0; }

@media (max-width: 960px) {
  .grid { grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 10px; }
}
@media (max-width: 700px) {
  .grid { grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 8px; }
}
</style>
