#!/usr/bin/env python3
"""
Test script per verificare che SlideGuru MVP sia completamente funzionale
"""

import os
import sys
import tempfile
import json

def test_imports():
    """Testa che tutti i moduli si importino correttamente"""
    print("🧪 Test import moduli...")
    try:
        import config
        import llm_service  
        import app
        print("✅ Tutti i moduli importati correttamente")
        return True
    except Exception as e:
        print(f"❌ Errore import: {e}")
        return False

def test_config_loading():
    """Testa il caricamento della configurazione"""
    print("🧪 Test configurazione...")
    try:
        from config import llm_config
        
        # Verifica che abbia modelli definiti
        assert len(llm_config.models) > 0, "Nessun modello definito"
        print(f"✅ Configurazione caricata: {len(llm_config.models)} modelli disponibili")
        
        # Verifica che abbia un modello corrente valido
        current = llm_config.get_current_model()
        assert current is not None, "Nessun modello corrente"
        print(f"✅ Modello corrente: {current.name}")
        
        # Verifica system prompt
        prompt = llm_config.get_system_prompt()
        assert len(prompt) > 0, "System prompt vuoto"
        print(f"✅ System prompt configurato ({len(prompt)} caratteri)")
        
        return True
    except Exception as e:
        print(f"❌ Errore configurazione: {e}")
        return False

def test_llm_service():
    """Testa il servizio LLM"""
    print("🧪 Test servizio LLM...")
    try:
        from llm_service import llm_service
        
        # Verifica che il servizio si inizializzi
        assert llm_service is not None, "Servizio LLM non inizializzato"
        print("✅ Servizio LLM inizializzato")
        
        # Verifica metodi disponibili
        methods = ['generate_content', 'available_cloud_models', 'available_local_models']
        for method in methods:
            assert hasattr(llm_service, method), f"Metodo {method} mancante"
        print("✅ Tutti i metodi del servizio presenti")
        
        return True
    except Exception as e:
        print(f"❌ Errore servizio LLM: {e}")
        return False

def test_file_processing():
    """Testa l'elaborazione dei file"""
    print("🧪 Test elaborazione file...")
    try:
        from app import extract_text_from_file, generate_slide_content
        
        # Crea un file di test temporaneo
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            test_content = "Questo è un test di SlideGuru. Il contenuto dovrebbe essere elaborato correttamente."
            f.write(test_content)
            temp_file = f.name
        
        try:
            # Testa estrazione testo
            extracted = extract_text_from_file(temp_file)
            assert extracted == test_content, "Estrazione testo fallita"
            print("✅ Estrazione testo da file funzionante")
            
            # Testa generazione slide (senza LLM effettivo)
            # Questo testerà la logica di parsing
            slides = generate_slide_content(test_content)
            assert isinstance(slides, list), "Le slide devono essere una lista"
            assert len(slides) > 0, "Nessuna slide generata"
            assert all('title' in slide and 'content' in slide for slide in slides), "Formato slide non valido"
            print(f"✅ Generazione slide funzionante ({len(slides)} slide create)")
            
        finally:
            os.unlink(temp_file)
        
        return True
    except Exception as e:
        print(f"❌ Errore elaborazione file: {e}")
        return False

def test_template_exists():
    """Testa che il template PowerPoint esista"""
    print("🧪 Test template PowerPoint...")
    try:
        template_path = os.path.join('static', 'template.pptx')
        assert os.path.exists(template_path), f"Template non trovato: {template_path}"
        print(f"✅ Template PowerPoint trovato: {template_path}")
        return True
    except Exception as e:
        print(f"❌ Errore template: {e}")
        return False

def test_flask_app():
    """Testa che l'app Flask si inizializzi"""
    print("🧪 Test applicazione Flask...")
    try:
        from app import app
        
        # Verifica che l'app si inizializzi
        assert app is not None, "App Flask non inizializzata"
        print("✅ App Flask inizializzata")
        
        # Verifica route principali
        with app.test_client() as client:
            response = client.get('/')
            assert response.status_code == 200, f"Homepage non raggiungibile: {response.status_code}"
            print("✅ Homepage raggiungibile")
            
            response = client.get('/config')
            assert response.status_code == 200, f"Pagina config non raggiungibile: {response.status_code}"
            print("✅ Pagina configurazione raggiungibile")
        
        return True
    except Exception as e:
        print(f"❌ Errore app Flask: {e}")
        return False

def main():
    """Esegue tutti i test"""
    print("🚀 Test MVP SlideGuru\n")
    
    tests = [
        test_imports,
        test_config_loading,
        test_llm_service,
        test_file_processing,
        test_template_exists,
        test_flask_app
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
    
    print(f"📊 Risultati test: {passed}/{total} passati")
    
    if passed == total:
        print("🎉 TUTTI I TEST PASSATI! SlideGuru MVP è completamente funzionale!")
        print("\n🚀 Per avviare l'applicazione:")
        print("   python app.py")
        print("\n🌐 Poi vai su: http://localhost:8080")
        return True
    else:
        print(f"⚠️  {total - passed} test falliti. Verifica gli errori sopra.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
