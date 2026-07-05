export interface Citation {
  document: string
  section: string
  page: number
  chunk_text: string
  chunk_id: string
}

export interface QueryResponse {
  query: string
  answer: string
  citations: Citation[]
  processing_time_ms: number
  session_id?: string
}

export interface SourceDocument {
  id: string
  title: string
  document_type: 'statute' | 'case_law'
  page_count: number
  ingested_at: string
  source_url?: string
}

export interface SourceContext {
  chunk_id: string
  document: string
  section: string
  page: number
  chunk_text: string
  previous_chunk_text?: string
  next_chunk_text?: string
}

export interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  citations?: Citation[]
  timestamp: number
}
