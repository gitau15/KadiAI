-- =============================================
-- Supabase pgvector migration for Election Law AI
-- Run this in Supabase SQL Editor (supabase.com > SQL Editor > New Query)
-- =============================================

-- 1. Enable pgvector extension
create extension if not exists vector with schema extensions;

-- 2. Create document_chunks table
create table if not exists document_chunks (
    id uuid primary key default gen_random_uuid(),
    document text not null,
    section text not null default '',
    page integer not null default 0,
    chunk_index integer not null default 0,
    chunk_text text not null,
    document_id text not null,
    source_url text not null default '',
    embedding vector(384) not null,
    created_at timestamptz not null default now()
);

-- 3. Create HNSW index for fast cosine similarity search
create index if not exists idx_document_chunks_embedding
    on document_chunks
    using hnsw (embedding vector_cosine_ops)
    with (m = 16, ef_construction = 64);

-- 4. Create index on document_id for faster aggregation
create index if not exists idx_document_chunks_doc_id
    on document_chunks (document_id);

-- 5. Create the similarity search function
create or replace function match_documents(
    query_embedding vector(384),
    match_count int default 5,
    filter_doc_ids text[] default null
)
returns table (
    id uuid,
    document text,
    section text,
    page integer,
    chunk_index integer,
    chunk_text text,
    document_id text,
    source_url text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        dc.id,
        dc.document,
        dc.section,
        dc.page,
        dc.chunk_index,
        dc.chunk_text,
        dc.document_id,
        dc.source_url,
        1 - (dc.embedding <=> query_embedding) as similarity
    from document_chunks dc
    where filter_doc_ids is null or dc.document_id = any(filter_doc_ids)
    order by dc.embedding <=> query_embedding
    limit match_count;
end;
$$;

-- 6. Create list_unique_documents function for the sources endpoint
create or replace function list_unique_documents()
returns table (
    document_id text,
    document text,
    document_type text,
    page_count bigint,
    source_url text
)
language plpgsql
as $$
begin
    return query
    select distinct on (dc.document_id)
        dc.document_id,
        dc.document,
        case
            when lower(dc.document) like any(array['%act%', '%constitution%', '%regulation%'])
            then 'statute'
            else 'case_law'
        end as document_type,
        count(*) over (partition by dc.document_id) as page_count,
        dc.source_url
    from document_chunks dc
    order by dc.document_id;
end;
$$;

-- 7. Row-level security (optional - disabled for service-role access)
alter table document_chunks enable row level security;

-- Allow service role full access (your backend uses service-role key)
create policy "Service role full access"
    on document_chunks
    for all
    using (true)
    with check (true);
