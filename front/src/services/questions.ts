import { http } from './api'

export interface QuestionItem {
  id: number
  book_id: number
  doc_text_id?: number | null
  page_number?: number | null
  text: string
  explanation?: string | null
}

export interface QuestionListResponse {
  items: QuestionItem[]
  total: number
  start: number
  limit: number
}

export function fetchQuestions(bookId: number, params: { start?: number; limit?: number } = {}) {
  const start = params.start != null ? `start=${params.start}` : ''
  const limit = params.limit != null ? `limit=${params.limit}` : ''
  const query = [start, limit].filter(Boolean).join('&')
  const suffix = query ? `?${query}` : ''
  return http<QuestionListResponse>(`/api/books/${bookId}/questions${suffix}`)
}

