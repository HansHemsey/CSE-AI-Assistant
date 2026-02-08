# CSE Assistant AI - Président

Assistant IA spécialisé pour le CSE (Comité Social et Économique) utilisant Streamlit et la technologie RAG (Retrieval-Augmented Generation).

## 🚀 Fonctionnalités

- **Base de connaissances intelligente** : Ingestion et vectorisation de documents PDF
- **Recherche vectorielle** : Récupération contextuelle des informations pertinentes
- **IA Conversationnelle** : Réponses basées sur Perplexity (Modèle Sonar)
- **Garde-fous juridiques** : Limité aux questions CSE et droit du travail français

## 📋 Prérequis

- Python 3.8+
- Une clé API Perplexity (https://www.perplexity.ai/api)

## 🔧 Installation

1. **Cloner le repository**
```bash
git clone <your-repo-url>
cd cse_assistant_ia
```

2. **Créer un environnement virtuel**
```bash
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configurer les secrets**
```bash
cp .streamlit/secrets.example.toml .streamlit/secrets.toml
```

Éditer `.streamlit/secrets.toml` et ajouter votre clé API Perplexity :
```toml
PERPLEXITY_API_KEY = "votre_clé_ici"
```

5. **Ajouter vos documents PDF**
Placez vos fichiers PDF dans le dossier `data/` :
```
data/
├── cse_bible_1.pdf
├── cse_bible_2.pdf
└── ...
```

6. **Lancer l'application**
```bash
streamlit run app.py
```

L'application sera accessible à `http://localhost:8501`

## 📁 Structure du projet

```
cse_assistant_ia/
├── app.py                          # Application principale Streamlit
├── requirements.txt                # Dépendances Python
├── .gitignore                      # Fichiers à exclure de Git
├── README.md                       # Ce fichier
├── data/                           # Dossier pour vos PDF
│   ├── cse_bible_1.pdf
│   └── cse_bible_2.pdf
├── .streamlit/
│   ├── config.toml                # Configuration Streamlit
│   ├── secrets.example.toml        # Modèle pour les secrets
│   └── secrets.toml                # ⚠️ JAMAIS à commiter (dans .gitignore)
└── faiss_index/                    # Index vectoriel (auto-généré, dans .gitignore)
    └── index.faiss
```

## 🔒 Sécurité

- **Ne JAMAIS commiter `.streamlit/secrets.toml`** (contient votre clé API)
- Utilisez `.streamlit/secrets.example.toml` comme template
- Les fichiers `.pdf` sont sauvegardés sur GitHub (pas de données sensibles)
- L'index FAISS est régénéré automatiquement au premier lancement

## 📚 Utilisation

Posez vos questions concernant :
- Le fonctionnement du CSE
- La législation du travail en France
- Les documents internes fournis

L'assistant refusera de répondre aux questions hors de ce périmètre.

## 🛠️ Technologies

- **Streamlit** : Interface web
- **Perplexity AI (Sonar)** : Modèle de langage
- **LangChain** : Framework RAG
- **FAISS** : Recherche vectorielle
- **HuggingFace Embeddings** : Vectorisation du texte
- **PyPDF** : Chargement de PDF

## 📝 License

[À définir selon vos préférences]

## ✍️ Auteur

[Votre nom/Votre organisation]

---

**Développé avec ❤️ pour l'excellence du CSE**
