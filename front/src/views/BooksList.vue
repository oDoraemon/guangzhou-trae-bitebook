<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { fetchBooks } from '../services/books'
import type { Book } from '../types/book'
import placeholder from '../assets/book-placeholder.svg'
import { API_BASE } from '../services/api'
import { ElMessage } from 'element-plus'
import { GlobalWorkerOptions, getDocument } from 'pdfjs-dist/build/pdf'
import workerSrc from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

const router = useRouter()
const items = ref<Book[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(10)
const q = ref('')
const loading = ref(false)
const error = ref('')

const dialogVisible = ref(false)
const uploadRef = ref()
const previewCanvas = ref<HTMLCanvasElement | null>(null)
const form = ref({
  title: '',
  author: '',
  description: '',
  published_year: undefined as undefined | number,
  isbn: '',
})
const uploadAction = `${API_BASE}/api/upload/book`
const hasFile = ref(false)

GlobalWorkerOptions.workerSrc = workerSrc

async function renderPdfPreview(file: File) {
  try {
    const buf = await file.arrayBuffer()
    const pdf = await getDocument({ data: buf }).promise
    const page = await pdf.getPage(1)
    const viewport0 = page.getViewport({ scale: 1 })
    const targetH = 320
    const scale = Math.min(targetH / viewport0.height, 2)
    const viewport = page.getViewport({ scale })
    const canvas = previewCanvas.value
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return
    const dpr = window.devicePixelRatio || 1
    canvas.width = Math.floor(viewport.width * dpr)
    canvas.height = Math.floor(viewport.height * dpr)
    canvas.style.width = `${viewport.width}px`
    canvas.style.height = `${viewport.height}px`
    const renderContext = { canvasContext: ctx, viewport, transform: dpr !== 1 ? [dpr, 0, 0, dpr, 0, 0] : undefined }
    await page.render(renderContext).promise
  } catch (e) {
    console.error(e)
  }
}

function onUploadChange(file: any, files: any[]) {
  hasFile.value = files && files.length > 0
  const f = files?.[0]
  const name: string = f?.name || ''
  if (name) {
    const stem = name.replace(/\.pdf$/i, '')
    if (!form.value.title) form.value.title = stem
  }
  const raw: File | undefined = (file && (file.raw as File)) || (f && (f.raw as File))
  if (raw) renderPdfPreview(raw)
}

const uploadData = computed(() => {
  const d: any = {}
  const { title, author, description, published_year, isbn } = form.value as any
  if (title) d.title = title
  if (author) d.author = author
  if (description) d.description = description
  if (typeof published_year === 'number' && !Number.isNaN(published_year)) d.published_year = published_year
  if (isbn) d.isbn = isbn
  return d
})

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

function openAdd() {
  dialogVisible.value = true
}

function resetForm() {
  form.value = { title: '', author: '', description: '', published_year: undefined, isbn: '' }
  uploadRef.value?.clearFiles?.()
}

function onUploadSuccess() {
  ElMessage.success('上传成功')
  dialogVisible.value = false
  resetForm()
  load()
}

function onUploadError() {
  ElMessage.error('上传失败')
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
      <el-button type="success" @click="openAdd">添加图书</el-button>
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
    <el-dialog v-model="dialogVisible" title="上传图书" width="720">
      <div class="upload-grid">
        <div class="u-left">
          <canvas ref="previewCanvas" class="pdf-preview"></canvas>
          <el-upload
            ref="uploadRef"
            drag
            :action="uploadAction"
            name="file"
            :auto-upload="false"
            :limit="1"
            :data="uploadData"
            :on-success="onUploadSuccess"
            :on-error="onUploadError"
            :on-change="onUploadChange"
            accept="application/pdf"
          >
            <div class="el-upload__text">拖拽文件到此处，或<em>点击上传</em></div>
            <template #tip>
              <div class="el-upload__tip">仅支持 PDF 文件</div>
            </template>
          </el-upload>
        </div>
        <div class="u-right">
          <el-form label-width="96px">
            <el-form-item label="书名">
              <el-input v-model="form.title" />
            </el-form-item>
            <el-form-item label="作者">
              <el-input v-model="form.author" />
            </el-form-item>
            <el-form-item label="出版年">
              <el-input v-model.number="form.published_year" placeholder="例如：1997" />
            </el-form-item>
            <el-form-item label="ISBN">
              <el-input v-model="form.isbn" />
            </el-form-item>
            <el-form-item label="简介">
              <el-input type="textarea" v-model="form.description" rows="3" />
            </el-form-item>
          </el-form>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="dialogVisible=false">取消</el-button>
          <el-button type="primary" :disabled="!hasFile || !form.title" @click="uploadRef?.submit?.()">上传</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
  
</template>

<style scoped>
.container { max-width: 100%; margin: 0 auto; padding: 16px 0; }
.toolbar { display: flex; gap: 8px; margin-bottom: 12px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; }
.card { cursor: pointer; padding: 0}
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
.upload-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.u-left, .u-right { width: 100%; }
.dialog-footer { display: flex; justify-content: flex-end; gap: 8px; }
@media (max-width: 700px) {
  .upload-grid { grid-template-columns: 1fr; }
}
.pdf-preview { width: 100%; max-height: 320px; border: 1px solid #eee; border-radius: 6px; margin-bottom: 8px; }
</style>
