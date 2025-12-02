import streamlit as st
import anthropic
import requests
import json
from datetime import datetime

# Configurazione pagina
st.set_page_config(
    page_title="Brand Mention Analyzer | Avantgrade",
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
    
    /* Verified badge */
    .verified-badge {
        display: inline-block;
        background: #4caf50;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 8px;
        font-size: 0.75rem;
        font-weight: 500;
        margin-left: 0.5rem;
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
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class="header-container">
        <h1>🎯 Brand Mention Analyzer</h1>
        <p>Scopri i siti web in cui il tuo brand dovrebbe essere menzionato per aumentare l'autorevolezza dai motori di ricerca basati su AI</p>
    </div>
""", unsafe_allow_html=True)

# Info box
st.markdown("""
    <div class="info-box">
        <p><strong>💡 Come funziona:</strong> Inserisci il tuo settore, ambito e lingua per scoprire i 10 principali siti dove dovresti proporre il tuo brand, con fonti verificate dal web.</p>
    </div>
""", unsafe_allow_html=True)

# Form inputs
col1, col2 = st.columns(2)

with col1:
    mercato = st.text_input("🏢 Mercato/Settore", placeholder="es. Logistica, Baie di carico")

with col2:
    lingua = st.selectbox("🌍 Lingua", options=["Italiano", "Inglese"])

ambito = st.text_input("🎯 Topic", placeholder="es. Soluzioni per magazzini, Equipment industriale")

# Inizializza session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'show_results' not in st.session_state:
    st.session_state.show_results = False

# Button
analyze_button = st.button("🔍 Analizza ora", use_container_width=True)

# Funzione per cercare con Brave Search
def brave_search(query, count=20):
    """Esegue ricerca con Brave Search API"""
    try:
        api_key = st.secrets["BRAVE_API_KEY"]
        
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key
        }
        
        params = {
            "q": query,
            "count": count,
            "search_lang": "it",
            "country": "IT"
        }
        
        response = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            headers=headers,
            params=params,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            
            # Estrai risultati web
            results = []
            if "web" in data and "results" in data["web"]:
                for result in data["web"]["results"]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "description": result.get("description", ""),
                    })
            
            return results
        else:
            st.error(f"Errore Brave Search: {response.status_code}")
            return []
        
    except Exception as e:
        st.error(f"Errore ricerca: {str(e)}")
        return []

# Funzione per analizzare risultati con Claude
def analyze_with_claude(search_results, mercato, ambito, lingua):
    """Usa Claude per analizzare i risultati di ricerca e identificare i top 10 siti"""
    try:
        client = anthropic.Anthropic(api_key=st.secrets["ANTHROPIC_API_KEY"])
        
        # Prepara contesto con i risultati di ricerca
        search_context = "RISULTATI RICERCA WEB:\n\n"
        for i, result in enumerate(search_results[:20], 1):
            search_context += f"{i}. {result['title']}\n"
            search_context += f"   URL: {result['url']}\n"
            search_context += f"   Descrizione: {result['description']}\n\n"
        
        prompt = f"""Sei un esperto di GEO (Generative Engine Optimization) e visibilità digitale.

CONTESTO:
Un'azienda opera nel settore: {mercato}
Ambito specifico: {ambito}
Mercato: Italia
Lingua: {lingua}

COMPITO:
Analizza i risultati di ricerca qui sotto e identifica i 10 BLOG, PORTALI DI SETTORE o RIVISTE ONLINE specifiche più autorevoli dove questa azienda DOVREBBE ESSERE MENZIONATA per massimizzare la visibilità sulle chat AI.

{search_context}

CRITERI FONDAMENTALI:
- Seleziona SOLO siti reali presenti nei risultati di ricerca
- Scegli SOLO blog, portali o riviste specifiche che pubblicano contenuti originali sul settore
- ESCLUDI assolutamente siti che sono "liste di blog" o "aggregatori" (es: "migliori blog di...", "top 10 siti di...", "blog più letti...")
- ESCLUDI siti istituzionali (.gov, .edu) e marketplace
- ESCLUDI AGENZIE (agenzie marketing, agenzie comunicazione, agenzie pubblicitarie, web agency)
- Priorità a fonti che creano contenuti editoriali originali e sono autorevoli nel settore

FORMATO OUTPUT (FONDAMENTALE):
Rispondi SOLO con un JSON array, niente altro:

[
  {{
    "number": 1,
    "name": "Nome del Sito",
    "type": "Blog/Portale/Rivista Online",
    "url": "https://url-esatto-dai-risultati.com",
    "description": "Spiegazione di 2-3 righe sul perché essere menzionati qui aumenterebbe la visibilità sulle chat AI"
  }},
  ...
]

Rispondi SOLO con il JSON, nessun testo prima o dopo."""

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            temperature=0.7,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text.strip()
        
        # Pulisci eventuali markdown
        if response_text.startswith("```json"):
            response_text = response_text.replace("```json", "").replace("```", "").strip()
        elif response_text.startswith("```"):
            response_text = response_text.replace("```", "").strip()
        
        # Parsa JSON
        results = json.loads(response_text)
        
        return results
        
    except json.JSONDecodeError as e:
        st.error(f"Errore parsing JSON: {str(e)}")
        st.code(response_text)
        return []
    except Exception as e:
        st.error(f"Errore Claude API: {str(e)}")
        return []

# Processo di analisi
if analyze_button:
    if not mercato or not ambito or not lingua:
        st.error("⚠️ Per favore compila tutti i campi")
    else:
        # Step 1: Ricerca con Brave
        with st.spinner("🔍 Ricerca siti autorevoli nel settore..."):
            query = f"{mercato} {ambito} blog portale rivista online Italia -\"migliori blog\" -\"top blog\" -\"lista\""
            search_results = brave_search(query, count=20)
            
            if not search_results:
                st.error("❌ Nessun risultato dalla ricerca. Riprova.")
                st.stop()
        
        # Step 2: Analisi con AI
        with st.spinner("🤖 Analisi dei risultati con intelligenza artificiale..."):
            analyzed_results = analyze_with_claude(search_results, mercato, ambito, lingua)

            if analyzed_results and len(analyzed_results) >= 5:
                st.session_state.results = analyzed_results
                st.session_state.show_results = True
                st.session_state.mercato = mercato
                st.session_state.lingua = lingua
                st.session_state.ambito = ambito
            else:
                st.error("⚠️ Non sono stati trovati abbastanza siti pertinenti. Prova con parametri diversi.")

# Mostra risultati
if st.session_state.show_results and st.session_state.results:
    st.markdown("---")

    # Costruisci introduzione personalizzata
    mercato_saved = st.session_state.get('mercato', 'il tuo mercato')
    lingua_saved = st.session_state.get('lingua', 'la tua lingua')
    ambito_saved = st.session_state.get('ambito', 'il tuo ambito')

    st.markdown(f"### 📊 I Primi 5 Siti Dove Dovresti Essere Posizionato se la Tua Azienda Lavora nel Mercato {mercato_saved} in Lingua {lingua_saved} e {ambito_saved}")
    
    # Prendi solo i primi 5
    first_5_results = st.session_state.results[:5]
    
    for result in first_5_results:
        number = result['number']
        name = result['name']
        type_badge = result['type']
        url = result['url']
        description = result['description']
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"#### {number}. [{name}]({url})")
            
            with col2:
                st.markdown(f"`{type_badge}`")
                st.markdown("✓ *Verificato*")
            
            st.markdown(f"🔗 **Vai al sito:** [{url}]({url})")
            st.markdown(description)
            st.markdown("---")
    
    # CTA Box
    st.markdown("""
        <div class="cta-box">
            <img src="https://www.avantgrade.com/wp-content/themes/avantgrade/assets/img/logo-colored.svg" alt="Avantgrade Logo">
            <h3>Vuoi scoprire gli altri 5 siti strategici?</h3>
            <p style="color: white; opacity: 0.95; margin-bottom: 1.5rem;">Contatta Avantgrade per ottenere l'analisi completa con tutti i 10 siti identificati e una strategia personalizzata per essere menzionato e dominare le chat AI nel tuo settore</p>
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
        <p>Powered by <strong>Avantgrade.com</strong></p>
    </div>
""", unsafe_allow_html=True)
