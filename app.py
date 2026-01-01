import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import io

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(page_title="Histoires Magiques ✨", page_icon="🦄", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #F0F8FF; }
    div.stButton > button {
        background-color: #FF69B4; color: white; border-radius: 25px; 
        padding: 12px 28px; font-size: 1.3em; font-weight: bold; border: none; width: 100%;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
    }
    div.stButton > button:hover { background-color: #FF1493; transform: scale(1.02); color: white;}
    h1, h2 { color: #4B0082; font-family: 'Comic Sans MS', sans-serif; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. AUTHENTIFICATION (Gérée par Streamlit Secrets)
# ==========================================
# On vérifie que les clés existent bien (elles seront ajoutées à l'étape 5)
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Il manque la clé Google API dans les Secrets.")
    st.stop()
    
if "OPENAI_API_KEY" not in st.secrets:
    st.warning("Il manque la clé OpenAI API. L'audio ne fonctionnera pas.")

# Configuration des clients
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

try:
    client_audio = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except:
    client_audio = None

# ==========================================
# 3. INTERFACE UTILISATEUR
# ==========================================
st.title("🦄 La Fabrique à Histoires")
st.caption("Scénario par Google Gemini ⚡ | Audio par OpenAI 🔊" | Créé avec ❤️ par Papounet)

with st.sidebar:
    st.header("👶 L'Enfant")
    col1, col2 = st.columns(2)
    with col1: sexe = st.radio("Genre", ["Garçon 👦", "Fille 👧"])
    with col2: age = st.number_input("Âge", 1, 2, 3, 4)
    prenom = st.text_input("Prénom", placeholder="ex: Maxence")
    
    st.divider()
