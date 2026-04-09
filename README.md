# 🤖 Code Debugging Assistant

A professional, AI-powered debugging SaaS that takes **code + error** as input and returns high-fidelity explanations and fixes.

- **Explanation** — Detailed analysis of *why* the error occurs.
- **Fix** — A robust, corrected version of the code.
- **Optimization** — Best-practice, optimized version for production.

Powered by **RAG** (FAISS + FastEmbed) and **Groq's Llama 3.3 70B** model.

## 🏗 Tech Stack

| Layer         | Technology                          |
|---------------|--------------------------------------|
| Backend       | FastAPI (Python 3.12)               |
| Frontend      | React + Vite (Vanilla CSS)          |
| Vector DB     | FAISS                               |
| Embeddings    | BAAI/bge-small-en-v1.5 (**FastEmbed**) |
| LLM           | Groq — llama-3.3-70b-versatile      |
| Deployment    | Render (Backend) + Vercel (Frontend) |

## 🚀 Deployment

- **Backend (Render)**: [Live API](https://code-assistant-backend.onrender.com/api/health)
- **Frontend (Vercel)**: Live Production Build

## 📁 Project Structure

```
Code-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment settings
│   │   ├── routers/debug.py     # API endpoints
│   │   ├── services/
│   │   │   ├── rag_service.py   # RAG pipeline
│   │   │   ├── vector_store.py  # FAISS management (FastEmbed)
│   │   │   └── llm_service.py   # Groq LLM wrapper
│   │   ├── models/schemas.py    # Pydantic models
│   │   └── knowledge/seed_data.py
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/          # Professional UI components
│   │   └── services/api.js      # API layer (Environment-aware)
│   └── package.json
└── README.md
```

## 🚀 Local Development

### Prerequisites
- Python 3.10+
- Node.js 18+
- A [Groq API key](https://console.groq.com)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Visit **http://localhost:5173** to test locally!

## 📡 API Endpoints

| Method | Endpoint       | Description                        |
|--------|----------------|------------------------------------|
| GET    | `/api/health`  | Health check                       |
| POST   | `/api/debug`   | Submit code + error for debugging  |

## 📝 License

MIT
