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
st.caption("Scénario par Google Gemini ⚡ | Audio par OpenAI 🔊 | Créé avec ❤️ par Papounet")

with st.sidebar:
    st.header("👶 L'Enfant")
    col1, col2 = st.columns(2)
    with col1: sexe = st.radio("Genre", ["Garçon 👦", "Fille 👧"])
    with col2: age = st.number_input("Âge", 1, 2, 3, 4, 5)
    prenom = st.text_input("Prénom", placeholder="ex: Maxence")
    
    st.divider()
    st.header("✨ L'Histoire")
    theme = st.selectbox("Thème", ["Animaux 🐻", "Espace 🚀", "Magie ✨", "Dinosaures 🦖", "Super-Héros ⚡", "Océan 🐳"])
    compagnon = st.text_input("Compagnon", placeholder="ex: Ulysse le chat")
    lecon = st.selectbox("Morale", ["Aucune", "Courage 🦁", "Partage 🤝", "Patience ⏳", "Calme 🧘"])
    
    st.divider()
    st.header("🔊 Voix")
    voice_map = {"Nova (Énergique)": "nova", "Shimmer (Douce)": "shimmer", "Fable (Conteur)": "fable", "Onyx (Grave)": "onyx"}
    voice_choice = st.selectbox("Narrateur", list(voice_map.keys()), index=1)

# ==========================================
# 4. LOGIQUE METIER
# ==========================================
def generate_story_gemini():
    genre = "garçon" if "Garçon" in sexe else "fille"
    nom = prenom if prenom else f"le petit {genre}"
    
    # Adaptation au user profile
    if age <= 2:
        style = "Phrases très courtes (3 mots). Beaucoup de répétitions. Onomatopées. Ton bébé doux."
    elif age <= 5:
        style = "Phrases simples. Structure claire. Vocabulaire joyeux."
    else:
        style = "Vocabulaire riche. Intrigue avec rebondissements."

    prompt = f"""
    Rôle : Auteur jeunesse expert.
    Cible : {genre}, {age} ans.
    Style : {style}
    
    Tâche : Écris une histoire courte sur le thème '{theme}'.
    Héros : {nom}.
    Compagnon : {compagnon if compagnon else "un ami surprise"}.
    Morale : {lecon}.
    
    Format : Titre avec emojis, puis texte aéré avec paragraphes. Pas de préambule.
    """
    
    try:
        # Utilisation du modèle Flash (plus rapide/gratuit)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Erreur Gemini : {e}"

def generate_audio_openai(text, voice_id):
    if not client_audio:
        return None
    try:
        response = client_audio.audio.speech.create(
            model="tts-1",
            voice=voice_id,
            input=text
        )
        return io.BytesIO(response.content)
    except Exception as e:
        st.error(f"Erreur Audio : {e}")
        return None

# ==========================================
# 5. EXECUTION
# ==========================================
if st.button("✨ Raconter l'histoire"):
    with st.spinner("✍️ Gemini écrit l'histoire..."):
        story = generate_story_gemini()
        
    if story and "Erreur" not in story:
        st.markdown("---")
        st.write(story)
        
        # Download Texte
        safe_name = prenom if prenom else "Histoire"
        st.download_button("📄 Télécharger le texte", story, file_name=f"{safe_name}.txt")

        # Audio
        with st.spinner("🎙️ OpenAI génère la voix..."):
            audio_stream = generate_audio_openai(story, voice_map[voice_choice])
            
        if audio_stream:
            st.success("Lecture prête !")
            st.audio(audio_stream, format="audio/mp3")
            st.download_button("📥 Télécharger l'MP3", audio_stream, file_name=f"{safe_name}.mp3", mime="audio/mpeg")
    elif story:
        st.error(story)
        
