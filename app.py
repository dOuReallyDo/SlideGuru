from dotenv import load_dotenv
import os
import json
from flask import Flask, render_template, request, send_file, redirect, url_for, flash
from werkzeug.utils import secure_filename
import docx
import fitz  # PyMuPDF
from pptx import Presentation
from openai import OpenAI

# --- CARICA CONFIG ---
load_dotenv()

# --- CONFIG CLIENT LM STUDIO ---
client = OpenAI(
    base_url="http://192.168.68.120:1234/v1",
    api_key="sk-local"  # LM Studio accetta qualsiasi stringa
)

# --- CONFIG FLASK ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a-super-secret-key-for-flash-messages'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'docx'}
app.config['TEMPLATE_PATH'] = os.path.join('static', 'template.pptx')

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
    # Sicurezza per file enormi
    return text[:5000]

def create_presentation(slides_content):
    prs = Presentation(app.config['TEMPLATE_PATH'])
    for slide_text in slides_content:
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        slide.shapes.title.text = slide_text.get("title", "")
        slide.placeholders[1].text = slide_text.get("content", "")
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output.pptx")
    prs.save(output_path)
    return output_path

def generate_slide_content(prompt_text):
    # Ulteriore safety per prompt lunghi
    prompt_text = prompt_text[:3000]
    response = client.chat.completions.create(
        model="qwen3-14b-mlx",
        messages=[
            {"role": "user", "content": f"Genera un elenco di slide in JSON con 'title' e 'content' su: {prompt_text}"}
        ]
    )
    try:
        slides_content = json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        slides_content = [{"title": "Errore parsing JSON", "content": response.choices[0].message.content}]
    return slides_content

# --- ROUTES ---
@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            text = extract_text_from_file(filepath)
            slides_content = generate_slide_content(text)
            pptx_path = create_presentation(slides_content)
            return send_file(pptx_path, as_attachment=True)

    return render_template('index.html')

# --- START ---
if __name__ == "__main__":
    app.run(debug=True)