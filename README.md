# 📄 PDF Chat Assistant

Une application moderne pour discuter avec vos documents PDF en utilisant l'intelligence artificielle. Téléchargez un PDF et posez des questions sur son contenu - l'IA vous répondra en citant les sources précises !

## ✨ Fonctionnalités

- 📁 **Upload de fichiers PDF** - Téléchargez directement vos documents
- 🌐 **Support d'URL** - Chargez des PDF depuis internet via URL
- 💬 **Chat interactif** - Interface de conversation intuitive
- 🔍 **Recherche sémantique** - Trouve les passages les plus pertinents
- 📚 **Citations précises** - Indique les pages sources des réponses
- 🎨 **Interface moderne** - Design élégant avec Streamlit
- 🚀 **API RESTful** - Backend FastAPI pour une intégration facile

## 🛠️ Technologies utilisées

- **Backend**: FastAPI, Python
- **Frontend**: Streamlit
- **IA**: OpenAI GPT-3.5-turbo
- **Embeddings**: Sentence Transformers
- **PDF**: PyMuPDF (fitz)
- **Recherche**: Cosine similarity avec scikit-learn

## 📦 Installation

1. **Clonez le repository**:
```bash
git clone <repository-url>
cd pdf-chat-assistant
```

2. **Installez les dépendances**:
```bash
pip install -r requirements.txt
```

3. **Configurez votre clé API OpenAI**:
```bash
# Créez un fichier .env
cp .env.example .env

# Éditez le fichier .env et ajoutez votre clé API
OPENAI_API_KEY=your_api_key_here
```

## 🚀 Démarrage rapide

### Option 1: Script automatique (Recommandé)
```bash
python start_app.py
```

### Option 2: Démarrage manuel

**Terminal 1 - API Backend**:
```bash
uvicorn api:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Interface utilisateur**:
```bash
streamlit run app.py --server.port 8501
```

## 🖥️ Accès à l'application

- **Interface utilisateur**: http://localhost:8501
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/status

## 📱 Utilisation

1. **Configurez votre clé API** dans la barre latérale
2. **Téléchargez un PDF** (fichier local ou URL)
3. **Attendez le traitement** (création des embeddings)
4. **Posez vos questions** dans l'interface de chat
5. **Recevez des réponses** avec citations des pages sources

### Exemples de questions
- "Résumez ce document"
- "Quels sont les points principaux ?"
- "Y a-t-il des recommandations ?"
- "Expliquez [concept spécifique] en détail"

## 🔧 API Endpoints

### Upload d'un PDF
```bash
POST /upload-pdf
Content-Type: multipart/form-data
Body: file (PDF)
```

### Upload depuis URL
```bash
POST /upload-pdf-url?url=https://example.com/document.pdf
```

### Chat avec le PDF
```bash
POST /chat
Content-Type: application/json
Body: {
  "question": "Votre question",
  "openai_key": "votre_clé_api" (optionnel)
}
```

### Vérifier le statut
```bash
GET /status
```

## 🐳 Docker

```bash
# Construire l'image
docker build -t pdf-chat-assistant .

# Lancer le conteneur
docker run -p 8000:8000 -p 8501:8501 -e OPENAI_API_KEY=your_key pdf-chat-assistant
```

Ou avec docker-compose:
```bash
docker-compose up
```

## 🔐 Configuration

### Variables d'environnement

| Variable | Description | Requis |
|----------|-------------|--------|
| `OPENAI_API_KEY` | Clé API OpenAI | Oui* |
| `API_HOST` | Host de l'API | Non (défaut: localhost) |
| `API_PORT` | Port de l'API | Non (défaut: 8000) |
| `STREAMLIT_PORT` | Port Streamlit | Non (défaut: 8501) |

*Peut être configuré dans l'interface

### Obtenir une clé API OpenAI

1. Visitez [OpenAI Platform](https://platform.openai.com/account/api-keys)
2. Créez un compte ou connectez-vous
3. Générez une nouvelle clé API
4. Copiez la clé dans votre fichier `.env` ou l'interface

## 🏗️ Architecture

```
┌─────────────────┐    HTTP     ┌─────────────────┐
│   Streamlit     │──────────▶  │   FastAPI       │
│   Frontend      │             │   Backend       │
│   (Port 8501)   │◀────────────│   (Port 8000)   │
└─────────────────┘   JSON      └─────────────────┘
                                          │
                                          ▼
┌─────────────────┐             ┌─────────────────┐
│   Sentence      │             │   OpenAI API    │
│   Transformers  │             │   GPT-3.5       │
│   (Embeddings)  │             │   (Génération)  │
└─────────────────┘             └─────────────────┘
```

## 🤝 Contribution

1. Fork le projet
2. Créez une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changes (`git commit -m 'Add AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrez une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🐛 Support

Si vous rencontrez des problèmes:

1. Vérifiez que toutes les dépendances sont installées
2. Assurez-vous que votre clé API OpenAI est valide
3. Consultez les logs pour les erreurs détaillées
4. Ouvrez une issue sur GitHub

## 🔮 Roadmap

- [ ] Support de plus de formats (Word, PowerPoint)
- [ ] Historique des conversations persistant
- [ ] Support de modèles LLM alternatifs
- [ ] Amélioration de l'interface mobile
- [ ] Export des conversations
- [ ] Support multilingue
- [ ] Intégration avec des bases de données vectorielles

## ⭐ Remerciements

- OpenAI pour l'API GPT
- Sentence Transformers pour les embeddings
- Streamlit pour l'interface utilisateur
- FastAPI pour le backend
- PyMuPDF pour le traitement PDF
