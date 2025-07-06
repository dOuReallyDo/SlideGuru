import os
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum

class LLMProvider(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"

@dataclass
class ModelConfig:
    name: str
    provider: LLMProvider
    description: str
    max_tokens: int
    temperature: float
    context_window: int
    cost_per_1k_tokens: Optional[float] = None
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None

class LLMConfig:
    def __init__(self):
        self.config_file = "llm_config.json"
        self.models = self._load_default_models()
        self.current_model = "gpt-3.5-turbo"
        self.local_backend = "ollama"  # "ollama" o "lmstudio"
        self.local_endpoint = "http://localhost:11434"  # default Ollama
        self.load_config()
    
    def _load_default_models(self) -> Dict[str, ModelConfig]:
        return {
            # OpenAI Models
            "gpt-4o": ModelConfig(
                name="GPT-4o",
                provider=LLMProvider.OPENAI,
                description="Modello più avanzato di OpenAI, eccellente per compiti complessi e creativi",
                max_tokens=4096,
                temperature=0.7,
                context_window=128000,
                cost_per_1k_tokens=0.005,
                api_key_env="OPENAI_API_KEY"
            ),
            "gpt-4o-mini": ModelConfig(
                name="GPT-4o Mini",
                provider=LLMProvider.OPENAI,
                description="Versione più veloce ed economica di GPT-4o, ottima per uso generale",
                max_tokens=4096,
                temperature=0.7,
                context_window=128000,
                cost_per_1k_tokens=0.00015,
                api_key_env="OPENAI_API_KEY"
            ),
            "gpt-3.5-turbo": ModelConfig(
                name="GPT-3.5 Turbo",
                provider=LLMProvider.OPENAI,
                description="Modello veloce ed economico, ideale per compiti quotidiani",
                max_tokens=4096,
                temperature=0.7,
                context_window=16385,
                cost_per_1k_tokens=0.0005,
                api_key_env="OPENAI_API_KEY"
            ),
            
            # Anthropic Models
            "claude-3-5-sonnet": ModelConfig(
                name="Claude 3.5 Sonnet",
                provider=LLMProvider.ANTHROPIC,
                description="Modello avanzato di Anthropic, eccellente per analisi e scrittura",
                max_tokens=4096,
                temperature=0.7,
                context_window=200000,
                cost_per_1k_tokens=0.003,
                api_key_env="ANTHROPIC_API_KEY"
            ),
            "claude-3-haiku": ModelConfig(
                name="Claude 3 Haiku",
                provider=LLMProvider.ANTHROPIC,
                description="Modello veloce di Anthropic, perfetto per risposte rapide",
                max_tokens=4096,
                temperature=0.7,
                context_window=200000,
                cost_per_1k_tokens=0.00025,
                api_key_env="ANTHROPIC_API_KEY"
            ),
            
            # Google Models
            "gemini-1.5-pro": ModelConfig(
                name="Gemini 1.5 Pro",
                provider=LLMProvider.GOOGLE,
                description="Modello avanzato di Google, ottimo per compiti complessi",
                max_tokens=8192,
                temperature=0.7,
                context_window=1000000,
                cost_per_1k_tokens=0.0035,
                api_key_env="GOOGLE_API_KEY"
            ),
            "gemini-1.5-flash": ModelConfig(
                name="Gemini 1.5 Flash",
                provider=LLMProvider.GOOGLE,
                description="Versione veloce di Gemini, ideale per uso generale",
                max_tokens=8192,
                temperature=0.7,
                context_window=1000000,
                cost_per_1k_tokens=0.000075,
                api_key_env="GOOGLE_API_KEY"
            ),
            
            # Local Models (Ollama/LM Studio)
            "llama3.1-8b": ModelConfig(
                name="Llama 3.1 8B",
                provider=LLMProvider.LOCAL,
                description="Modello locale leggero, veloce e privato",
                max_tokens=4096,
                temperature=0.7,
                context_window=8192,
                base_url="http://localhost:11434"
            ),
            "llama3.1-70b": ModelConfig(
                name="Llama 3.1 70B",
                provider=LLMProvider.LOCAL,
                description="Modello locale potente, richiede più risorse",
                max_tokens=4096,
                temperature=0.7,
                context_window=8192,
                base_url="http://localhost:11434"
            ),
            "mistral-7b": ModelConfig(
                name="Mistral 7B",
                provider=LLMProvider.LOCAL,
                description="Modello bilanciato tra performance e velocità",
                max_tokens=4096,
                temperature=0.7,
                context_window=8192,
                base_url="http://localhost:11434"
            ),
            "codellama-7b": ModelConfig(
                name="Code Llama 7B",
                provider=LLMProvider.LOCAL,
                description="Specializzato per codice e documentazione tecnica",
                max_tokens=4096,
                temperature=0.7,
                context_window=8192,
                base_url="http://localhost:11434"
            )
        }
    
    def load_config(self):
        """Carica la configurazione da file"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    data = json.load(f)
                    self.current_model = data.get('current_model', 'gpt-3.5-turbo')
                    self.local_backend = data.get('local_backend', 'ollama')
                    self.local_endpoint = data.get('local_endpoint', 'http://localhost:11434')
                    # Aggiorna i parametri personalizzati
                    for model_id, params in data.get('custom_params', {}).items():
                        if model_id in self.models:
                            for key, value in params.items():
                                if hasattr(self.models[model_id], key):
                                    setattr(self.models[model_id], key, value)
            except Exception as e:
                print(f"Errore nel caricamento della configurazione: {e}")
    
    def save_config(self):
        """Salva la configurazione su file"""
        try:
            data = {
                'current_model': self.current_model,
                'local_backend': self.local_backend,
                'local_endpoint': self.local_endpoint,
                'custom_params': {}
            }
            # Salva solo i parametri personalizzati
            for model_id, model in self.models.items():
                custom_params = {}
                if model.temperature != 0.7:
                    custom_params['temperature'] = model.temperature
                if model.max_tokens != 4096:
                    custom_params['max_tokens'] = model.max_tokens
                if custom_params:
                    data['custom_params'][model_id] = custom_params
            
            with open(self.config_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Errore nel salvataggio della configurazione: {e}")
    
    def get_current_model(self) -> ModelConfig:
        """Restituisce il modello corrente"""
        return self.models.get(self.current_model, self.models['gpt-3.5-turbo'])
    
    def set_current_model(self, model_id: str):
        """Imposta il modello corrente"""
        if model_id in self.models:
            self.current_model = model_id
            self.save_config()
    
    def update_model_params(self, model_id: str, **params):
        """Aggiorna i parametri di un modello"""
        if model_id in self.models:
            model = self.models[model_id]
            for key, value in params.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            self.save_config()
    
    def get_models_by_provider(self, provider: LLMProvider) -> Dict[str, ModelConfig]:
        """Restituisce tutti i modelli di un provider"""
        return {k: v for k, v in self.models.items() if v.provider == provider}
    
    def add_custom_model(self, model_id: str, config: ModelConfig):
        """Aggiunge un modello personalizzato"""
        self.models[model_id] = config
        self.save_config()
    
    def get_api_key(self, provider: LLMProvider) -> Optional[str]:
        """Restituisce la chiave API per un provider"""
        env_vars = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            LLMProvider.GOOGLE: "GOOGLE_API_KEY"
        }
        
        if provider in env_vars:
            return os.getenv(env_vars[provider])
        return None
    
    def set_api_key(self, provider: LLMProvider, api_key: str):
        """Imposta la chiave API per un provider"""
        env_vars = {
            LLMProvider.OPENAI: "OPENAI_API_KEY",
            LLMProvider.ANTHROPIC: "ANTHROPIC_API_KEY",
            LLMProvider.GOOGLE: "GOOGLE_API_KEY"
        }
        
        if provider in env_vars:
            os.environ[env_vars[provider]] = api_key
    
    def set_local_backend(self, backend: str, endpoint: str):
        self.local_backend = backend
        self.local_endpoint = endpoint
        self.save_config()

# Istanza globale della configurazione
llm_config = LLMConfig() 