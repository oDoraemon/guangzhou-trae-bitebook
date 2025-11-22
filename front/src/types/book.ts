export interface Book {
  id: number
  title: string
  author: string
  description?: string | null
  published_year?: number | null
  isbn?: string | null
  cover_url?: string | null
  preview_images?: string[] | null
}

export interface BookListResponse {
  items: Book[]
  total: number
  page: number
  page_size: number
}
