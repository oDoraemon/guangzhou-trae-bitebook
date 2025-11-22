import { http } from './api'
import type { Book, BookListResponse } from '../types/book'

export function fetchBooks(params: { q?: string; page?: number; page_size?: number } = {}) {
  const q = params.q ? `q=${encodeURIComponent(params.q)}` : ''
  const page = params.page ? `page=${params.page}` : ''
  const page_size = params.page_size ? `page_size=${params.page_size}` : ''
  const query = [q, page, page_size].filter(Boolean).join('&')
  const suffix = query ? `?${query}` : ''
  return http<BookListResponse>(`/api/books/${suffix}`)
}

export function fetchBook(id: number) {
  return http<Book>(`/api/books/${id}`)
}

