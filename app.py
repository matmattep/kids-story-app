import streamlit as st
import google.generativeai as genai
from openai import OpenAI
import io

# ==========================================
# 1. CONFIGURATION & STYLE
# ==========================================
st.set_page_config(page_title="Histoires Magiques ✨", page_icon="🦄", layout="centered")

# Initialisation des variables de session (Mémoire)
# Nécessaire pour que le zoom ne régénère pas une nouvelle histoire
if 'current_story' not in st.session_state:
    st.session_state.current_story = ""
if 'text_size' not in st.session_state:
    st.session_state.text_size = 18  # Taille par défaut

st.markdown("""
<style>
    /* Fond général */
    .stApp { 
        background-color: #F0F8FF; 
    }
    
    /* CORRECTION : Force le texte en gris foncé partout */
    .stApp, .stMarkdown, p, div {
        color: #333333;
    }
    
    /* Force la couleur des titres */
    h1, h2, h3, h4, h5, h6 { 
        color: #4B0082 !important; 
        font-family: 'Comic Sans MS', 'Chalkboard SE', sans-serif; 
    }
    
    /* Style du bouton principal */
    div.stButton > button {
        background-color: #FF69B4; 
        color: white !important;
        border-radius: 25px; 
        font-weight: bold; 
        border: none; 
        box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    div.stButton > button:hover { 
        background-color: #FF1493; 
        transform: scale(1.02); 
    }
    
    /* Style spécifique pour les petits boutons de zoom (via selecteur CSS partiel) */
    div[data-testid="column"] button {
        background-color: #4B0082;
        padding: 5px 15px;
        font-size: 1em;
    }

    /* Labels */
    .stRadio label, .stNumberInput label, .stTextInput label, .stSelectbox label, .stSlider label {
        color: #333333 !important;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 2. AUTHENTIFICATION
# ==========================================
if "GOOGLE_API_KEY" not in st.secrets:
    st.error("Il manque la clé Google API dans les Secrets.")
    st.stop()

# On ne bloque pas si OpenAI manque, sauf si l'utilisateur veut de l'audio
has_openai = "OPENAI_API_KEY" in st.secrets

try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except:
    pass

try:
    if has_openai:
        client_audio = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    else:
        client_audio = None
except:
    client_audio = None

# ==========================================
# 3. INTERFACE UTILISATEUR (SIDEBAR)
# ==========================================
st.title("🦄 La Fabrique à Histoires")
st.caption("Cree avec ❤️ par Papa | Moteur : Google Gemini 2.5 Flash ⚡ | Audio : OpenAI 🔊")

with st.sidebar:
    st.header("👶 L'Enfant")
    col1, col2 = st.columns(2)
    with col1: sexe = st.radio("Genre", ["Garçon 👦", "Fille 👧"])
    with col2: age = st.number_input("Âge", 1, 10, 4)
    prenom = st.text_input("Prénom", placeholder="ex: Maxence")
    
    st.divider()
    st.header("✨ L'Histoire")
    theme = st.selectbox("Thème", ["Animaux 🐻", "Espace 🚀", "Magie ✨", "Dinosaures 🦖", "Super-Héros ⚡", "Océan 🐳", "Pirates 🏴‍☠️", "Chevaliers 🏰"])
    compagnon = st.text_input("Compagnon", placeholder="ex: Ulysse le chat")
    lecon = st.selectbox("Morale", ["Aucune", "Courage 🦁", "Partage 🤝", "Patience ⏳", "Calme 🧘", "Honnêteté 😇"])
    
    # NOUVEAU : Slider de durée
    duree = st.select_slider(
        "Durée de lecture (estimée)", 
        options=[1, 2, 3, 4, 5], 
        value=3,
        format_func=lambda x: f"{x} min"
    )

    st.divider()
    
    # NOUVEAU : Choix du rendu
    st.header("⚙️ Options")
    mode_rendu = st.radio("Format de sortie", ["Histoire seule 📜", "Histoire + Audio 🎧"], index=1)
    
    if "Audio" in mode_rendu:
        voice_map = {"Nova (Énergique)": "nova", "Shimmer (Douce)": "shimmer", "Fable (Conteur)": "fable", "Onyx (Grave)": "onyx"}
        voice_choice = st.selectbox("Narrateur", list(voice_map.keys()), index=1)
    else:
        voice_choice = None


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

    # Calcul approximatif de la longueur (1 min de lecture ~ 130 mots pour enfant)
    target_words = duree * 130
    length_instruction = f"Longueur cible : environ {target_words} mots (pour une lecture de {duree} minutes)."

    prompt = f"""
    Rôle : Auteur jeunesse expert.
    Cible : {genre}, {age} ans.
    Style : {style}
    {length_instruction}
    
    Tâche : Écris une histoire sur le thème '{theme}'.
    Héros : {nom}.
    Compagnon : {compagnon if compagnon else "un ami surprise"}.
    Morale : {lecon}.
    
    Format : Titre avec emojis, puis texte aéré avec paragraphes. Pas de préambule.
    """
    
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
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

# Bouton principal de génération
if st.button("✨ Raconter l'histoire"):
    # On vide l'ancienne histoire
    st.session_state.current_story = "" 
    
    with st.spinner("✍️ Gemini écrit l'histoire..."):
        # Génération et stockage dans la session
        st.session_state.current_story = generate_story_gemini()

# Affichage du résultat (s'il y a une histoire en mémoire)
if st.session_state.current_story:
    story = st.session_state.current_story
    
    if "Erreur" not in story:
        st.markdown("---")
        
        # NOUVEAU : Contrôles de Zoom
        col_z1, col_z2, col_z3 = st.columns([1, 1, 4])
        with col_z1:
            if st.button("Agrandir ➕"):
                st.session_state.text_size += 2
        with col_z2:
            if st.button("Rétrécir ➖"):
                st.session_state.text_size = max(10, st.session_state.text_size - 2)
        
        # Affichage du texte avec la taille dynamique HTML/CSS
        st.markdown(
            f"<div style='font-size:{st.session_state.text_size}px; line-height: 1.6;'>{story}</div>", 
            unsafe_allow_html=True
        )
        
        st.markdown("---")
        
        # Download Texte
        safe_name = prenom if prenom else "Histoire"
        st.download_button("📄 Télécharger le texte", story, file_name=f"{safe_name}.txt")

        # Gestion de l'audio SEULEMENT si demandé
        if "Audio" in mode_rendu and voice_choice:
            # On vérifie si on a déjà généré l'audio pour éviter de le refaire à chaque clic de zoom
            # (Note: ici par simplicité on le régénère à la demande initiale, 
            # pour optimiser parfaitement on pourrait aussi le stocker en session_state, 
            # mais attention à la mémoire RAM).
            
            # Ici, on lance l'audio uniquement si on vient de cliquer sur "Raconter" 
            # OU si l'utilisateur le veut vraiment. 
            # Pour faire simple : on lance la génération audio ici.
            
            # Note : Pour éviter de re-payer l'API audio quand on clique sur Zoom, 
            # l'idéal est de générer l'audio une seule fois.
            # Voici une implémentation simple : le lecteur apparaît, 
            # mais attention, si tu cliques sur Zoom, l'audio va se recharger.
            
            with st.spinner("🎙️ Génération de la voix..."):
                voice_id = voice_map[voice_choice]
                audio_stream = generate_audio_openai(story, voice_id)
                
            if audio_stream:
                st.audio(audio_stream, format="audio/mp3")
                st.download_button("📥 MP3", audio_stream, file_name=f"{safe_name}.mp3", mime="audio/mpeg")
            elif not has_openai:
                st.warning("Clé OpenAI manquante pour l'audio.")

    else:
        st.error(story)
            
