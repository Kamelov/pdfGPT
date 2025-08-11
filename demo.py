#!/usr/bin/env python3
"""
Script de démonstration pour PDF Chat Assistant
Ce script teste l'API avec un PDF exemple et des questions prédéfinies
"""

import requests
import time
import json
import os
from urllib.request import urlretrieve

# Configuration
API_BASE_URL = "http://localhost:8000"
PDF_EXAMPLE_URL = "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf"
PDF_LOCAL_PATH = "example.pdf"

def wait_for_api(max_attempts=30, delay=2):
    """Attend que l'API soit disponible"""
    print("🔄 Attente de l'API...")
    
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{API_BASE_URL}/")
            if response.status_code == 200:
                print("✅ API prête !")
                return True
        except requests.exceptions.ConnectionError:
            pass
        
        print(f"   Tentative {attempt + 1}/{max_attempts}...")
        time.sleep(delay)
    
    print("❌ Impossible de se connecter à l'API")
    return False

def download_example_pdf():
    """Télécharge un PDF exemple pour la démonstration"""
    print("📥 Téléchargement du PDF exemple...")
    try:
        urlretrieve(PDF_EXAMPLE_URL, PDF_LOCAL_PATH)
        print(f"✅ PDF téléchargé: {PDF_LOCAL_PATH}")
        return True
    except Exception as e:
        print(f"❌ Erreur de téléchargement: {e}")
        return False

def upload_pdf_to_api():
    """Upload le PDF vers l'API"""
    print("📤 Upload du PDF vers l'API...")
    
    try:
        with open(PDF_LOCAL_PATH, 'rb') as f:
            files = {'file': (PDF_LOCAL_PATH, f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ PDF traité: {result['message']}")
            return True
        else:
            print(f"❌ Erreur upload: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur upload: {e}")
        return False

def test_chat(question, openai_key):
    """Teste une question avec l'API"""
    print(f"\n❓ Question: {question}")
    
    try:
        data = {
            "question": question,
            "openai_key": openai_key
        }
        response = requests.post(f"{API_BASE_URL}/chat", json=data)
        
        if response.status_code == 200:
            result = response.json()
            print(f"🤖 Réponse: {result['answer']}")
            if result['sources']:
                print(f"📚 Sources: {', '.join(result['sources'])}")
            return True
        else:
            print(f"❌ Erreur chat: {response.text}")
            return False
    
    except Exception as e:
        print(f"❌ Erreur chat: {e}")
        return False

def get_api_status():
    """Vérifie le statut de l'API"""
    try:
        response = requests.get(f"{API_BASE_URL}/status")
        if response.status_code == 200:
            status = response.json()
            print(f"📊 Statut API:")
            print(f"   • Chunks chargés: {status['chunks_loaded']}")
            print(f"   • Embeddings créés: {status['embeddings_created']}")
            print(f"   • Modèle chargé: {status['model_loaded']}")
            return True
        else:
            print("❌ Impossible d'obtenir le statut")
            return False
    except Exception as e:
        print(f"❌ Erreur statut: {e}")
        return False

def main():
    print("🚀 Démonstration PDF Chat Assistant")
    print("=" * 50)
    
    # Vérifier la clé API OpenAI
    openai_key = os.getenv("OPENAI_API_KEY")
    if not openai_key:
        print("⚠️  Variable OPENAI_API_KEY non trouvée")
        openai_key = input("Entrez votre clé API OpenAI: ").strip()
        if not openai_key:
            print("❌ Clé API OpenAI requise pour la démonstration")
            return
    
    # Attendre que l'API soit prête
    if not wait_for_api():
        print("💡 Assurez-vous que l'API est démarrée avec: python start_app.py")
        return
    
    # Télécharger le PDF exemple
    if not download_example_pdf():
        return
    
    # Upload du PDF
    if not upload_pdf_to_api():
        return
    
    # Vérifier le statut
    get_api_status()
    
    # Questions de test
    test_questions = [
        "Résumez ce document",
        "De quoi parle ce PDF ?",
        "Quelles sont les informations principales ?",
    ]
    
    print("\n💬 Test des questions...")
    print("-" * 30)
    
    for question in test_questions:
        success = test_chat(question, openai_key)
        if success:
            time.sleep(1)  # Petit délai entre les questions
        else:
            break
    
    # Nettoyage
    try:
        os.remove(PDF_LOCAL_PATH)
        print(f"\n🧹 Fichier temporaire supprimé: {PDF_LOCAL_PATH}")
    except:
        pass
    
    print("\n✨ Démonstration terminée !")
    print("💡 Vous pouvez maintenant utiliser l'interface web sur http://localhost:8501")

if __name__ == "__main__":
    main()