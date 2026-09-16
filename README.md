# KnowBase AI — V1

> **AI-powered business knowledge assistant for organizations**
>
> V1 goal: allow an organization to upload PDF documents, process their text, generate embeddings, store them in PostgreSQL + pgvector, and ask natural-language questions that are answered using retrieved document context with source/page citations.

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. V1 Objective](#2-v1-objective)
- [3. V1 Scope](#3-v1-scope)
- [4. Explicitly NOT in V1](#4-explicitly-not-in-v1)
- [5. Architecture](#5-architecture)
- [6. Technology Stack](#6-technology-stack)
- [7. Python AI Service](#7-python-ai-service)
- [8. Database](#8-database)
- [9. Database Architecture](#9-database-architecture)
- [10. Core Tables](#10-core-tables)
- [11. Users](#11-users)
- [12. Organizations](#12-organizations)
- [13. Organization Membership](#13-organization-membership)
- [14. Multi-Tenant Security](#14-multi-tenant-security)
- [15. Documents](#15-documents)
- [16. Document Versions](#16-document-versions)
- [17. Document Chunks](#17-document-chunks)
- [18. Chunking Strategy — V1](#18-chunking-strategy--v1)
- [19. Page Preservation](#19-page-preservation)
- [20. Embedding Model](#20-embedding-model)
- [21. Embedding Rules](#21-embedding-rules)
- [22. RAG Pipeline](#22-rag-pipeline)
- [23. Vector Search](#23-vector-search)
- [24. Retrieval Security](#24-retrieval-security)
- [25. RAG Context](#25-rag-context)
- [26. LLM Rules](#26-llm-rules)
- [27. Citations](#27-citations)
- [28. Conversations](#28-conversations)
- [29. Messages](#29-messages)
- [30. Processing Status](#30-processing-status)
- [31. Python AI Service Responsibilities](#31-python-ai-service-responsibilities)
- [32. Recommended Python Structure](#32-recommended-python-structure)
- [33. Python Environment](#33-python-environment)
- [34. V1 Development Order](#34-v1-development-order)
- [35. First Milestone](#35-first-milestone)
- [36. Testing Strategy](#36-testing-strategy)
- [37. Error Handling](#37-error-handling)
- [38. Logging](#38-logging)
- [39. Configuration](#39-configuration)
- [40. Git Rules](#40-git-rules)
- [41. Coding Principles](#41-coding-principles)
- [42. LangChain Policy](#42-langchain-policy)
- [43. LangGraph Policy](#43-langgraph-policy)
- [44. Future Architecture](#44-future-architecture)
- [45. Important Architectural Decisions](#45-important-architectural-decisions)
- [46. AI Agent Instructions](#46-ai-agent-instructions)
- [47. AI Coding Agent Workflow](#47-ai-coding-agent-workflow)
- [48. Definition of Done](#48-definition-of-done)
- [49. V1 End-to-End Definition of Done](#49-v1-end-to-end-definition-of-done)
- [50. Current Development Status](#50-current-development-status)
- [51. Guiding Principle](#51-guiding-principle)

---

## 1. Project Overview

KnowBase AI is a multi-tenant B2B SaaS application that allows organizations to upload internal knowledge documents and interact with them through an AI-powered question-answering system.

### Example

An organization uploads:

```text
Employee Handbook.pdf
```

The system processes the document:

```text
PDF
 ↓
Text extraction
 ↓
Page-aware text
 ↓
Chunking
 ↓
Embedding generation
 ↓
PostgreSQL + pgvector
```

An employee asks:

```text
How many paid leaves do employees get?
```

The system:

```text
Question
 ↓
Question embedding
 ↓
Vector similarity search
 ↓
Relevant document chunks
 ↓
LLM
 ↓
Answer + citation
```

Expected response:

```text
Employees are entitled to 24 paid leaves per year.

Source:
Employee Handbook — Page 14
```

---

## 2. V1 Objective

The primary objective of V1 is to build and prove a reliable **document → RAG → answer** pipeline.

V1 must successfully support:

1. User authentication
2. Organizations / tenants
3. Organization membership
4. PDF upload
5. PDF text extraction
6. Page-aware text preservation
7. Text chunking
8. Embedding generation
9. Vector storage
10. Semantic similarity search
11. Question answering using retrieved context
12. Source/page citations
13. Conversations
14. Messages
15. Basic document processing status

The system should be simple, understandable, and extensible.

---

## 3. V1 Scope

### Included

#### Authentication

- User registration
- Login
- Logout
- Session/authentication handling
- User identity

#### Organizations

- Organization creation
- Organization membership
- Basic organization roles
- Tenant isolation

#### Documents

- PDF upload
- Document metadata
- Document versions
- Document processing status
- Text extraction
- Chunk storage
- Embeddings

#### RAG

- Question embedding
- Vector similarity search
- Top-K retrieval
- Context construction
- LLM generation
- Citations

#### Conversations

- Create conversation
- Send message
- Store user messages
- Store assistant messages
- Store citations

---

## 4. Explicitly NOT in V1

Do NOT implement these unless specifically requested:

- OCR
- Vision models
- Image understanding
- Complex table extraction
- Multimodal RAG
- Agents
- Multi-agent systems
- LangGraph workflows
- Complex LangChain abstractions
- Redis
- Kafka
- Kubernetes
- Microservice orchestration
- Google Drive integration
- OneDrive integration
- SharePoint integration
- Slack integration
- Notion integration
- WhatsApp integration
- Billing
- Payments
- Advanced analytics
- Advanced permissions
- Enterprise SSO
- Advanced reranking
- Fine-tuning
- Model training

These may be added in future versions.

**Do not expand V1 scope without an explicit requirement.**

---

## 5. Architecture

V1 uses a hybrid TypeScript + Python architecture.

```text
                         ┌───────────────┐
                         │    Next.js    │
                         │   Frontend    │
                         └───────┬───────┘
                                 │
                                 ▼
                         ┌───────────────┐
                         │    NestJS     │
                         │ Application   │
                         │     API       │
                         └───────┬───────┘
                                 │
                         ┌───────┴───────┐
                         │               │
                         ▼               ▼
                  PostgreSQL        Python AI
                  + pgvector         Service
                                         │
                         ┌───────────────┼───────────────┐
                         │               │               │
                         ▼               ▼               ▼
                     Extraction      Chunking       Embeddings
                                         │
                                         ▼
                                  RAG / Retrieval
                                         │
                                         ▼
                                       LLM
```

---

## 6. Technology Stack

### Frontend

```text
Next.js
TypeScript
Tailwind CSS
```

The frontend is responsible for:

- Authentication UI
- Organization UI
- Document upload
- Document list
- Processing status
- Chat interface
- Conversation history
- Citation display

### Backend

```text
NestJS
TypeScript
Prisma
```

NestJS is the primary application backend.

It is responsible for:

- Authentication integration
- Users
- Organizations
- Memberships
- Documents
- Conversations
- Messages
- Authorization
- API endpoints
- Application/business logic
- Database access
- Calling/communicating with the Python AI service

NestJS should NOT contain the main AI/document-processing implementation.

---

## 7. Python AI Service

Python is responsible for AI and document-processing workloads.

V1 responsibilities:

```text
PDF extraction
       ↓
Text cleaning
       ↓
Chunking
       ↓
Embedding generation
       ↓
Vector retrieval
       ↓
RAG context preparation
       ↓
LLM interaction
```

Python should be treated as an independent internal AI service.

---

## 8. Database

Primary database:

```text
PostgreSQL
```

Vector extension:

```text
pgvector
```

The database stores both:

1. Application data
2. AI/RAG data

There is no separate vector database in V1.

---

## 9. Database Architecture

Core relationship:

```text
User
 │
 └── Organization Membership
             │
             ▼
       Organization
             │
             ├── Documents
             │      │
             │      ▼
             │   Document Versions
             │      │
             │      ▼
             │   Document Chunks
             │      │
             │      └── Embedding
             │
             └── Conversations
                    │
                    ▼
                 Messages
                    │
                    ▼
              Message Citations
                    │
                    ▼
              Document Chunks
```

---

## 10. Core Tables

The primary V1 tables are:

```text
users
organizations
organization_members

documents
document_versions
document_chunks

conversations
messages
message_citations
```

The database schema has been designed to support future expansion, but V1 should focus on these core entities.

---

## 11. Users

A user represents a person using KnowBase AI.

Important fields:

```text
id
email
name
status
created_at
updated_at
```

A user is NOT directly owned by an organization.

A user can belong to multiple organizations.

Relationship:

```text
User
 ↓
OrganizationMember
 ↓
Organization
```

This allows future users to participate in multiple organizations.

---

## 12. Organizations

An organization represents a tenant/customer.

Important fields:

```text
id
name
slug
owner_id
status
created_at
updated_at
deleted_at
```

Every business resource must ultimately belong to an organization.

Examples:

```text
Document → Organization
Conversation → Organization
AI Usage → Organization
```

---

## 13. Organization Membership

Users belong to organizations through:

```text
organization_members
```

Important fields:

```text
id
organization_id
user_id
role
status
created_at
updated_at
```

Example roles:

```text
OWNER
ADMIN
MEMBER
VIEWER
```

Important constraint:

```text
UNIQUE(organization_id, user_id)
```

---

## 14. Multi-Tenant Security

This is one of the most important rules in the project.

Every organization-owned resource must be isolated by organization.

Example:

```text
Organization A
 ├── Documents
 ├── Conversations
 └── Members

Organization B
 ├── Documents
 ├── Conversations
 └── Members
```

Organization A must NEVER be able to access Organization B's data.

### Critical rule

Never blindly trust:

```text
organizationId
```

sent by the frontend.

Instead:

```text
Authenticated User
        ↓
Organization Membership
        ↓
Authorized Organization
        ↓
Resource
```

The backend must verify authorization.

---

## 15. Documents

A document represents a logical uploaded document.

Important fields:

```text
id
organization_id
name
original_filename
mime_type
file_size
storage_path
checksum
status
processing_status
current_version_id
created_by
created_at
updated_at
deleted_at
```

Example:

```text
Employee Handbook.pdf
```

---

## 16. Document Versions

Documents should support versioning.

Example:

```text
Employee Handbook
       │
       ├── Version 1
       ├── Version 2
       └── Version 3 ← current
```

Important fields:

```text
id
document_id
version_number
storage_path
checksum
status
created_at
```

Why versioning matters:

A user may ask a question today using Version 3.

An old conversation may have been answered using Version 1.

The citation must still point to the correct historical content.

---

## 17. Document Chunks

A document version is divided into chunks.

Example:

```text
Document
   ↓
Version 1
   ↓
Chunk 0
Chunk 1
Chunk 2
Chunk 3
...
```

Important fields:

```text
id
document_version_id
chunk_index
content
page_number
token_count
embedding
embedding_model
embedding_version
metadata
created_at
```

---

## 18. Chunking Strategy — V1

Keep chunking simple.

V1 should use page-aware, recursive/token-aware chunking.

Initial target:

```text
Chunk size:
~500–800 tokens

Overlap:
~50–100 tokens
```

These are starting values, not permanent constants.

The chunking implementation should be configurable.

Do NOT build sophisticated semantic chunking in V1.

---

## 19. Page Preservation

Page information is important.

The PDF loader should preserve:

```text
page_number
text
```

Example:

```python
[
    {
        "page_number": 1,
        "text": "Introduction..."
    },
    {
        "page_number": 2,
        "text": "Leave policy..."
    }
]
```

Chunks should retain the source page whenever possible.

This enables:

```text
Answer
 ↓
Citation
 ↓
Document
 ↓
Page
```

---

## 20. Embedding Model

V1 embedding model:

```text
gemini-embedding-001
```

Configured output dimensionality:

```text
1536
```

Stored in PostgreSQL as:

```sql
vector(1536)
```

Embedding generation happens in Python via the Gemini API (OpenAI-compatible client).

Conceptually:

```text
Text
 ↓
Embedding Model
 ↓
Vector
```

Example:

```python
embedding = create_embedding(
    "Employees receive 24 paid leaves every year."
)
```

The returned embedding length determines the PostgreSQL vector dimension.

### Important

The database dimension must match the actual embedding output being used.

For `gemini-embedding-001`, request `output_dimensionality=1536` and verify programmatically:

```python
print(len(embedding))  # must be 1536
```

Then configure the pgvector column as `vector(1536)`.

---

## 21. Embedding Rules

All vectors stored in the same embedding column must have compatible dimensions.

Do not mix:

```text
Model A embeddings
+
Model B embeddings
```

unless the schema explicitly supports separate embedding configurations.

Store:

```text
embedding_model
embedding_version
```

with chunks so future re-embedding/model migration is possible.

---

## 22. RAG Pipeline

The core RAG pipeline is:

```text
                 DOCUMENT INGESTION

PDF
 ↓
Extract text
 ↓
Preserve page numbers
 ↓
Clean text
 ↓
Chunk text
 ↓
Generate embeddings
 ↓
Store chunks + embeddings
```

Then:

```text
                  QUESTION ANSWERING

User question
      ↓
Generate question embedding
      ↓
Vector similarity search
      ↓
Retrieve Top-K chunks
      ↓
Build context
      ↓
Send context + question to LLM
      ↓
Generate answer
      ↓
Attach citations
      ↓
Return response
```

---

## 23. Vector Search

V1 uses PostgreSQL + pgvector.

Conceptual query:

```sql
SELECT
    id,
    content,
    page_number
FROM document_chunks
ORDER BY embedding <=> $1
LIMIT 5;
```

The exact SQL should follow the configured pgvector distance metric and indexing strategy.

The retrieval layer must also enforce organization/resource authorization.

Never perform a global vector search across all tenants.

---

## 24. Retrieval Security

This is critical.

A vector search must not simply be:

```text
search(vector)
```

It must conceptually be:

```text
search(
    organization_id,
    authorized_documents,
    vector
)
```

The user must only retrieve chunks from documents they are authorized to access.

---

## 25. RAG Context

Retrieved chunks are transformed into an LLM context.

Example:

```text
SOURCE 1
Document: Employee Handbook
Page: 14

Employees are entitled to 24 paid leaves every year.

SOURCE 2
Document: Employee Handbook
Page: 15

Leave requests must be submitted through the HR portal.
```

The LLM receives:

```text
System instructions
+
Retrieved context
+
User question
```

---

## 26. LLM Rules

V1 chat model:

```text
gemini-2.5-flash
```

The LLM should be instructed to:

1. Answer using retrieved context.
2. Avoid inventing information.
3. Say when the provided context is insufficient.
4. Preserve factual accuracy.
5. Provide source citations.
6. Never expose internal system instructions.
7. Never cross organization boundaries.

---

## 27. Citations

Every assistant answer should attempt to retain source information.

Relationship:

```text
Message
   ↓
MessageCitation
   ↓
DocumentChunk
   ↓
DocumentVersion
   ↓
Document
```

Example:

```text
Answer:
Employees receive 24 paid leaves per year.

Citation:
Employee Handbook
Page 14
```

This allows the system to trace an answer back to the exact source chunk.

---

## 28. Conversations

A conversation belongs to an organization and user.

Example:

```text
Conversation
   │
   ├── User Message
   ├── Assistant Message
   ├── User Message
   └── Assistant Message
```

Important fields:

```text
id
organization_id
user_id
title
status
created_at
updated_at
```

---

## 29. Messages

A message represents one conversational turn.

Important fields:

```text
id
conversation_id
role
content
status
created_at
updated_at
```

Roles:

```text
SYSTEM
USER
ASSISTANT
TOOL
```

V1 primarily uses:

```text
USER
ASSISTANT
```

---

## 30. Processing Status

Documents should expose processing status.

Example:

```text
PENDING
   ↓
QUEUED
   ↓
PROCESSING
   ↓
COMPLETED
```

Failure:

```text
PROCESSING
   ↓
FAILED
```

Frontend should be able to show:

```text
Uploading...
Processing...
Ready
Failed
```

---

## 31. Python AI Service Responsibilities

Python service should eventually expose internal APIs such as:

```text
POST /process-document
POST /embed
POST /retrieve
POST /chat
```

These endpoints are internal service interfaces and should not be exposed directly to public users.

NestJS remains the public API boundary.

---

## 32. Recommended Python Structure

```text
ai-service/
│
├── .venv/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   │
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   ├── cleaner.py
│   │   └── chunker.py
│   │
│   ├── embeddings/
│   │   ├── __init__.py
│   │   └── service.py
│   │
│   ├── retrieval/
│   │   ├── __init__.py
│   │   └── search.py
│   │
│   └── rag/
│       ├── __init__.py
│       └── pipeline.py
│
├── requirements.txt
├── .env
└── .gitignore
```

---

## 33. Python Environment

`.venv` is only the Python environment.

Never place application code inside:

```text
.venv/
```

Correct:

```text
ai-service/
├── .venv/
└── app/
```

Incorrect:

```text
ai-service/
└── .venv/
    └── app/
```

---

## 34. V1 Development Order

Build in this exact order unless there is a clear technical reason to change it.

### Phase 1 — PDF ingestion

```text
PDF
 ↓
Text extraction
 ↓
Page-aware output
```

First prove that a real PDF can be processed.

### Phase 2 — Chunking

```text
Page-aware text
 ↓
Cleaning
 ↓
Chunking
```

Inspect the generated chunks manually.

### Phase 3 — Embeddings

```text
Chunk
 ↓
Embedding model
 ↓
Vector
```

Verify:

```python
len(embedding)
```

before finalizing the vector dimension.

### Phase 4 — Vector storage

```text
Chunk
+
Embedding
 ↓
PostgreSQL + pgvector
```

### Phase 5 — Retrieval

Implement:

```text
Question
 ↓
Question embedding
 ↓
Similarity search
 ↓
Top-K chunks
```

Before involving an LLM, verify that the correct chunks are actually being retrieved.

### Phase 6 — RAG

```text
Question
 ↓
Retrieval
 ↓
Context
 ↓
LLM
 ↓
Answer
```

### Phase 7 — Citations

Connect:

```text
Answer
 ↓
Retrieved chunk
 ↓
Page
 ↓
Document
```

### Phase 8 — NestJS integration

After the Python pipeline works independently:

```text
NestJS
 ↓
Python AI service
```

NestJS becomes the application orchestrator.

### Phase 9 — Frontend integration

Finally:

```text
Next.js
 ↓
NestJS
 ↓
Python
 ↓
PostgreSQL
 ↓
LLM
```

---

## 35. First Milestone

The first major milestone is NOT a polished UI.

The first milestone is:

```text
Upload PDF
      ↓
Extract text
      ↓
Create chunks
      ↓
Create embeddings
      ↓
Store in pgvector
      ↓
Ask question
      ↓
Retrieve correct chunks
      ↓
Generate answer
      ↓
Show page citation
```

Example acceptance test:

#### Input PDF

```text
Employee Handbook.pdf
```

#### Question

```text
How many paid leaves do employees receive?
```

#### Expected behavior

The system retrieves the relevant chunk and produces an answer grounded in that document.

---

## 36. Testing Strategy

V1 should contain tests for:

### PDF extraction

```text
PDF → expected page count
PDF → expected text
```

### Chunking

```text
Input text
→ chunks
→ valid size
→ correct ordering
→ page metadata preserved
```

### Embeddings

```text
Input text
→ embedding
→ expected dimension
```

### Retrieval

Given a known document:

```text
Question
→ expected relevant chunk appears in Top-K
```

### Multi-tenancy

Test:

```text
User A → Organization A → Document A
```

and verify:

```text
User B → Organization B
```

cannot retrieve Document A.

### Citations

Verify:

```text
Assistant message
→ citation
→ chunk
→ document version
→ document
→ page
```

---

## 37. Error Handling

Every pipeline stage should have explicit failure handling.

Examples:

```text
Invalid PDF
PDF extraction failure
Empty document
Chunking failure
Embedding API failure
Database failure
LLM failure
Invalid vector dimension
Unauthorized document
```

Do not silently swallow errors.

Return meaningful errors and log technical details internally.

---

## 38. Logging

Logs should make document processing traceable.

Example:

```text
[INGESTION] Document received
[EXTRACTION] Extracted 24 pages
[CHUNKING] Created 182 chunks
[EMBEDDING] Generated 182 embeddings
[DATABASE] Stored 182 chunks
[PROCESSING] Document completed
```

For a failed document:

```text
[PROCESSING] FAILED
document_id=...
stage=embedding
error=...
```

Never log:

- API secrets
- passwords
- authentication tokens
- sensitive user information unnecessarily

---

## 39. Configuration

Use environment variables for secrets and environment-specific configuration.

Example:

```env
DATABASE_URL=
GEMINI_API_KEY=
AI_SERVICE_URL=
```

Never hardcode:

```text
API keys
passwords
database credentials
tokens
```

Never commit `.env` to Git.

---

## 40. Git Rules

`.gitignore` should include:

```gitignore
.venv/
__pycache__/
.env
node_modules/
dist/
.next/
```

Do not commit:

```text
.env
API keys
database passwords
large uploaded PDFs
generated embeddings
temporary files
```

---

## 41. Coding Principles

All code should follow these principles:

### Keep responsibilities separate

NestJS:

```text
Application/business logic
```

Python:

```text
AI/document processing
```

PostgreSQL:

```text
Persistent data
```

Next.js:

```text
UI/client experience
```

### Prefer simple implementations

For V1:

```text
Simple > clever
Readable > abstract
Working > over-engineered
```

Do not introduce an abstraction/library unless it solves an actual problem.

---

## 42. LangChain Policy

LangChain is NOT required for the initial implementation.

First understand and implement:

```text
PDF extraction
Chunking
Embeddings
Vector search
RAG
```

directly.

Only introduce LangChain when an abstraction genuinely reduces complexity.

Do not replace understandable code with LangChain simply because the project is an AI project.

---

## 43. LangGraph Policy

LangGraph is NOT part of V1.

It becomes useful later for workflows such as:

```text
Question
 ↓
Classify
 ↓
Retrieve
 ↓
Evaluate retrieval
 ↓
Retry retrieval
 ↓
Call tools
 ↓
Human approval
 ↓
Final response
```

V1 does not require this complexity.

---

## 44. Future Architecture

Future versions may evolve toward:

```text
Next.js
   ↓
NestJS API
   ↓
Queue
   ↓
Python Workers
   ├── PDF
   ├── DOCX
   ├── CSV
   ├── PPTX
   ├── OCR
   ├── Vision
   ├── Chunking
   ├── Embeddings
   ├── Reranking
   └── RAG
```

Potential future capabilities:

```text
Google Drive
OneDrive
SharePoint
Slack
Notion
Website ingestion
Multimodal documents
Advanced permissions
Enterprise SSO
Billing
Usage limits
Agents
Tool calling
Workflow automation
```

These are future concerns.

---

## 45. Important Architectural Decisions

### Decision 1

Use:

```text
PostgreSQL + pgvector
```

instead of a separate vector database for V1.

### Decision 2

Use:

```text
NestJS + TypeScript
```

for the main application backend.

### Decision 3

Use:

```text
Python
```

for document processing, chunking, embeddings, and RAG/AI workloads.

### Decision 4

Use:

```text
gemini-embedding-001
```

with `1536` output dimensions as the initial embedding model.

Use:

```text
gemini-2.5-flash
```

as the initial chat model for RAG answers.

### Decision 5

Keep PDF processing simple in V1.

Do not implement OCR/vision/multimodal processing yet.

### Decision 6

Do not introduce LangChain/LangGraph until their abstractions are actually needed.

---

## 46. AI Agent Instructions

This repository may be worked on using coding agents such as Cursor.

The following rules should be treated as project-level instructions.

### Before modifying code

1. Inspect the existing repository.
2. Understand the current architecture.
3. Inspect the existing database schema.
4. Reuse existing implementations where appropriate.
5. Do not rewrite working systems unnecessarily.

### Before creating a new dependency

Ask:

```text
Is this dependency actually necessary?
```

Prefer existing project dependencies when possible.

### Before changing the database

Check:

```text
Existing schema
Existing migrations
Existing relationships
Existing application code
```

Do not casually rename or remove existing fields.

### Before creating a new service

Confirm that the functionality cannot reasonably belong to an existing service.

### Preserve architectural boundaries

Do not move AI processing into NestJS just because it is convenient.

Do not move application/business logic into Python.

---

## 47. AI Coding Agent Workflow

When asked to implement a feature:

```text
1. Understand the requirement
        ↓
2. Inspect repository
        ↓
3. Identify affected modules
        ↓
4. Check database relationships
        ↓
5. Design minimal change
        ↓
6. Implement
        ↓
7. Run tests/type checks
        ↓
8. Fix errors
        ↓
9. Explain changes
```

Do not immediately start creating files without inspecting the existing codebase.

---

## 48. Definition of Done

A feature is not complete merely because the code compiles.

For V1, consider a feature complete when:

```text
Code implemented
+
Database changes migrated
+
Validation implemented
+
Authorization implemented
+
Errors handled
+
Tests added where appropriate
+
Existing functionality still works
```

For RAG features:

```text
Correct retrieval
+
Grounded answer
+
Citation
```

are required.

---

## 49. V1 End-to-End Definition of Done

The project reaches V1 when this complete flow works:

```text
User
 ↓
Creates organization
 ↓
Uploads PDF
 ↓
NestJS receives upload
 ↓
Python processes PDF
 ↓
Text extracted
 ↓
Text chunked
 ↓
Embeddings generated
 ↓
Chunks + embeddings stored
 ↓
User opens chat
 ↓
User asks question
 ↓
Question embedded
 ↓
Relevant chunks retrieved
 ↓
LLM receives context
 ↓
LLM generates answer
 ↓
Citation attached
 ↓
User sees answer + source/page
```

---

## 50. Current Development Status

Current known state:

```text
[READY] NestJS backend
[READY] PostgreSQL database
[READY] pgvector/database foundation
[IN PROGRESS] Python AI service
[TODO] PDF extraction
[TODO] Chunking
[TODO] Embeddings
[TODO] Vector storage integration
[TODO] Retrieval
[TODO] RAG
[TODO] Citations
[TODO] NestJS ↔ Python integration
[TODO] Frontend integration
```

The **next implementation target is the Python AI service**.

Start with:

```text
ai-service/
├── .venv/
├── app/
│   ├── main.py
│   └── ingestion/
│       ├── loader.py
│       └── chunker.py
├── requirements.txt
├── .env
└── .gitignore
```

First implementation:

```text
PDF → page-aware extracted text
```

Then:

```text
page-aware text → chunks
```

Then:

```text
chunks → embeddings
```

Then:

```text
embeddings → pgvector
```

Then:

```text
question → retrieval → LLM → citations
```

---

## 51. Guiding Principle

The goal of V1 is not to demonstrate how many AI technologies can be added.

The goal is to build a **working, understandable, testable RAG system**.

The core system should be understandable by a developer looking at the repository:

```text
Document
   ↓
Extraction
   ↓
Chunking
   ↓
Embedding
   ↓
Vector Storage
   ↓
Retrieval
   ↓
Context
   ↓
LLM
   ↓
Answer
   ↓
Citation
```

Everything else comes later.
