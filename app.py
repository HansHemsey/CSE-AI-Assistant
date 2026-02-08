import streamlit as st
import os
from openai import OpenAI
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

# --- CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="CSE Assistant AI - Président",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar repliée pour plus d'immersion
)

# --- CONSTANTES & PATHS ---
DATA_FOLDER = "data"
INDEX_FOLDER = "faiss_index"
MODEL_NAME = "sonar" # Modèle demandé

# --- CSS FUTURISTE ---
st.markdown("""
<style>
    /* Fond global */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 50%, #111 0%, #000 100%);
    }
    
    /* Input Chat Style Console */
    .stTextInput > div > div > input {
        background-color: #111;
        color: #00ADB5;
        border: 1px solid #333;
    }
    
    /* Titres Néons */
    h1 {
        text-shadow: 0 0 10px rgba(0, 173, 181, 0.7);
        font-family: 'Courier New', monospace;
    }

    /* Boites de chat utilisateur */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(odd) {
        background-color: rgba(255, 255, 255, 0.05);
        border-left: 3px solid #777;
    }
    
    /* Boites de chat Assistant */
    .stChatMessage[data-testid="stChatMessage"]:nth-child(even) {
        background-color: rgba(0, 173, 181, 0.05);
        border-right: 3px solid #00ADB5;
        box-shadow: 0 0 20px rgba(0, 173, 181, 0.1);
    }
    
    /* Cacher le menu hamburger standard de Streamlit pour faire plus "App" */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- GESTION DE LA CLÉ API ---
try:
    api_key = st.secrets["PERPLEXITY_API_KEY"]
except FileNotFoundError:
    st.error("⚠️ Fichier .streamlit/secrets.toml manquant ou clé non trouvée.")
    st.stop()

# --- FONCTIONS COEUR (Backend) ---

@st.cache_resource
def load_knowledge_base():
    """
    Logique intelligente :
    1. Vérifie si un index vectoriel existe déjà sur le disque.
    2. Si OUI : Le charge (Ultra rapide < 1s).
    3. Si NON : Scanne le dossier 'data', ingère les PDF, crée l'index et le sauvegarde.
    """
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    
    # Vérification si l'index existe déjà
    if os.path.exists(INDEX_FOLDER) and os.path.exists(f"{INDEX_FOLDER}/index.faiss"):
        print("Chargement de l'index existant...")
        return FAISS.load_local(INDEX_FOLDER, embeddings, allow_dangerous_deserialization=True)
    
    # Sinon, création de l'index (premier lancement uniquement)
    print("Création du nouvel index à partir des PDF...")
    documents = []
    
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        st.error(f"Le dossier '{DATA_FOLDER}' est vide. Veuillez y placer vos PDF et relancer.")
        st.stop()
        
    pdf_files = [f for f in os.listdir(DATA_FOLDER) if f.endswith('.pdf')]
    
    if not pdf_files:
        st.error(f"Aucun fichier PDF trouvé dans '{DATA_FOLDER}'.")
        st.stop()

    # Chargement des fichiers
    with st.spinner(f"Initialisation du système : Ingestion de {len(pdf_files)} documents..."):
        for file in pdf_files:
            file_path = os.path.join(DATA_FOLDER, file)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())

        # Découpage
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)
        
        # Vectorisation
        vector_store = FAISS.from_documents(splits, embeddings)
        
        # Sauvegarde sur disque pour les prochaines fois
        vector_store.save_local(INDEX_FOLDER)
        
    return vector_store

def get_perplexity_response(messages, context):
    """Appel à l'API Perplexity (Sonar) avec Garde-fous stricts"""
    client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
    
    # --- PROMPT SYSTÈME RENFORCÉ (GARDE-FOUS) ---
    system_content = f"""
    ### RÔLE ET IDENTITÉ
    Tu es "L'Assistant Stratégique du Président du CSE". Tu es un expert en Droit du Travail, en relations sociales et en fonctionnement des instances représentatives du personnel en France.
    
    ### PÉRIMÈTRE D'INTERVENTION STRICT
    Tu dois UNIQUEMENT répondre aux questions concernant :
    1. Le fonctionnement, les attributions et les missions du CSE (Comité Social et Économique).
    2. La législation du travail en France (Code du travail, conventions collectives).
    3. Les documents internes de l'entreprise fournis ci-dessous.
    
    ### RÈGLES DE SÉCURITÉ (GUARDRAILS)
    - SI la question de l'utilisateur sort de ce cadre (ex: sport, cuisine, politique générale, code informatique, blagues), tu dois REFUSER de répondre en disant : "Je suis un assistant spécialisé pour le CSE. Je ne peux pas répondre aux questions hors de ce périmètre."
    - Ne jamais inventer de jurisprudence. Si tu ne trouves pas l'info, dis-le.
    
    ### CONTEXTE INTERNE (Documents Officiels - RAG) :
    Les informations suivantes proviennent des documents PDF de l'entreprise. C'est ta source de vérité prioritaire :
    ---
    {context}
    ---
    
    ### INSTRUCTIONS DE RÉPONSE
    1. Analyse d'abord le CONTEXTE INTERNE ci-dessus.
    2. Si l'info manque, utilise tes connaissances juridiques et la recherche internet (Perplexity) pour compléter, MAIS reste strictement focalisé sur la France et le CSE.
    3. Cite tes sources (ex: "Selon l'article L2312-5 du Code du travail..." ou "D'après le PDF fourni...").
    """
    
    # Préparation des messages pour l'API
    final_messages = [{"role": "system", "content": system_content}]
    
    # On ajoute l'historique de conversation (nettoyé des anciens system prompts)
    for msg in messages:
        if msg["role"] != "system":
            final_messages.append(msg)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME, 
            messages=final_messages,
            stream=True
        )
        return response
    except Exception as e:
        return f"Erreur API : {str(e)}"

# --- INITIALISATION ---

if "messages" not in st.session_state:
    st.session_state.messages = []

# Chargement de la base de connaissances (Mise en cache)
try:
    vector_store = load_knowledge_base()
except Exception as e:
    st.error(f"Erreur critique lors du chargement de la base : {e}")
    st.stop()

# --- INTERFACE PRINCIPALE ---

col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80) # Icone placeholder style IA
with col2:
    st.title("CSE / ASSISTANT AI")
    st.caption(f"Bienvenue dans votre assistant stratégique spécialisé pour le Comité Social et Économique. Posez vos questions sur le droit du travail, les missions du CSE.")
    st.caption("L'IA s'appuie sur une base de connaissances alimentée par Legifrance et la recherche en temps réel sur internet pour vous fournir des réponses précises et contextualisées.")

# Affichage Historique
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Zone Input
if prompt := st.chat_input("Entrez votre directive ou question..."):
    
    # 1. User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. RAG Retrieval (Recherche vectorielle locale)
    docs = vector_store.similarity_search(prompt, k=3)
    retrieved_context = "\n\n".join([d.page_content for d in docs])

    # 3. AI Generation
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # Appel API
        stream = get_perplexity_response(st.session_state.messages, retrieved_context)
        
        if isinstance(stream, str): # Cas d'erreur
            st.error(stream)
        else:
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Sauvegarde Assistant Message
            st.session_state.messages.append({"role": "assistant", "content": full_response})