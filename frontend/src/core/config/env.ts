const publicApiBase =
  typeof process !== 'undefined' ? process.env.NEXT_PUBLIC_API_BASE_URL : undefined

export const API_BASE_URL = publicApiBase ?? 'http://localhost:8000'
