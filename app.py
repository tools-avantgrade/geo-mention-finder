import streamlit as st
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from datetime import datetime
import re
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

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
        <h1>🎯 Site Mention Analyzer</h1>
        <p>Scopri dove il tuo brand deve essere menzionato per massimizzare la visibilità su Gemini AI</p>
    </div>
""", unsafe_allow_html=True)

# Info box
st.markdown("""
    <div class="info-box">
        <p><strong>💡 Come funziona:</strong> Inserisci il tuo settore, ambito e lingua per scoprire i 10 principali siti informativi e canali dove dovresti essere presente, con link diretti ad articoli pertinenti.</p>
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

# Funzione per pulire il testo da markdown
def clean_markdown(text):
    """Rimuove markdown e caratteri speciali dal testo"""
    if not text:
        return text
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)
    text = re.sub(r'_([^_]+)_', r'\1', text)
    return text.strip()

# Funzione per ottenere il dominio da un nome sito
def extract_domain_from_sitename(site_name):
    """Cerca il dominio del sito usando ricerca web simulata"""
    try:
        # Prova a cercare con requests
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Cerca su Google
        query = f"{site_name} sito ufficiale"
        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        response = requests.get(google_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca il primo link nei risultati
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if '/url?q=' in href:
                    url = href.split('/url?q=')[1].split('&')[0]
                    parsed = urlparse(url)
                    if parsed.netloc and 'google' not in parsed.netloc:
                        return parsed.netloc
        
        return None
    except:
        return None

# Funzione per cercare articolo specifico su un sito
def search_article_on_site(site_name, domain, mercato, ambito):
    """Cerca un articolo specifico su un sito usando ricerca web REALE"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Costruisci query con site operator
        if domain:
            query = f"site:{domain} {mercato} {ambito}"
        else:
            query = f"{site_name} {mercato} {ambito}"
        
        google_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        
        response = requests.get(google_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Cerca il primo risultato reale
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if '/url?q=' in href:
                    url = href.split('/url?q=')[1].split('&')[0]
                    
                    # Verifica che sia un URL valido
                    if url.startswith('http') and 'google.com' not in url:
                        # Verifica che il dominio corrisponda se disponibile
                        if domain:
                            if domain in url:
                                return url
                        else:
                            return url
        
        # Fallback: homepage del sito
        if domain:
            return f"https://{domain}"
        
        return None
        
    except Exception as e:
        print(f"Errore ricerca articolo per {site_name}: {str(e)}")
        return None

# Funzione per parsare i risultati (solo nomi siti)
def parse_results(text):
    """Parsa i risultati in una struttura dati"""
    results = []
    lines = text.split('\n')
    current_result = None
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Cerca pattern numero. Nome - Tipo
        match = re.match(r'^(\d+)\.\s*\*?\*?(.+?)\*?\*?\s*-\s*(.+)$', line)
        if match:
            if current_result:
                results.append(current_result)
            
            name = clean_markdown(match.group(2).strip())
            type_text = clean_markdown(match.group(3).strip())
            
            current_result = {
                'number': match.group(1),
                'name': name,
                'type': type_text,
                'url': '',
                'description': []
            }
            i += 1
            continue
        
        if current_result:
            if not line:
                i += 1
                continue
            
            if not re.match(r'^\d+\.', line) and not line.startswith('http'):
                cleaned_line = clean_markdown(line)
                current_result['description'].append(cleaned_line)
        
        i += 1
    
    if current_result:
        results.append(current_result)
    
    return results

# Funzione per trovare articoli REALI per ogni sito
def find_real_articles(results, mercato, ambito, progress_bar=None):
    """Trova articoli REALI usando ricerca web"""
    total = len(results)
    
    for idx, result in enumerate(results):
        if progress_bar:
            progress_bar.progress((idx + 1) / total, text=f"🔍 Ricerca articoli reali {idx + 1}/{total}: {result['name']}")
        
        # Prima trova il dominio del sito
        domain = extract_domain_from_sitename(result['name'])
        
        # Poi cerca un articolo specifico
        article_url = search_article_on_site(result['name'], domain, mercato, ambito)
        
        if article_url:
            result['url'] = article_url
        else:
            # Ultimo fallback
            result['url'] = f"https://www.google.com/search?q={result['name'].replace(' ', '+')}"
    
    return results

# Funzione per chiamare Gemini (solo per nomi siti)
def get_gemini_suggestions(mercato, ambito, lingua):
    try:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        models_to_try = [
            'gemini-2.0-flash-exp',
            'gemini-exp-1206',
            'gemini-1.5-pro-latest',
            'gemini-1.5-flash-latest',
        ]
        
        model = None
        
        for model_name in models_to_try:
            try:
                model = genai.GenerativeModel(model_name)
                break
            except:
                continue
        
        if model is None:
            return "❌ Errore: Nessun modello Gemini disponibile"
        
        prompt = f"""Sei un esperto di GEO (Generative Engine Optimization) e visibilità digitale.

Un'azienda opera nel settore: {mercato}
Ambito specifico: {ambito}
Lingua: {lingua}

Identifica i 10 siti web informativi, portali, blog e canali YouTube più autorevoli dove questa azienda DEVE essere menzionata per massimizzare la visibilità su Gemini AI.

IMPORTANTE:
- Fornisci SOLO il nome del sito e la tipologia
- NON inventare URL
- Escludi siti istituzionali (.gov, .edu)
- NON usare formattazione markdown

Formatta ESATTAMENTE così:

1. Nome Esatto del Sito - Tipologia
Spiegazione di 2-3 righe sul perché questo sito è strategico

2. Nome Esatto del Sito - Tipologia
Spiegazione...

Continua per tutti i 10 siti. USA SOLO nomi di siti REALI."""

        generation_config = genai.types.GenerationConfig(
            temperature=0.7,
            top_p=0.95,
            max_output_tokens=3000,
        )
        
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        if response and hasattr(response, 'text') and response.text:
            return response.text
        elif response and hasattr(response, 'parts') and response.parts:
            return ''.join(part.text for part in response.parts if hasattr(part, 'text'))
        
        return "❌ Errore: Nessuna risposta"
        
    except Exception as e:
        return f"❌ Errore: {str(e)}"

# Processo di analisi
if analyze_button:
    if not mercato or not ambito or not lingua:
        st.error("⚠️ Per favore compila tutti i campi")
    else:
        with st.spinner("🔄 Sto identificando i siti più strategici..."):
            result = get_gemini_suggestions(mercato, ambito, lingua)
            
            if not result.startswith("❌"):
                parsed_results = parse_results(result)
                
                if len(parsed_results) >= 5:
                    # Ora cerca articoli REALI per ogni sito
                    progress_placeholder = st.empty()
                    progress_bar = progress_placeholder.progress(0, text="🔍 Ricerca articoli reali...")
                    
                    verified_results = find_real_articles(parsed_results, mercato, ambito, progress_bar)
                    
                    progress_placeholder.empty()
                    
                    st.session_state.results = verified_results
                    st.session_state.show_results = True
                else:
                    st.error("⚠️ Non sono stati trovati abbastanza siti pertinenti.")
            else:
                st.error(result)

# Mostra risultati
if st.session_state.show_results and st.session_state.results:
    st.markdown("---")
    st.markdown("### 📊 I Primi 5 Siti Strategici Identificati")
    
    first_5_results = st.session_state.results[:5]
    
    for result in first_5_results:
        number = result['number']
        name = result['name']
        type_badge = result['type']
        url = result['url']
        description = ' '.join(result['description'])
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            
            with col1:
                st.markdown(f"#### {number}. [{name}]({url})")
            
            with col2:
                st.markdown(f"`{type_badge}`")
                if 'google.com/search' not in url:
                    st.markdown("📄 *Articolo*")
            
            st.markdown(f"🔗 [{url}]({url})")
            st.markdown(description)
            st.markdown("---")
    
    # CTA Box
    st.markdown("""
        <div class="cta-box">
            <img src="https://www.avantgrade.com/wp-content/themes/avantgrade/assets/img/logo-colored.svg" alt="Avantgrade Logo">
            <h3>Vuoi scoprire gli altri 5 siti strategici?</h3>
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
