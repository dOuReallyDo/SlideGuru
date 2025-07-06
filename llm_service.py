import json
import requests
from typing import Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic
import google.generativeai as genai
from config import LLMProvider, llm_config

class LLMService:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.google_model = None
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Inizializza i client per le diverse API"""
        # OpenAI
        openai_key = llm_config.get_api_key(LLMProvider.OPENAI)
        if openai_key:
            self.openai_client = OpenAI(api_key=openai_key)
        
        # Anthropic
        anthropic_key = llm_config.get_api_key(LLMProvider.ANTHROPIC)
        if anthropic_key:
            self.anthropic_client = Anthropic(api_key=anthropic_key)
        
        # Google
        google_key = llm_config.get_api_key(LLMProvider.GOOGLE)
        if google_key:
            genai.configure(api_key=google_key)
    
    def generate_content(self, prompt: str, model_id: Optional[str] = None) -> str:
        """Genera contenuto usando il modello specificato o quello corrente"""
        if model_id is None:
            model_id = llm_config.current_model
        
        model_config = llm_config.models.get(model_id)
        if not model_config:
            raise ValueError(f"Modello {model_id} non trovato")
        
        # Prepara il prompt finale con il system prompt
        system_prompt = llm_config.get_system_prompt()
        full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            if model_config.provider == LLMProvider.OPENAI:
                return self._generate_openai(full_prompt, model_config)
            elif model_config.provider == LLMProvider.ANTHROPIC:
                return self._generate_anthropic(full_prompt, model_config)
            elif model_config.provider == LLMProvider.GOOGLE:
                return self._generate_google(full_prompt, model_config)
            elif model_config.provider == LLMProvider.LOCAL:
                return self._generate_local(full_prompt, model_config)
            else:
                raise ValueError(f"Provider {model_config.provider} non supportato")
        except Exception as e:
            raise Exception(f"Errore nella generazione del contenuto: {str(e)}")
    
    def _generate_openai(self, prompt: str, model_config) -> str:
        """Genera contenuto usando OpenAI"""
        if not self.openai_client:
            raise Exception("Client OpenAI non inizializzato. Verifica la chiave API.")
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model_config.name,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Errore OpenAI: {str(e)}")
    
    def _generate_anthropic(self, prompt: str, model_config) -> str:
        """Genera contenuto usando Anthropic"""
        if not self.anthropic_client:
            raise Exception("Client Anthropic non inizializzato. Verifica la chiave API.")
        
        try:
            response = self.anthropic_client.messages.create(
                model=model_config.name,
                max_tokens=model_config.max_tokens,
                temperature=model_config.temperature,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text
        except Exception as e:
            raise Exception(f"Errore Anthropic: {str(e)}")
    
    def _generate_google(self, prompt: str, model_config) -> str:
        """Genera contenuto usando Google Gemini"""
        try:
            model = genai.GenerativeModel(model_config.name)
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=model_config.max_tokens,
                    temperature=model_config.temperature
                )
            )
            return response.text
        except Exception as e:
            raise Exception(f"Errore Google: {str(e)}")
    
    def _generate_local(self, prompt: str, model_config) -> str:
        """Genera contenuto usando modelli locali (Ollama/LM Studio)"""
        try:
            # Usa l'endpoint configurato invece di base_url
            endpoint = llm_config.local_endpoint
            backend = llm_config.local_backend
            
            if backend == "ollama":
                response = requests.post(
                    f"{endpoint}/api/generate",
                    json={
                        "model": model_config.name,
                        "prompt": prompt,
                        "stream": False,
                        "options": {
                            "temperature": model_config.temperature,
                            "num_predict": model_config.max_tokens
                        }
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    raise Exception(f"Errore API Ollama: {response.status_code}")
            
            elif backend == "lmstudio":
                response = requests.post(
                    f"{endpoint}/v1/chat/completions",
                    json={
                        "model": model_config.name,
                        "messages": [{"role": "user", "content": prompt}],
                        "max_tokens": model_config.max_tokens,
                        "temperature": model_config.temperature
                    },
                    timeout=120
                )
                
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    raise Exception(f"Errore API LM Studio: {response.status_code}")
            
            else:
                raise Exception(f"Backend locale non supportato: {backend}")
                
        except Exception as e:
            raise Exception(f"Errore modello locale: {str(e)}")
    
    def test_connection(self, provider: LLMProvider) -> Dict[str, Any]:
        """Testa la connessione a un provider"""
        try:
            if provider == LLMProvider.OPENAI:
                if not self.openai_client:
                    return {"status": "error", "message": "Client OpenAI non inizializzato"}
                response = self.openai_client.models.list()
                return {"status": "success", "message": f"Connesso a OpenAI. Modelli disponibili: {len(response.data)}"}
            
            elif provider == LLMProvider.ANTHROPIC:
                if not self.anthropic_client:
                    return {"status": "error", "message": "Client Anthropic non inizializzato"}
                # Test semplice con Anthropic
                return {"status": "success", "message": "Connesso a Anthropic"}
            
            elif provider == LLMProvider.GOOGLE:
                try:
                    models = genai.list_models()
                    return {"status": "success", "message": f"Connesso a Google. Modelli disponibili: {len(list(models))}"}
                except:
                    return {"status": "error", "message": "Errore nella connessione a Google"}
            
            elif provider == LLMProvider.LOCAL:
                endpoint = llm_config.local_endpoint
                backend = llm_config.local_backend
                try:
                    if backend == "ollama":
                        response = requests.get(f"{endpoint}/api/tags", timeout=5)
                        if response.status_code == 200:
                            models = response.json().get("models", [])
                            return {"status": "success", "message": f"Connesso a Ollama. Modelli disponibili: {len(models)}"}
                        else:
                            return {"status": "error", "message": "Ollama non raggiungibile"}
                    elif backend == "lmstudio":
                        response = requests.get(f"{endpoint}/v1/internal/model/all", timeout=5)
                        if response.status_code == 200:
                            models = response.json().get("data", [])
                            return {"status": "success", "message": f"Connesso a LM Studio. Modelli disponibili: {len(models)}"}
                        else:
                            return {"status": "error", "message": "LM Studio non raggiungibile"}
                    else:
                        return {"status": "error", "message": f"Backend locale non supportato: {backend}"}
                except Exception as e:
                    return {"status": "error", "message": f"Errore connessione locale: {str(e)}"}
            
            else:
                return {"status": "error", "message": "Provider non supportato"}
        
        except Exception as e:
            return {"status": "error", "message": f"Errore nel test: {str(e)}"}
    
    def get_available_models(self, provider: LLMProvider) -> Dict[str, Any]:
        """Restituisce i modelli disponibili per un provider"""
        try:
            if provider == LLMProvider.OPENAI:
                if not self.openai_client:
                    return {"status": "error", "message": "Client OpenAI non inizializzato"}
                response = self.openai_client.models.list()
                models = [model.id for model in response.data if "gpt" in model.id]
                return {"status": "success", "models": models}
            
            elif provider == LLMProvider.LOCAL:
                endpoint = llm_config.local_endpoint
                backend = llm_config.local_backend
                try:
                    if backend == "ollama":
                        response = requests.get(f"{endpoint}/api/tags", timeout=5)
                        if response.status_code == 200:
                            models = [model["name"] for model in response.json().get("models", [])]
                            return {"status": "success", "models": models}
                        else:
                            return {"status": "error", "message": "Ollama non raggiungibile"}
                    elif backend == "lmstudio":
                        response = requests.get(f"{endpoint}/v1/internal/model/all", timeout=5)
                        if response.status_code == 200:
                            models = [model["modelId"] for model in response.json().get("data", [])]
                            return {"status": "success", "models": models}
                        else:
                            return {"status": "error", "message": "LM Studio non raggiungibile"}
                    else:
                        return {"status": "error", "message": f"Backend locale non supportato: {backend}"}
                except Exception as e:
                    return {"status": "error", "message": f"Errore nel recupero dei modelli: {str(e)}"}
            
            else:
                return {"status": "error", "message": "Provider non supportato per il listing dei modelli"}
        
        except Exception as e:
            return {"status": "error", "message": f"Errore nel recupero dei modelli: {str(e)}"}

    def available_cloud_models(self):
        """Restituisce solo i modelli cloud per cui esiste una chiave API valida."""
        available = {}
        for model_id, model in llm_config.models.items():
            if model.provider in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.GOOGLE]:
                if llm_config.get_api_key(model.provider):
                    available[model_id] = model
        return available

    def available_local_models(self):
        """Restituisce solo i modelli locali effettivamente disponibili interrogando Ollama o LM Studio."""
        available = {}
        endpoint = llm_config.local_endpoint
        backend = llm_config.local_backend
        try:
            if backend == "ollama":
                response = requests.get(f"{endpoint}/api/tags", timeout=5)
                if response.status_code == 200:
                    local_names = [m["name"] for m in response.json().get("models", [])]
                    for model_id, model in llm_config.models.items():
                        if model.provider == LLMProvider.LOCAL and model.name in local_names:
                            available[model_id] = model
            elif backend == "lmstudio":
                response = requests.get(f"{endpoint}/v1/internal/model/all", timeout=5)
                if response.status_code == 200:
                    local_names = [m["modelId"] for m in response.json().get("data", [])]
                    for model_id, model in llm_config.models.items():
                        if model.provider == LLMProvider.LOCAL and model.name in local_names:
                            available[model_id] = model
        except Exception:
            pass
        return available

# Istanza globale del servizio LLM
llm_service = LLMService()
