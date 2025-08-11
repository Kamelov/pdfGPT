import os
import re
import shutil
import urllib.request
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import List, Optional
import fitz
import numpy as np
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import openai
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="PDF Chat API", description="API pour discuter avec des documents PDF")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles globaux
sentence_model = None
document_chunks = []
chunk_embeddings = None

class ChatRequest(BaseModel):
    question: str
    openai_key: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

def get_sentence_model():
    global sentence_model
    if sentence_model is None:
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
    return sentence_model

def download_pdf(url, output_path):
    urllib.request.urlretrieve(url, output_path)

def preprocess(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

def pdf_to_text(path, start_page=1, end_page=None):
    doc = fitz.open(path)
    total_pages = doc.page_count

    if end_page is None:
        end_page = total_pages

    text_list = []

    for i in range(start_page - 1, end_page):
        text = doc.load_page(i).get_text("text")
        text = preprocess(text)
        text_list.append(text)

    doc.close()
    return text_list

def text_to_chunks(texts, word_length=150, start_page=1):
    text_toks = [t.split(' ') for t in texts]
    chunks = []

    for idx, words in enumerate(text_toks):
        for i in range(0, len(words), word_length):
            chunk = words[i : i + word_length]
            if (
                (i + word_length) > len(words)
                and (len(chunk) < word_length)
                and (len(text_toks) != (idx + 1))
            ):
                text_toks[idx + 1] = chunk + text_toks[idx + 1]
                continue
            chunk = ' '.join(chunk).strip()
            chunk_with_page = f'[Page {idx+start_page}] {chunk}'
            chunks.append(chunk_with_page)
    return chunks

def find_relevant_chunks(question: str, top_k: int = 5) -> List[str]:
    global document_chunks, chunk_embeddings
    
    if not document_chunks or chunk_embeddings is None:
        return []
    
    model = get_sentence_model()
    question_embedding = model.encode([question])
    
    # Calculer la similarité cosinus
    similarities = cosine_similarity(question_embedding, chunk_embeddings)[0]
    
    # Obtenir les indices des chunks les plus similaires
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    return [document_chunks[i] for i in top_indices if similarities[i] > 0.1]

def generate_answer_with_openai(question: str, relevant_chunks: List[str], api_key: str) -> str:
    if not relevant_chunks:
        return "Je n'ai pas trouvé d'informations pertinentes dans le document pour répondre à votre question."
    
    context = "\n\n".join(relevant_chunks)
    
    prompt = f"""Basé sur le contexte suivant extrait d'un document PDF, répondez à la question de manière précise et concise. 
Citez les numéros de page entre crochets [] quand c'est pertinent.

Contexte:
{context}

Question: {question}

Réponse:"""

    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erreur avec l'API OpenAI: {str(e)}"

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    global document_chunks, chunk_embeddings
    
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Le fichier doit être un PDF")
    
    # Sauvegarder le fichier temporairement
    suffix = Path(file.filename).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = Path(tmp.name)
    
    try:
        # Extraire le texte du PDF
        texts = pdf_to_text(str(tmp_path))
        document_chunks = text_to_chunks(texts)
        
        # Créer les embeddings
        model = get_sentence_model()
        chunk_embeddings = model.encode(document_chunks)
        
        return {
            "message": f"PDF '{file.filename}' traité avec succès. {len(document_chunks)} chunks créés.",
            "chunks_count": len(document_chunks)
        }
    
    finally:
        # Nettoyer le fichier temporaire
        tmp_path.unlink()

@app.post("/upload-pdf-url")
async def upload_pdf_url(url: str):
    global document_chunks, chunk_embeddings
    
    try:
        # Télécharger le PDF
        download_pdf(url, 'temp_pdf.pdf')
        
        # Extraire le texte du PDF
        texts = pdf_to_text('temp_pdf.pdf')
        document_chunks = text_to_chunks(texts)
        
        # Créer les embeddings
        model = get_sentence_model()
        chunk_embeddings = model.encode(document_chunks)
        
        return {
            "message": f"PDF téléchargé et traité avec succès. {len(document_chunks)} chunks créés.",
            "chunks_count": len(document_chunks)
        }
    
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists('temp_pdf.pdf'):
            os.remove('temp_pdf.pdf')

@app.post("/chat", response_model=ChatResponse)
async def chat_with_pdf(request: ChatRequest):
    if not document_chunks:
        raise HTTPException(status_code=400, detail="Aucun PDF n'a été téléchargé. Veuillez d'abord télécharger un PDF.")
    
    # Obtenir la clé API OpenAI
    api_key = request.openai_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="Clé API OpenAI requise")
    
    # Trouver les chunks pertinents
    relevant_chunks = find_relevant_chunks(request.question)
    
    # Générer la réponse
    answer = generate_answer_with_openai(request.question, relevant_chunks, api_key)
    
    # Extraire les sources (numéros de page)
    sources = []
    for chunk in relevant_chunks:
        if '[Page' in chunk:
            page_info = chunk.split(']')[0] + ']'
            if page_info not in sources:
                sources.append(page_info)
    
    return ChatResponse(answer=answer, sources=sources)

@app.get("/status")
async def get_status():
    return {
        "chunks_loaded": len(document_chunks),
        "embeddings_created": chunk_embeddings is not None,
        "model_loaded": sentence_model is not None
    }

@app.get("/")
async def root():
    return {"message": "API PDF Chat - Téléchargez un PDF et posez vos questions!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
