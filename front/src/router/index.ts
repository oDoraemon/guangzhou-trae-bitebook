import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  { path: '/', redirect: '/books' },
  { path: '/books', name: 'BooksList', component: () => import('../views/BooksList.vue') },
  { path: '/books/:id', name: 'BookDetail', component: () => import('../views/BookDetail.vue') },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})
