-- =====================================================
-- CAMPUSMIND AI - SUPABASE POSTGRESQL SCHEMA
-- Upgraded schema with pgvector, student profiles,
-- document embeddings, notices, exams, and chat history.
-- =====================================================

-- 1. Enable pgvector extension (if available in your Supabase project)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Users / Profiles Table
CREATE TABLE IF NOT EXISTS users (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(50) DEFAULT 'student', -- 'guest', 'student', 'alumni', 'faculty', 'admin'
    department VARCHAR(100) DEFAULT 'Computer Science', -- 'Computer Science', 'Information Technology', 'Electronics', 'Mechanical', 'Civil'
    year_of_study VARCHAR(50) DEFAULT '1st Year', -- '1st Year', '2nd Year', '3rd Year', '4th Year'
    semester INT DEFAULT 1,
    student_id VARCHAR(100),
    avatar_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_year ON users(year_of_study);

-- 3. Documents Table (For RAG Pipeline)
CREATE TABLE IF NOT EXISTS documents (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) DEFAULT 'pdf',
    category VARCHAR(50) DEFAULT 'general', -- 'syllabus', 'notice', 'timetable', 'event', 'handbook', 'policy'
    department VARCHAR(100) DEFAULT 'All',
    target_year VARCHAR(50) DEFAULT 'All', -- '1st Year', '2nd Year', '3rd Year', '4th Year', 'All'
    content TEXT,
    file_url TEXT,
    uploaded_by VARCHAR(255) DEFAULT 'admin',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Document Chunks & Embeddings Table
CREATE TABLE IF NOT EXISTS document_chunks (
    id BIGSERIAL PRIMARY KEY,
    document_id BIGINT REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INT NOT NULL,
    chunk_text TEXT NOT NULL,
    embedding vector(384), -- Standard dimension or dense representation
    embedding_json TEXT, -- JSON fallback for environments without pgvector
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_doc_chunks_doc_id ON document_chunks(document_id);

-- Vector Similarity Search RPC Function
CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(384),
    match_count INT DEFAULT 5,
    filter_department VARCHAR DEFAULT 'All',
    filter_year VARCHAR DEFAULT 'All'
)
RETURNS TABLE (
    id BIGINT,
    document_id BIGINT,
    chunk_text TEXT,
    metadata JSONB,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        dc.id,
        dc.document_id,
        dc.chunk_text,
        dc.metadata,
        1 - (dc.embedding <=> query_embedding) AS similarity
    FROM document_chunks dc
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- 5. Subjects / Courses Table
CREATE TABLE IF NOT EXISTS subjects (
    id BIGSERIAL PRIMARY KEY,
    subject_code VARCHAR(50) NOT NULL,
    subject_name VARCHAR(255) NOT NULL,
    department VARCHAR(100) NOT NULL,
    year_of_study VARCHAR(50) NOT NULL, -- '1st Year', '2nd Year', '3rd Year', '4th Year'
    semester INT NOT NULL,
    credits INT DEFAULT 4,
    instructor VARCHAR(255),
    syllabus_summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_subjects_year_dept ON subjects(year_of_study, department);

-- 6. Exams & Schedule Table
CREATE TABLE IF NOT EXISTS exams (
    id BIGSERIAL PRIMARY KEY,
    subject_id BIGINT REFERENCES subjects(id) ON DELETE SET NULL,
    subject_name VARCHAR(255) NOT NULL,
    subject_code VARCHAR(50),
    department VARCHAR(100) NOT NULL,
    year_of_study VARCHAR(50) NOT NULL,
    semester INT NOT NULL,
    exam_type VARCHAR(50) DEFAULT 'Mid-Term', -- 'Quiz', 'Mid-Term', 'End-Term', 'Practical'
    exam_date DATE NOT NULL,
    start_time VARCHAR(20) NOT NULL,
    end_time VARCHAR(20) NOT NULL,
    room_no VARCHAR(50) DEFAULT 'Main Hall',
    syllabus_topics TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_exams_year_dept ON exams(year_of_study, department);

-- 7. Notices & Announcements Table
CREATE TABLE IF NOT EXISTS notices (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'Academic', -- 'Academic', 'Exam', 'Placement', 'Event', 'Urgent'
    department VARCHAR(100) DEFAULT 'All',
    target_year VARCHAR(50) DEFAULT 'All', -- '1st Year', '2nd Year', '3rd Year', '4th Year', 'All'
    priority VARCHAR(20) DEFAULT 'Normal', -- 'Low', 'Normal', 'High', 'Urgent'
    published_by VARCHAR(255) DEFAULT 'Campus Administration',
    published_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_notices_target ON notices(target_year, department);

-- 8. Campus Events Table
CREATE TABLE IF NOT EXISTS events (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) DEFAULT 'Workshop', -- 'Hackathon', 'Cultural', 'Sports', 'Seminar', 'Workshop'
    venue VARCHAR(255) NOT NULL,
    event_date TIMESTAMPTZ NOT NULL,
    end_date TIMESTAMPTZ,
    organizer VARCHAR(255) DEFAULT 'Student Council',
    registration_link TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Chat Sessions & Messages Table (Chat History)
CREATE TABLE IF NOT EXISTS chat_sessions (
    id VARCHAR(100) PRIMARY KEY,
    user_id BIGINT REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) DEFAULT 'New Conversation',
    persona VARCHAR(50) DEFAULT 'student',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS chat_messages (
    id BIGSERIAL PRIMARY KEY,
    session_id VARCHAR(100) REFERENCES chat_sessions(id) ON DELETE CASCADE,
    user_id BIGINT REFERENCES users(id) ON DELETE SET NULL,
    role VARCHAR(50) NOT NULL, -- 'user', 'assistant', 'system'
    content TEXT NOT NULL,
    sources_used JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session ON chat_messages(session_id);
