# SlideGuru

SlideGuru è un'applicazione Flask per generare presentazioni PowerPoint (.pptx) a partire da uno o più documenti (PDF, DOCX, TXT) usando modelli LLM cloud (OpenAI, Anthropic, Google) o locali (Ollama, LM Studio).

## Funzionalità principali

- **Configurazione sempre sincronizzata**: ogni scelta fatta dall'utente (modello, backend locale, endpoint, parametri) viene salvata e usata realmente dal backend.
- **Sezione impostazioni attuali**: la pagina di configurazione mostra sempre i parametri effettivi in uso, letti dal file di configurazione.
- **Persistenza reale**: tutte le modifiche sono storicizzate e usate per la generazione delle slide.
- **Upload multiplo**: puoi caricare più file contemporaneamente, che verranno sintetizzati in un'unica presentazione.
- **Supporto multi-backend locale**: puoi scegliere tra Ollama e LM Studio e impostare l'endpoint desiderato.
- **Gestione API key cloud**: solo i modelli per cui è presente una chiave API valida sono selezionabili; se manca la key viene mostrato il link ufficiale per ottenerla.

## Come funziona

1. **Configura i modelli** nella pagina di configurazione (`/config`).
2. **Le scelte sono sempre persistenti**: ogni selezione aggiorna il file di configurazione e viene usata per tutte le generazioni successive.
3. **Carica uno o più file** dalla home page: verranno uniti e sintetizzati in slide usando il modello e i parametri attuali.
4. **Scarica la presentazione** pronta e modificabile in PowerPoint.

## Note tecniche
- Tutte le API di configurazione sono RESTful e la UI si aggiorna sempre leggendo lo stato reale dal backend.
- Il file di configurazione `llm_config.json` tiene traccia di tutte le scelte e parametri.
- L'app è pronta per essere estesa con nuovi modelli o backend.

## Avvio rapido
```bash
python app.py
```

## Requisiti
- Python 3.12+
- Flask, python-pptx, fitz, openai, anthropic, google-generativeai, ecc.

## Repository
https://github.com/dOuReallyDo/SlideGuru 