const defaultBase = 'http://localhost:8000'
const envBase = (import.meta as any).env?.VITE_API_BASE
export const API_BASE = envBase !== undefined ? envBase : defaultBase

export async function http<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) throw new Error(`${res.status}`)
  return res.json() as Promise<T>
}
