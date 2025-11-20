import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Site Mention Analyzer | Avantgrade",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# CSS personalizzato
st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Global Styles */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .main {
        padding: 2rem 1rem;
    }
    
    /* Header */
    .header-container {
        text-align: center;
        margin-bottom: 2rem;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 16px;
        color: white;
    }
    
    .header-container h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .header-container p {
        margin: 0;
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    /* Input fields styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #e0e0e0;
        padding: 0.75rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.3s ease;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.3);
    }
    
    /* Results container */
    .results-container {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .result-item {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1rem;
        margin-bottom: 1rem;
        border-radius: 8px;
    }
    
    .result-item h4 {
        color: #667eea;
        margin-top: 0;
        margin-bottom: 0.5rem;
        font-size: 1.1rem;
    }
    
    .result-item p {
        margin: 0;
        color: #555;
        line-height: 1.6;
    }
    
    /* CTA Box */
    .cta-box {
        background: linear-gradient(135deg, #ff6b35 0%, #ff8e53 100%);
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        margin-top: 3rem;
        box-shadow: 0 10px 25px rgba(255, 107, 53, 0.3);
    }
    
    .cta-box img {
        height: 40px;
        margin-bottom: 1rem;
        filter: brightness(0) invert(1);
    }
    
    .cta-box h3 {
        color: white;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1rem 0;
    }
    
    .btn-orange {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: white;
        color: #ff6b35;
        padding: 1rem 2rem;
        border-radius: 50px;
        text-decoration: none;
        font-weight: 600;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .btn-orange:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.2);
        color: #ff6b35;
    }
    
    .btn-orange svg {
        width: 20px;
        height: 20px;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Info box */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
    }
    
    .info-box p {
        margin: 0;
        color: #1976d2;
    }
    
    /* Error box */
    .error-box {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-box p {
        margin: 0;
        color: #c62828;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1>🎯 Site Mention Analyzer</h1>
        <p>Scopri dove il tuo brand deve essere menzionato per massimizzare la visibilità su Gemini AI</p>
    </div>
""", unsafe_allow_html=True)

# Info box
st.markdown("""
    <div class="info-box">
        <p><strong>💡 Come funziona:</strong> Inserisci il tuo settore, ambito e lingua per scoprire i 5 principali siti informativi e canali dove dovresti essere presente.</p>
    </div>
""", unsafe_allow_html=True)

# Form inputs
col1, col2 = st.columns(2)

with col1:
    mercato = st.text_input("🏢 Mercato/Settore", placeholder="es. Logistica, Baie di carico")

with col2:
    lingua = st.text_input("🌍 Lingua", placeholder="es. Italiano, Inglese")

ambito = st.text_input("🎯 Ambito specifico", placeholder="es. Soluzioni per magazzini, Equipment industriale")

# Inizializza session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Button
analyze_button = st.button("🔍 Analizza ora", use_container_width=True)

# Funzione per chiamare Gemini
def get_gemini_suggestions(mercato, ambito, lingua):
    try:
        # Configura Gemini con la API key dai secrets
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # Lista dei modelli più recenti da provare
        models_to_try = [
            'gemini-2.0-flash-exp',
            'gemini-exp-1206',
            'gemini-exp-1121',
            'gemini-1.5-pro-latest',
            'gemini-1.5-flash-latest',
            'gemini-1.5-pro-002',
            'gemini-1.5-flash-002',
        ]
        
        model = None
        working_model_name = None
        errors = []
        
        # Prova ogni modello fino a trovarne uno che funziona
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                working_model_name = model_name
                break
            except Exception as e:
                errors.append(f"{model_name}: {str(e)}")
                continue
        
        if model is None:
            error_details = "\n".join(errors[:3])
            return f"❌ Errore: Nessun modello Gemini disponibile. Verifica la tua API key su https://aistudio.google.com/app/apikey\n\nDettagli:\n{error_details}"
        
        # Crea il prompt
        prompt = f"""Sei un esperto di GEO (Generative Engine Optimization) e visibilità digitale in Italia.

Un'azienda opera nel settore: {mercato}
Ambito specifico: {ambito}
Mercato di riferimento: Italia
Lingua: {lingua}

Identifica i 10 siti web informativi, portali di settore, blog specializzati e canali YouTube più autorevoli e rilevanti dove questa azienda DEVE essere menzionata per massimizzare la propria visibilità su Gemini AI e altri motori di ricerca generativi.

IMPORTANTE: 
- Escludi siti istituzionali (.gov, .edu)
- Concentrati su: portali informativi di settore, magazine online, blog specializzati, testate giornalistiche di settore, canali YouTube autorevoli
- Per ogni fonte fornisci: nome, tipologia (sito/blog/canale YouTube), e una breve spiegazione (2-3 righe) del perché è importante per la visibilità su Gemini

Formatta la risposta così:

1. [Nome] - [Tipologia]
[Spiegazione dettagliata del perché questo canale è cruciale per la visibilità su Gemini, quali contenuti pubblicano, che autorevolezza hanno nel settore]

2. [Nome] - [Tipologia]
[Spiegazione dettagliata...]

E così via per tutti i 10 suggerimenti."""

        # Configurazione di generazione
        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            top_k=40,
            max_output_tokens=2048,
        )
        
        # Safety settings corretti
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        # Genera la risposta
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Estrai il testo dalla risposta
        if response and hasattr(response, 'text') and response.text:
            return response.text
        elif response and hasattr(response, 'parts') and response.parts:
            return ''.join(part.text for part in response.parts if hasattr(part, 'text'))
        elif response:
            return f"❌ Errore: Risposta ricevuta ma vuota. La risposta potrebbe essere stata bloccata dai filtri di sicurezza."
        else:
            return "❌ Errore: Nessuna risposta dal modello Gemini"
        
    except Exception as e:
        error_message = str(e)
        
        # Messaggi di errore più user-friendly
        if "API_KEY" in error_message.upper() or "api key" in error_message.lower():
            return "❌ Errore: API Key non configurata o non valida.\n\nVerifica su: https://aistudio.google.com/app/apikey"
        elif "QUOTA" in error_message.upper() or "quota" in error_message.lower():
            return "❌ Errore: Quota API esaurita. Verifica il tuo account Google AI Studio."
        elif "RATE_LIMIT" in error_message.upper() or "rate limit" in error_message.lower():
            return "❌ Errore: Limite di richieste raggiunto. Riprova tra qualche minuto."
        elif "404" in error_message:
            return f"❌ Errore 404: Modelli non trovati.\n\nSoluzione:\n1. Vai su https://aistudio.google.com/app/apikey\n2. Crea una nuova API key\n3. Assicurati che sia abilitata per Gemini API\n\nErrore tecnico: {error_message}"
        elif "PERMISSION" in error_message.upper() or "permission" in error_message.lower():
            return "❌ Errore: Permessi insufficienti. Verifica che la tua API key sia attiva."
        elif "SAFETY" in error_message.upper():
            return "❌ Errore: La risposta è stata bloccata dai filtri di sicurezza. Riprova con una richiesta leggermente diversa."
        else:
            return f"❌ Errore imprevisto: {error_message}\n\nSe il problema persiste, crea una nuova API key su: https://aistudio.google.com/app/apikey"

# Processo di analisi
if analyze_button:
    if not mercato or not ambito or not lingua:
        st.error("⚠️ Per favore compila tutti i campi")
    else:
        with st.spinner("🔄 Sto analizzando i migliori canali per la tua visibilità su Gemini..."):
            result = get_gemini_suggestions(mercato, ambito, lingua)
            st.session_state.results = result
            st.session_state.show_results = True

# Mostra risultati
if st.session_state.show_results and st.session_state.results:
    st.markdown("---")
    
    # Controlla se c'è un errore
    if st.session_state.results.startswith("❌"):
        st.markdown(f"""
            <div class="error-box">
                <p style="white-space: pre-wrap;">{st.session_state.results}</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("### 📊 Risultati dell'Analisi")
        
        # Split dei risultati - LOGICA MIGLIORATA per mostrare 5 risultati COMPLETI
        full_results = st.session_state.results
        results_lines = full_results.split('\n')
        
        display_lines = []
        count = 0
        in_result = False
        
        for i, line in enumerate(results_lines):
            # Rileva l'inizio di un nuovo risultato numerato
            if line.strip() and len(line.strip()) > 0:
                first_chars = line.strip()[:3]
                # Controlla se inizia con un numero seguito da un punto
                if any(char.isdigit() for char in first_chars) and '.' in first_chars:
                    count += 1
                    in_result = True
                    
                    # Se abbiamo già 5 risultati completi, fermiamoci
                    if count > 5:
                        break
            
            # Aggiungi la linea se siamo dentro i primi 5 risultati
            if count <= 5:
                display_lines.append(line)
            elif count == 6:
                # Appena inizia il 6° risultato, fermiamoci
                break
        
        # Mostra i primi 5 risultati COMPLETI
        preview_text = '\n'.join(display_lines)
        
        st.markdown(f"""
            <div class="results-container">
                <div style="white-space: pre-wrap;">{preview_text}</div>
            </div>
        """, unsafe_allow_html=True)
        
        # CTA Box con testo corretto
        st.markdown("""
            <div class="cta-box">
                <img src="https://www.avantgrade.com/wp-content/themes/avantgrade/assets/img/logo-colored.svg" alt="Avantgrade Logo">
                <h3>Vuoi scoprire gli altri 5 siti e canali strategici?</h3>
                <p style="color: white; opacity: 0.95; margin-bottom: 1.5rem;">Contatta Avantgrade per ottenere l'analisi completa con tutti i 10 siti identificati e una strategia personalizzata per dominare Gemini AI nel tuo settore</p>
                <a class="btn-orange" target="_blank" href="https://www.avantgrade.com/schedule-a-call?utm_source=streamlit&utm_medium=geo_tool&utm_campaign=mention_analyzer">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 23.001 27.343" fill="currentColor">
                        <path d="m6.606 26.641-.339-.521A7.816 7.816 0 0 0 7.49 14l-.106-.1L1.49 8.282A4.827 4.827 0 0 1 0 4.8v-.516A4.217 4.217 0 0 1 2.235.528 4.217 4.217 0 0 1 6.6.7l14.451 9.383a4.278 4.278 0 0 1 0 7.175L6.607 26.641Zm.97-13.419.238.225a8.451 8.451 0 0 1 1.127 10.937l11.774-7.647a3.656 3.656 0 0 0 0-6.132L6.265 1.221a3.6 3.6 0 0 0-3.733-.147 3.6 3.6 0 0 0-1.91 3.21V4.8a4.2 4.2 0 0 0 1.3 3.029Z"/>
                        <path d="M4.28 27.343a4.277 4.277 0 0 1-2.045-.527A4.217 4.217 0 0 1 0 23.059v-.518a4.828 4.828 0 0 1 1.491-3.48L7.6 13.242l.214.2a8.438 8.438 0 0 1-1.21 13.2 4.254 4.254 0 0 1-2.323.7M7.6 14.103l-5.68 5.408a4.2 4.2 0 0 0-1.3 3.03v.518a3.6 3.6 0 0 0 1.91 3.21 3.6 3.6 0 0 0 3.733-.147A7.817 7.817 0 0 0 7.6 14.103"/>
                        <path d="m7.614 14.088-.23-.19-5.893-5.616A4.826 4.826 0 0 1 0 4.8v-.516A4.216 4.216 0 0 1 2.235.527 4.215 4.215 0 0 1 6.6.7a8.438 8.438 0 0 1 1.228 13.183ZM4.279.623a3.654 3.654 0 0 0-1.748.451 3.6 3.6 0 0 0-1.91 3.21V4.8a4.2 4.2 0 0 0 1.3 3.03l5.674 5.41a7.816 7.816 0 0 0-1.33-12.02 3.637 3.637 0 0 0-1.986-.6"/>
                        <path d="M1.177 16.875a1.184 1.184 0 0 1-.467-.1A1.155 1.155 0 0 1 0 15.701v-4.062a1.155 1.155 0 0 1 .71-1.076 1.154 1.154 0 0 1 1.269.229L5 13.67l-3.021 2.879a1.159 1.159 0 0 1-.8.326m0-5.789a.561.561 0 0 0-.222.047.535.535 0 0 0-.333.505v4.063a.535.535 0 0 0 .331.509.535.535 0 0 0 .6-.107L4.1 13.67l-2.55-2.429a.537.537 0 0 0-.374-.154"/>
                    </svg>
                    Richiedi Analisi Completa
                </a>
            </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #888; padding: 2rem 0;">
        <p>Powered by <strong>Avantgrade.com</strong> | GEO & AI Search Optimization Experts</p>
    </div>
""", unsafe_allow_html=True)
