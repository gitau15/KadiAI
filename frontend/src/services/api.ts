import axios from 'axios'
import type { QueryResponse, SourceDocument, SourceContext } from '@/types'

const client = axios.create({
  baseURL: '/api/v1',
  timeout: 300000,
})

export async function askQuery(query: string, topK: number = 5): Promise<QueryResponse> {
  const { data } = await client.post<QueryResponse>('/query', { query, top_k: topK })
  return data
}

export async function listSources(): Promise<SourceDocument[]> {
  const { data } = await client.get<SourceDocument[]>('/sources')
  return data
}

export async function getSourceContext(chunkId: string): Promise<SourceContext> {
  const { data } = await client.get<SourceContext>(`/sources/${chunkId}/context`)
  return data
}

export async function healthCheck(): Promise<boolean> {
  try {
    await client.get('/health')
    return true
  } catch {
    return false
  }
}

export interface SchedulerStatus {
  enabled: boolean
  is_running: boolean
  last_run: string | null
  last_result: any
  next_run: string | null
  schedule: string
}

export async function getSchedulerStatus(): Promise<SchedulerStatus> {
  const { data } = await client.get<SchedulerStatus>('/scheduler/status')
  return data
}

export async function triggerManualScrape(): Promise<{ message: string }> {
  const { data } = await client.post('/scheduler/run')
  return data
}
