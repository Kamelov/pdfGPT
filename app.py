import streamlit as st
import requests
import json
import os
from datetime import datetime
from typing import List, Dict

# Configuration de la page
st.set_page_config(
    page_title="PDF Chat Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# URL de l'API
API_BASE_URL = "http://localhost:8000"

# CSS personnalisé pour un design moderne
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1e3a8a;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .user-message {
        background-color: #e0f2fe;
        border-left: 4px solid #0288d1;
    }
    .assistant-message {
        background-color: #f3e5f5;
        border-left: 4px solid #7b1fa2;
    }
    .source-tag {
        background-color: #fff3e0;
        color: #e65100;
        padding: 0.2rem 0.5rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialise les variables de session"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'pdf_uploaded' not in st.session_state:
        st.session_state.pdf_uploaded = False
    if 'openai_key' not in st.session_state:
        st.session_state.openai_key = ""

def upload_pdf_file(uploaded_file, openai_key):
    """Télécharge un fichier PDF vers l'API"""
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
        response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
        
        if response.status_code == 200:
            st.session_state.pdf_uploaded = True
            st.session_state.openai_key = openai_key
            return True, response.json()["message"]
        else:
            return False, f"Erreur: {response.text}"
    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def upload_pdf_url(url, openai_key):
    """Télécharge un PDF depuis une URL"""
    try:
        response = requests.post(f"{API_BASE_URL}/upload-pdf-url", params={"url": url})
        
        if response.status_code == 200:
            st.session_state.pdf_uploaded = True
            st.session_state.openai_key = openai_key
            return True, response.json()["message"]
        else:
            return False, f"Erreur: {response.text}"
    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def chat_with_pdf(question: str, openai_key: str):
    """Envoie une question à l'API et récupère la réponse"""
    try:
        data = {
            "question": question,
            "openai_key": openai_key
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=data)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erreur: {response.text}"
    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def display_chat_message(message_type: str, content: str, sources: List[str] = None):
    """Affiche un message de chat stylisé"""
    if message_type == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>🙋‍♂️ Vous:</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)
    else:
        sources_html = ""
        if sources:
            sources_html = "<br><strong>Sources:</strong> " + " ".join([f'<span class="source-tag">{source}</span>' for source in sources])
        
        st.markdown(f"""
        <div class="chat-message assistant-message">
            <strong>🤖 Assistant:</strong><br>
            {content}
            {sources_html}
        </div>
        """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    # En-tête principal
    st.markdown('<h1 class="main-header">📄 PDF Chat Assistant</h1>', unsafe_allow_html=True)
    st.markdown("**Téléchargez un PDF et discutez avec son contenu grâce à l'IA**")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("🔧 Configuration")
        
        # Clé API OpenAI
        openai_key = st.text_input(
            "Clé API OpenAI",
            type="password",
            value=st.session_state.openai_key,
            help="Obtenez votre clé sur https://platform.openai.com/account/api-keys"
        )
        
        if not openai_key:
            openai_key = os.getenv("OPENAI_API_KEY", "")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Section de téléchargement
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.header("📤 Télécharger un PDF")
        
        upload_method = st.radio("Méthode de téléchargement:", ["Fichier local", "URL"])
        
        if upload_method == "Fichier local":
            uploaded_file = st.file_uploader(
                "Choisissez un fichier PDF",
                type="pdf",
                help="Sélectionnez un fichier PDF depuis votre ordinateur"
            )
            
            if uploaded_file is not None and st.button("📁 Traiter le PDF"):
                if not openai_key:
                    st.error("Veuillez entrer votre clé API OpenAI")
                else:
                    with st.spinner("Traitement du PDF en cours..."):
                        success, message = upload_pdf_file(uploaded_file, openai_key)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        else:  # URL
            pdf_url = st.text_input(
                "URL du PDF",
                placeholder="https://exemple.com/document.pdf",
                help="Entrez l'URL directe vers un fichier PDF"
            )
            
            if pdf_url and st.button("🌐 Télécharger depuis l'URL"):
                if not openai_key:
                    st.error("Veuillez entrer votre clé API OpenAI")
                else:
                    with st.spinner("Téléchargement et traitement du PDF..."):
                        success, message = upload_pdf_url(pdf_url, openai_key)
                        if success:
                            st.success(message)
                        else:
                            st.error(message)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Statut
        if st.button("🔄 Vérifier le statut"):
            try:
                response = requests.get(f"{API_BASE_URL}/status")
                if response.status_code == 200:
                    status = response.json()
                    st.info(f"Chunks chargés: {status['chunks_loaded']}")
                else:
                    st.error("Impossible de vérifier le statut")
            except:
                st.error("API non disponible")
        
        # Bouton pour vider l'historique
        if st.button("🗑️ Vider l'historique"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Interface de chat principale
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.header("💬 Chat avec votre PDF")
        
        # Vérification que le PDF est téléchargé
        if not st.session_state.pdf_uploaded:
            st.warning("⚠️ Veuillez d'abord télécharger un PDF dans la barre latérale.")
            st.info("📝 **Instructions:**\n1. Entrez votre clé API OpenAI\n2. Téléchargez un fichier PDF ou entrez une URL\n3. Commencez à poser des questions!")
        else:
            # Zone de chat
            chat_container = st.container()
            
            with chat_container:
                # Affichage de l'historique des messages
                for message in st.session_state.chat_history:
                    display_chat_message(
                        message["type"], 
                        message["content"], 
                        message.get("sources", [])
                    )
            
            # Zone de saisie de la question
            question = st.text_input(
                "Posez votre question:",
                placeholder="Ex: Quels sont les points principaux de ce document ?",
                key="question_input"
            )
            
            col_send, col_examples = st.columns([1, 2])
            
            with col_send:
                if st.button("📤 Envoyer", type="primary"):
                    if question.strip():
                        # Ajouter la question à l'historique
                        st.session_state.chat_history.append({
                            "type": "user",
                            "content": question,
                            "timestamp": datetime.now()
                        })
                        
                        # Obtenir la réponse de l'API
                        with st.spinner("Génération de la réponse..."):
                            success, response = chat_with_pdf(question, st.session_state.openai_key)
                            
                            if success:
                                st.session_state.chat_history.append({
                                    "type": "assistant",
                                    "content": response["answer"],
                                    "sources": response["sources"],
                                    "timestamp": datetime.now()
                                })
                            else:
                                st.session_state.chat_history.append({
                                    "type": "assistant",
                                    "content": f"Erreur: {response}",
                                    "sources": [],
                                    "timestamp": datetime.now()
                                })
                        
                        st.rerun()
                    else:
                        st.warning("Veuillez entrer une question.")
            
            with col_examples:
                st.markdown("**💡 Exemples de questions:**")
                example_questions = [
                    "Résumez ce document",
                    "Quels sont les points principaux ?",
                    "Y a-t-il des recommandations ?",
                    "Expliquez ce concept en détail"
                ]
                
                for i, example in enumerate(example_questions):
                    if st.button(f"💭 {example}", key=f"example_{i}"):
                        st.session_state.chat_history.append({
                            "type": "user",
                            "content": example,
                            "timestamp": datetime.now()
                        })
                        
                        with st.spinner("Génération de la réponse..."):
                            success, response = chat_with_pdf(example, st.session_state.openai_key)
                            
                            if success:
                                st.session_state.chat_history.append({
                                    "type": "assistant",
                                    "content": response["answer"],
                                    "sources": response["sources"],
                                    "timestamp": datetime.now()
                                })
                            else:
                                st.session_state.chat_history.append({
                                    "type": "assistant",
                                    "content": f"Erreur: {response}",
                                    "sources": [],
                                    "timestamp": datetime.now()
                                })
                        
                        st.rerun()
    
    with col2:
        st.header("ℹ️ Informations")
        st.markdown("""
        **Fonctionnalités:**
        - 📄 Support des fichiers PDF
        - 🌐 Téléchargement via URL
        - 💬 Chat interactif
        - 📚 Citations des sources
        - 🔍 Recherche sémantique
        
        **Conseils:**
        - Posez des questions spécifiques
        - Les réponses incluent les pages sources
        - Utilisez les exemples pour commencer
        """)

if __name__ == "__main__":
    main()
