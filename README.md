# SlideGuru

SlideGuru è un'applicazione Flask per generare presentazioni PowerPoint (.pptx) a partire da uno o più documenti (PDF, DOCX, TXT) usando modelli LLM cloud (OpenAI, Anthropic, Google) o locali (Ollama, LM Studio).

## ✨ Funzionalità principali

- **🔧 Configurazione sempre sincronizzata**: ogni scelta fatta dall'utente (modello, backend locale, endpoint, parametri) viene salvata e usata realmente dal backend
- **📊 Sezione impostazioni attuali**: la pagina di configurazione mostra sempre i parametri effettivi in uso, letti dal file di configurazione
- **💾 Persistenza reale**: tutte le modifiche sono storicizzate e usate per la generazione delle slide
- **📁 Upload multiplo**: puoi caricare più file contemporaneamente, che verranno sintetizzati in un'unica presentazione
- **🏠 Supporto multi-backend locale**: Ollama e LM Studio con endpoint configurabili
- **🔑 Gestione API key cloud**: solo i modelli per cui è presente una chiave API valida sono selezionabili
- **🎯 System prompt personalizzabile**: personalizza il comportamento di SlideGuru modificando il prompt di sistema
- **🛡️ Gestione errori robusta**: logging completo e recupero intelligente dai fallimenti

## 🚀 Avvio rapido

### Prerequisiti

- Python 3.8+ (testato con Python 3.12)
- pip

### Installazione

1. **Clona il repository**:
```bash
git clone https://github.com/dOuReallyDo/SlideGuru.git
cd SlideGuru
```

2. **Installa le dipendenze**:
```bash
pip install -r requirements.txt
```

3. **Configura le variabili d'ambiente** (opzionale per modelli cloud):
```bash
cp .env.example .env
# Modifica .env con le tue chiavi API
```

4. **Avvia l'applicazione**:
```bash
python app.py
```

5. **Apri il browser** su `http://localhost:8080`

## 🔧 Configurazione

### Modelli Cloud

SlideGuru supporta i seguenti provider cloud:

#### OpenAI
- **Modelli**: GPT-4o, GPT-4o Mini, GPT-3.5 Turbo
- **Chiave API**: [Ottieni qui](https://platform.openai.com/api-keys)
- **Variabile**: `OPENAI_API_KEY`

#### Anthropic
- **Modelli**: Claude 3.5 Sonnet, Claude 3 Haiku
- **Chiave API**: [Ottieni qui](https://console.anthropic.com/settings/keys)
- **Variabile**: `ANTHROPIC_API_KEY`

#### Google Gemini
- **Modelli**: Gemini 1.5 Pro, Gemini 1.5 Flash
- **Chiave API**: [Ottieni qui](https://makersuite.google.com/app/apikey)
- **Variabile**: `GOOGLE_API_KEY`

### Modelli Locali

#### Ollama
1. **Installa Ollama**: [https://ollama.ai](https://ollama.ai)
2. **Scarica un modello**:
```bash
ollama pull llama3.1:8b
# oppure
ollama pull mistral:7b
```
3. **Configura l'endpoint** in SlideGuru (default: `http://localhost:11434`)

#### LM Studio
1. **Installa LM Studio**: [https://lmstudio.ai](https://lmstudio.ai)
2. **Scarica e carica un modello**
3. **Avvia il server locale** in LM Studio
4. **Configura l'endpoint** in SlideGuru (default: `http://localhost:1234`)

## 📖 Come funziona

1. **Vai alla configurazione** (`/config`) per impostare i tuoi modelli preferiti
2. **Configura le chiavi API** per i provider cloud che vuoi usare
3. **Testa le connessioni** per verificare che tutto funzioni
4. **Personalizza il system prompt** per adattare SlideGuru alle tue esigenze
5. **Torna alla home** e carica uno o più documenti
6. **Scarica la presentazione** generata automaticamente

## 🏗️ Architettura

```
SlideGuru/
├── app.py                 # Applicazione Flask principale
├── config.py              # Configurazione modelli LLM
├── llm_service.py         # Servizio per comunicazione con LLM
├── requirements.txt       # Dipendenze Python
├── .env.example          # Template variabili d'ambiente
├── static/
│   └── template.pptx     # Template PowerPoint base
├── templates/
│   ├── index.html        # Pagina principale
│   ├── config.html       # Pagina configurazione
│   └── 500.html          # Pagina errore
├── uploads/              # File caricati e generati
└── logs/                 # Log dell'applicazione
```

## 🔧 API Endpoints

### Configurazione
- `GET /config` - Pagina di configurazione
- `POST /api/set_api_key` - Imposta chiave API
- `POST /api/test_connection` - Testa connessione provider
- `POST /api/set_model` - Seleziona modello corrente
- `POST /api/set_local_backend` - Configura backend locale
- `GET /api/get_config` - Ottieni configurazione attuale

### System Prompt
- `GET /api/get_system_prompt` - Ottieni prompt di sistema
- `POST /api/set_system_prompt` - Imposta prompt di sistema

### Modelli
- `POST /api/list_models` - Lista modelli disponibili
- `GET /api/refresh_models` - Aggiorna lista modelli

## 🛠️ Sviluppo

### Struttura del codice

- **config.py**: Gestisce la configurazione dei modelli e le impostazioni persistenti
- **llm_service.py**: Interfaccia unificata per tutti i provider LLM
- **app.py**: Logica dell'applicazione web e routing Flask

### Aggiungere un nuovo provider

1. Aggiungi il provider all'enum `LLMProvider` in `config.py`
2. Implementa i metodi `_generate_[provider]` in `llm_service.py`
3. Aggiungi la sezione UI in `templates/config.html`

### Logging

I log sono salvati in `logs/app.log` con rotazione automatica. Livello di default: ERROR.

## 🐛 Risoluzione problemi

### "Modello non trovato"
- Verifica che il modello sia disponibile nel provider selezionato
- Per Ollama: `ollama list` per vedere i modelli installati
- Per LM Studio: verifica che il modello sia caricato e il server attivo

### "Client non inizializzato"
- Verifica che la chiave API sia configurata correttamente
- Usa il pulsante "Test" nella pagina di configurazione

### "Endpoint non raggiungibile"
- Per Ollama: verifica che il servizio sia attivo (`ollama serve`)
- Per LM Studio: verifica che il server locale sia avviato
- Controlla che l'endpoint sia corretto

### Errori di parsing JSON
- SlideGuru gestisce automaticamente le risposte non JSON
- Il contenuto viene mostrato in forma grezza se il parsing fallisce

## 📝 Formati supportati

### Input
- **PDF**: Estrazione testo tramite PyMuPDF
- **DOCX**: Estrazione tramite python-docx
- **TXT**: Lettura diretta

### Output
- **PPTX**: Presentazione PowerPoint con template personalizzabile

## 🔒 Sicurezza

- Le chiavi API sono memorizzate solo nelle variabili d'ambiente
- I file caricati sono gestiti in modo sicuro
- Validazione estensioni file
- Logging degli errori per debug

## 🤝 Contribuire

1. Fork del repository
2. Crea un branch per la tua feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## 📄 Licenza

Questo progetto è distribuito sotto licenza MIT. Vedi `LICENSE` per maggiori dettagli.

## 🔗 Link utili

- **Repository**: https://github.com/dOuReallyDo/SlideGuru
- **Issues**: https://github.com/dOuReallyDo/SlideGuru/issues
- **Ollama**: https://ollama.ai
- **LM Studio**: https://lmstudio.ai

## 📞 Supporto

Se hai problemi o domande:

1. Controlla la sezione "Risoluzione problemi"
2. Cerca negli Issues esistenti
3. Crea un nuovo Issue se necessario

---

*Sviluppato con ❤️ per semplificare la creazione di presentazioni professionali*
