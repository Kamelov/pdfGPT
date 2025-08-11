#!/usr/bin/env python3
"""
Script pour démarrer l'application PDF Chat Assistant
Lance automatiquement l'API FastAPI et l'interface Streamlit
"""

import subprocess
import time
import os
import sys
import signal
from multiprocessing import Process

def start_api():
    """Démarre l'API FastAPI"""
    print("🚀 Démarrage de l'API FastAPI...")
    os.system("uvicorn api:app --host 0.0.0.0 --port 8000 --reload")

def start_streamlit():
    """Démarre l'interface Streamlit"""
    print("🌐 Démarrage de l'interface Streamlit...")
    time.sleep(3)  # Attendre que l'API soit prête
    os.system("streamlit run app.py --server.port 8501 --server.address 0.0.0.0")

def check_dependencies():
    """Vérifie si toutes les dépendances sont installées"""
    try:
        import streamlit
        import fastapi
        import uvicorn
        import fitz
        import sentence_transformers
        import openai
        print("✅ Toutes les dépendances sont installées")
        return True
    except ImportError as e:
        print(f"❌ Dépendance manquante: {e}")
        print("📦 Installez les dépendances avec: pip install -r requirements.txt")
        return False

def main():
    print("📄 PDF Chat Assistant - Démarrage")
    print("=" * 50)
    
    # Vérifier les dépendances
    if not check_dependencies():
        sys.exit(1)
    
    # Vérifier la clé API OpenAI
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Clé API OpenAI non trouvée dans les variables d'environnement")
        print("💡 Vous pouvez la configurer dans l'interface ou via la variable OPENAI_API_KEY")
    
    try:
        # Démarrer les processus
        api_process = Process(target=start_api)
        streamlit_process = Process(target=start_streamlit)
        
        api_process.start()
        streamlit_process.start()
        
        print("\n🎉 Application démarrée avec succès !")
        print("📋 Informations d'accès:")
        print("   • API FastAPI: http://localhost:8000")
        print("   • Interface utilisateur: http://localhost:8501")
        print("\n⏹️  Appuyez sur Ctrl+C pour arrêter l'application")
        
        # Attendre les processus
        api_process.join()
        streamlit_process.join()
        
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de l'application...")
        
        # Arrêter les processus
        if api_process.is_alive():
            api_process.terminate()
            api_process.join()
        
        if streamlit_process.is_alive():
            streamlit_process.terminate()
            streamlit_process.join()
        
        print("✅ Application arrêtée")

if __name__ == "__main__":
    main()