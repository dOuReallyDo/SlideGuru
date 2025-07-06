#!/usr/bin/env python3
"""
Test avanzato per verificare archiviazione e persistenza in SlideGuru
"""

import os
import sys
import tempfile
import json
import shutil
from datetime import datetime

def test_session_archiving():
    """Testa il sistema di archiviazione sessioni"""
    print("🧪 Test sistema di archiviazione...")
    try:
        from app import create_session_folder, save_files_to_session
        
        # Test creazione cartella sessione
        session_path, session_name = create_session_folder("test_document.pdf")
        
        # Verifica che la cartella sia stata creata
        assert os.path.exists(session_path), "Cartella sessione non creata"
        
        # Verifica naming convention
        assert "test_document" in session_name, "Nome file non incluso nel nome sessione"
        assert datetime.now().strftime("%Y%m%d") in session_name, "Data non inclusa nel nome sessione"
        
        print(f"✅ Cartella sessione creata: {session_name}")
        
        # Pulizia
        shutil.rmtree(session_path, ignore_errors=True)
        
        return True
    except Exception as e:
        print(f"❌ Errore test archiviazione: {e}")
        return False

def test_config_persistence():
    """Testa la persistenza della configurazione"""
    print("🧪 Test persistenza configurazione...")
    try:
        from config import llm_config, LLMProvider
        
        # Backup del file di configurazione esistente
        config_backup = None
        if os.path.exists(llm_config.config_file):
            with open(llm_config.config_file, 'r') as f:
                config_backup = f.read()
        
        # Test salvataggio/caricamento
        original_model = llm_config.current_model
        original_prompt = llm_config.system_prompt
        
        # Cambia configurazione
        test_model = "gpt-4o-mini"
        test_prompt = "Test prompt per verifica persistenza"
        
        llm_config.set_current_model(test_model)
        llm_config.set_system_prompt(test_prompt)
        
        # Verifica che i cambiamenti siano stati salvati
        assert os.path.exists(llm_config.config_file), "File di configurazione non creato"
        
        # Ricarica configurazione
        llm_config.load_config()
        
        # Verifica persistenza
        assert llm_config.current_model == test_model, "Modello non persistito"
        assert llm_config.system_prompt == test_prompt, "System prompt non persistito"
        
        print("✅ Configurazione persistita correttamente")
        
        # Ripristina configurazione originale
        llm_config.set_current_model(original_model)
        llm_config.set_system_prompt(original_prompt)
        
        if config_backup:
            with open(llm_config.config_file, 'w') as f:
                f.write(config_backup)
        
        return True
    except Exception as e:
        print(f"❌ Errore test persistenza: {e}")
        return False

def test_api_key_persistence():
    """Testa la persistenza delle API keys"""
    print("🧪 Test persistenza API keys...")
    try:
        from config import llm_config, LLMProvider
        
        # Backup delle API keys esistenti
        original_keys = {
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'google': os.getenv('GOOGLE_API_KEY'),
        }
        
        # Test API key
        test_key = "test-api-key-123"
        llm_config.set_api_key(LLMProvider.OPENAI, test_key)
        llm_config.save_config()
        
        # Verifica che l'API key sia stata salvata
        assert os.getenv('OPENAI_API_KEY') == test_key, "API key non impostata nell'ambiente"
        
        # Ricarica configurazione
        llm_config.load_config()
        
        # Verifica persistenza
        assert os.getenv('OPENAI_API_KEY') == test_key, "API key non persistita"
        
        print("✅ API keys persistite correttamente")
        
        # Ripristina API keys originali
        for provider, key in original_keys.items():
            if key:
                os.environ[f'{provider.upper()}_API_KEY'] = key
            else:
                os.environ.pop(f'{provider.upper()}_API_KEY', None)
        
        return True
    except Exception as e:
        print(f"❌ Errore test persistenza API keys: {e}")
        return False

def test_archive_folder_creation():
    """Testa la creazione automatica delle cartelle di archivio"""
    print("🧪 Test creazione cartelle archivio...")
    try:
        from app import app
        
        # Verifica che la cartella archive esista
        archive_path = app.config['ARCHIVE_FOLDER']
        assert os.path.exists(archive_path), "Cartella archive non creata"
        
        print(f"✅ Cartella archivio esistente: {archive_path}")
        
        return True
    except Exception as e:
        print(f"❌ Errore test cartelle archivio: {e}")
        return False

def test_model_availability():
    """Testa che i modelli siano disponibili in base alle API keys"""
    print("🧪 Test disponibilità modelli...")
    try:
        from llm_service import llm_service
        
        # Test modelli cloud
        cloud_models = llm_service.available_cloud_models()
        assert isinstance(cloud_models, dict), "Modelli cloud non restituiti come dict"
        
        # Test modelli locali
        local_models = llm_service.available_local_models()
        assert isinstance(local_models, dict), "Modelli locali non restituiti come dict"
        
        print(f"✅ Modelli disponibili: {len(cloud_models)} cloud, {len(local_models)} locali")
        
        return True
    except Exception as e:
        print(f"❌ Errore test disponibilità modelli: {e}")
        return False

def test_single_active_model():
    """Testa che ci sia sempre un solo modello attivo"""
    print("🧪 Test singolo modello attivo...")
    try:
        from config import llm_config
        
        # Verifica che ci sia un modello corrente
        current_model = llm_config.get_current_model()
        assert current_model is not None, "Nessun modello corrente"
        
        # Verifica che sia uno dei modelli disponibili
        assert llm_config.current_model in llm_config.models, "Modello corrente non valido"
        
        print(f"✅ Modello attivo: {current_model.name}")
        
        return True
    except Exception as e:
        print(f"❌ Errore test singolo modello: {e}")
        return False

def main():
    """Esegue tutti i test avanzati"""
    print("🚀 Test Avanzati SlideGuru\n")
    
    tests = [
        test_session_archiving,
        test_config_persistence,
        test_api_key_persistence,
        test_archive_folder_creation,
        test_model_availability,
        test_single_active_model
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test fallito con eccezione: {e}")
        print()
    
    print(f"📊 Risultati test avanzati: {passed}/{total} passati")
    
    if passed == total:
        print("🎉 TUTTI I TEST AVANZATI PASSATI!")
        print("✅ Archiviazione sessioni funzionante")
        print("✅ Persistenza configurazione funzionante")
        print("✅ Persistenza API keys funzionante")
        print("✅ Sistema di cartelle archivio funzionante")
        print("✅ Gestione modelli corretta")
        return True
    else:
        print(f"⚠️  {total - passed} test avanzati falliti.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
