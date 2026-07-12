import asyncio
import json
import sqlite3
from typing import AsyncGenerator
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel

app = FastAPI(title="ChatGPT/Gemini Clone API")

# Habilitar CORS para peticiones local/frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------
# 1. BASE DE DATOS DE HISTORIAL (SQLite)
# ------------------------------------------------------------------
DB_NAME = "chat_memory.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            role TEXT,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

init_db()

def save_message(session_id: str, role: str, content: str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
        (session_id, role, content)
    )
    conn.commit()
    conn.close()

def get_history(session_id: str, limit: int = 10):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
        (session_id, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": r[0], "content": r[1]} for r in reversed(rows)]

# ------------------------------------------------------------------
# 2. MÓDULO RAG (Ejemplo conceptual con ChromaDB)
# ------------------------------------------------------------------
def get_rag_context(query: str) -> str:
    if "python" in query.lower():
        return " [Contexto RAG: El proyecto usa FastAPI y SQLite]."
    return ""

# ------------------------------------------------------------------
# 3. GENERADOR DE STREAMING (SSE)
# ------------------------------------------------------------------
class ChatRequest(BaseModel):
    session_id: str
    prompt: str

async def fake_llm_stream_generator(prompt: str, session_id: str) -> AsyncGenerator[str, None]:
    # 1. Recuperar contexto RAG e historial
    rag_context = get_rag_context(prompt)
    history = get_history(session_id)
    
    # 2. Guardar mensaje del usuario
    save_message(session_id, "user", prompt)

    # 3. Simulación de respuesta en Streaming
    full_response = (
        f"He recibido tu mensaje: **\"{prompt}\"**.{rag_context}\n\n"
        "Aquí tienes un ejemplo de código generado:\n\n"
        "
http://googleusercontent.com/immersive_entry_chip/0
