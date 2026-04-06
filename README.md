# 🤖 AI Debugging Assistant

An AI-powered debugging assistant that takes **code + error** as input and returns:
- **Explanation** — why the error occurs
- **Fix** — corrected version of the code
- **Optimization** — best-practice, optimized version

Powered by **RAG** (FAISS + sentence-transformers) and **Groq's Llama 3.3 70B** model.

## 🏗 Tech Stack

| Layer         | Technology                          |
|---------------|--------------------------------------|
| Backend       | FastAPI (Python)                    |
| Frontend      | React + Vite                        |
| Vector DB     | FAISS                               |
| Embeddings    | all-MiniLM-L6-v2 (sentence-transformers) |
| LLM           | Groq — llama-3.3-70b-versatile      |
| RAG Framework | LangChain                           |

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
│   │   │   ├── vector_store.py  # FAISS management
│   │   │   └── llm_service.py   # Groq LLM wrapper
│   │   ├── models/schemas.py    # Pydantic models
│   │   └── knowledge/seed_data.py
│   ├── data/knowledge_base/     # Debugging knowledge docs
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/          # React components
│   │   └── services/api.js      # API layer
│   └── package.json
└── README.md
```

## 🚀 Getting Started

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

# Configure environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

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

### 3. Open the App

Visit **http://localhost:5173** — paste your code and error, then click **Debug My Code**!

## 📡 API Endpoints

| Method | Endpoint       | Description                        |
|--------|----------------|------------------------------------|
| GET    | `/api/health`  | Health check                       |
| POST   | `/api/debug`   | Submit code + error for debugging  |

### POST `/api/debug` — Request Body

```json
{
  "code": "def add(a, b):\n    return a + b\n\nprint(add(1, '2'))",
  "error_message": "TypeError: unsupported operand type(s) for +: 'int' and 'str'",
  "language": "python"
}
```

### Response

```json
{
  "explanation": "The error occurs because...",
  "fix": "def add(a, b):\n    return int(a) + int(b)...",
  "optimized_code": "def add(a: int, b: int) -> int:...",
  "relevant_context": ["..."]
}
```

## 📝 License

MIT
