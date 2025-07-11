#!/usr/bin/env python3
"""
Test specifico per modelli locali multipli con endpoint diversi
"""

import requests
from llm_service import llm_service
from config import llm_config

def test_multiple_endpoints():
    """Testa il rilevamento di modelli su endpoint multipli"""
    print("🔍 Test rilevamento modelli locali multipli")
    
    # Configura gli endpoint per LM Studio
    llm_config.local_backend = "lmstudio"
    
    # Test endpoint principale
    print(f"📡 Test endpoint principale: {llm_config.local_endpoint}")
    try:
        response = requests.get(f"{llm_config.local_endpoint}/v1/internal/model/all", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"✅ Endpoint {llm_config.local_endpoint}: {len(models)} modelli trovati")
            for model in models:
                print(f"   📋 {model['modelId']}")
        else:
            print(f"❌ Endpoint {llm_config.local_endpoint}: non raggiungibile (status {response.status_code})")
    except Exception as e:
        print(f"❌ Endpoint {llm_config.local_endpoint}: errore {e}")
    
    # Test endpoint secondario
    secondary_endpoint = "http://192.168.68.130:1234"
    print(f"📡 Test endpoint secondario: {secondary_endpoint}")
    try:
        response = requests.get(f"{secondary_endpoint}/v1/internal/model/all", timeout=5)
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"✅ Endpoint {secondary_endpoint}: {len(models)} modelli trovati")
            for model in models:
                print(f"   📋 {model['modelId']}")
        else:
            print(f"❌ Endpoint {secondary_endpoint}: non raggiungibile (status {response.status_code})")
    except Exception as e:
        print(f"❌ Endpoint {secondary_endpoint}: errore {e}")
    
    # Test modelli aggregati
    print("\n🔄 Test modelli aggregati tramite available_local_models()")
    available_models = llm_service.available_local_models()
    print(f"📊 Totale modelli locali rilevati: {len(available_models)}")
    
    for model_id, model_config in available_models.items():
        print(f"✅ {model_id}: {model_config.name} su {model_config.base_url}")
    
    return len(available_models)

def test_ollama_endpoints():
    """Testa il rilevamento di modelli Ollama"""
    print("\n🦙 Test rilevamento modelli Ollama")
    
    # Configura gli endpoint per Ollama
    original_backend = llm_config.local_backend
    llm_config.local_backend = "ollama"
    
    # Test endpoint principale
    print(f"📡 Test endpoint Ollama: {llm_config.local_endpoint}")
    try:
        response = requests.get(f"{llm_config.local_endpoint}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Endpoint Ollama: {len(models)} modelli trovati")
            for model in models:
                print(f"   🦙 {model['name']}")
        else:
            print(f"❌ Endpoint Ollama: non raggiungibile (status {response.status_code})")
    except Exception as e:
        print(f"❌ Endpoint Ollama: errore {e}")
    
    # Ripristina configurazione originale
    llm_config.local_backend = original_backend
    
    return True

if __name__ == "__main__":
    print("🚀 Test Modelli Locali Multipli\n")
    
    print("🔧 Configurazione attuale:")
    print(f"Backend: {llm_config.local_backend}")
    print(f"Endpoint: {llm_config.local_endpoint}")
    print(f"Endpoint configurati: {llm_config.local_endpoints}")
    print()
    
    # Test LM Studio multipli
    models_found = test_multiple_endpoints()
    
    # Test Ollama
    test_ollama_endpoints()
    
    print(f"\n📊 Risultato finale: {models_found} modelli locali disponibili")
    
    if models_found > 0:
        print("🎉 Sistema di endpoint multipli funzionante!")
    else:
        print("⚠️  Nessun modello locale rilevato. Verificare:")
        print("   - Che i server locali siano attivi")
        print("   - Che gli endpoint siano corretti")
        print("   - Che ci siano modelli caricati")
