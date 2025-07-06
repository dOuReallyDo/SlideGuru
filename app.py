from dotenv import load_dotenv
import os
import json
from flask import Flask, render_template, request, send_file, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import docx
import fitz  # PyMuPDF
from pptx import Presentation
from config import llm_config, LLMProvider
from llm_service import llm_service
import logging
from logging.handlers import RotatingFileHandler
import traceback

# --- CARICA CONFIG ---
load_dotenv()

# --- CONFIG FLASK ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-for-flash-messages'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}
app.config['TEMPLATE_PATH'] = os.path.join('static', 'template.pptx')

# Logging su file
if not os.path.exists('logs'):
    os.makedirs('logs')
file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=3)
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
app.logger.addHandler(file_handler)

# Handler globale per errori 500
@app.errorhandler(500)
def internal_error(error):
    tb = traceback.format_exc()
    app.logger.error(f"Errore 500: {error}\nTraceback:\n{tb}")
    return render_template('500.html', error=error, traceback=tb), 500

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- UTILITY ---
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_file(filepath):
    ext = filepath.rsplit('.', 1)[1].lower()
    text = ""
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    elif ext == 'pdf':
        doc = fitz.open(filepath)
        for page in doc:
            text += page.get_text()
    elif ext == 'docx':
        doc = docx.Document(filepath)
        for para in doc.paragraphs:
            text += para.text + '\n'
    return text

def create_presentation(slides_content):
    prs = Presentation(app.config['TEMPLATE_PATH'])
    for slide_text in slides_content:
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = slide_text.get("title", "")
        slide.placeholders[1].text = slide_text.get("content", "")
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.pptx")
    prs.save(output_path)
    return output_path

def generate_slide_content(prompt_text):
    try:
        prompt = f"Genera una breve struttura di slide PowerPoint per: {prompt_text}. Rispondi in JSON con lista di dict contenenti 'title' e 'content'."
        response = llm_service.generate_content(prompt)
        try:
            slides_content = json.loads(response)
        except json.JSONDecodeError:
            slides_content = [{"title": "Errore parsing JSON", "content": response}]
        return slides_content
    except Exception as e:
        return [{"title": "Errore generazione", "content": f"Errore: {str(e)}"}]

# --- ROUTES ---
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        files = request.files.getlist('file')
        if not files or all(f.filename == '' for f in files):
            flash('No selected file')
            return redirect(request.url)
        texts = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                texts.append(extract_text_from_file(filepath))
        if not texts:
            flash('Nessun file valido caricato')
            return redirect(request.url)
        text = '\n'.join(texts)
        slides_content = generate_slide_content(text)
        pptx_path = create_presentation(slides_content)
        return send_file(pptx_path, as_attachment=True)
    return render_template('index.html')

@app.route("/config")
def config_page():
    current_model = llm_config.get_current_model()
    # Modelli cloud disponibili solo se c'è la key
    available_cloud = llm_service.available_cloud_models()
    # Modelli locali effettivamente disponibili
    available_local = llm_service.available_local_models()
    # Per ogni provider cloud, indica se manca la key
    missing_keys = {
        'openai': not bool(llm_config.get_api_key(LLMProvider.OPENAI)),
        'anthropic': not bool(llm_config.get_api_key(LLMProvider.ANTHROPIC)),
        'google': not bool(llm_config.get_api_key(LLMProvider.GOOGLE)),
    }
    return render_template('config.html',
        current_model=current_model,
        available_cloud=available_cloud,
        available_local=available_local,
        missing_keys=missing_keys,
        local_backend=llm_config.local_backend,
        local_endpoint=llm_config.local_endpoint,
        llm_config=llm_config)

@app.route("/api/set_model", methods=['POST'])
def set_model():
    data = request.get_json()
    model_id = data.get('model_id')
    if model_id and model_id in llm_config.models:
        llm_config.set_current_model(model_id)
        return jsonify({"status": "success", "message": f"Modello impostato su {llm_config.models[model_id].name}"})
    return jsonify({"status": "error", "message": "Modello non trovato"})

@app.route("/api/update_model_params", methods=['POST'])
def update_model_params():
    data = request.get_json()
    model_id = data.get('model_id')
    params = data.get('params', {})
    
    if model_id and model_id in llm_config.models:
        llm_config.update_model_params(model_id, **params)
        return jsonify({"status": "success", "message": "Parametri aggiornati"})
    return jsonify({"status": "error", "message": "Modello non trovato"})

@app.route("/api/set_api_key", methods=['POST'])
def set_api_key():
    data = request.get_json()
    provider_name = data.get('provider')
    api_key = data.get('api_key')
    
    try:
        provider = LLMProvider(provider_name)
        llm_config.set_api_key(provider, api_key)
        # Reinizializza il servizio LLM
        llm_service._initialize_clients()
        return jsonify({"status": "success", "message": f"Chiave API per {provider_name} impostata"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/test_connection", methods=['POST'])
def test_connection():
    data = request.get_json()
    provider_name = data.get('provider')
    
    try:
        provider = LLMProvider(provider_name)
        result = llm_service.test_connection(provider)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/get_available_models", methods=['POST'])
def get_available_models():
    data = request.get_json()
    provider_name = data.get('provider')
    
    try:
        provider = LLMProvider(provider_name)
        result = llm_service.get_available_models(provider)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/set_local_backend", methods=['POST'])
def set_local_backend():
    data = request.get_json()
    backend = data.get('backend')
    endpoint = data.get('endpoint')
    if backend in ['ollama', 'lmstudio'] and endpoint:
        llm_config.set_local_backend(backend, endpoint)
        return jsonify({"status": "success", "message": "Backend locale aggiornato"})
    return jsonify({"status": "error", "message": "Dati non validi"})

@app.route("/api/get_config", methods=['GET'])
def get_config():
    config = {
        'current_model': llm_config.current_model,
        'local_backend': llm_config.local_backend,
        'local_endpoint': llm_config.local_endpoint,
        'models': {k: v.__dict__ for k, v in llm_config.models.items()},
        'custom_params': {},
        'api_keys': {
            'openai': bool(llm_config.get_api_key(LLMProvider.OPENAI)),
            'anthropic': bool(llm_config.get_api_key(LLMProvider.ANTHROPIC)),
            'google': bool(llm_config.get_api_key(LLMProvider.GOOGLE)),
        }
    }
    return jsonify(config)

# --- START SERVER ---
if __name__ == "__main__":
    app.run(debug=False, port=8080)