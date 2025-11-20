# 🎯 GEO Mention Finder

Strumento di lead generation sviluppato da Avantgrade per identificare i siti web e canali più rilevanti dove essere menzionati per migliorare la visibilità su Gemini AI.

## 🚀 Setup

1. Clona il repository
2. Installa le dipendenze:
```bash
pip install -r requirements.txt
```

3. Configura i secrets di Streamlit:
Crea il file `.streamlit/secrets.toml` e aggiungi:
```toml
GEMINI_API_KEY = "your-api-key-here"
```

4. Avvia l'applicazione:
```bash
streamlit run app.py
```

## 🔑 Configurazione API Key

Per ottenere la tua API key di Gemini:
1. Vai su [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Crea una nuova API key
3. Aggiungila ai secrets di Streamlit

## 📦 Deploy su Streamlit Cloud

1. Pusha il codice su GitHub
2. Vai su [share.streamlit.io](https://share.streamlit.io)
3. Connetti il repository
4. Aggiungi il secret `GEMINI_API_KEY` nelle impostazioni dell'app

## 💼 Utilizzo

1. Inserisci il mercato/settore (es. "Logistica, Baie di carico")
2. Specifica l'ambito (es. "Soluzioni per magazzini")
3. Indica la lingua (es. "Italiano")
4. Clicca su "Analizza ora"
5. Visualizza i primi 5 risultati strategici
6. Contatta Avantgrade per l'analisi completa

## 🎨 Features

- ✅ Interfaccia professionale con branding Avantgrade
- ✅ Integrazione con Gemini AI (modello Flash per costi ottimizzati)
- ✅ Lead generation integrato con CTA
- ✅ Responsive design
- ✅ UTM tracking per analytics
- ✅ Embedding-ready per sito web

## 📄 Licenza

© 2024 Avantgrade.com - All rights reserved
