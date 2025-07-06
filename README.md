# SlideGuru MVP

SlideGuru is a smart presentation assistant that transforms raw documents into beautifully styled PowerPoint slides. This MVP (Minimum Viable Product) serves as the core foundation, focusing on transforming text-based documents (`.docx`, `.pdf`, `.txt`) into a presentation using a user-provided template.

## ✨ Core Features (MVP)

-   **Multi-Format Ingestion:** Upload `.docx`, `.pdf`, or `.txt` files.
-   **AI-Powered Synthesis:** Uses a Large Language Model (LLM) to analyze the document, extract key points, and structure them logically into slide-sized chunks.
-   **Template-Based Styling:** Generates a `.pptx` file that strictly adheres to the styles (colors, fonts, layouts) of a master `template.pptx`.
-   **Web Interface:** A simple, clean UI to upload a document and receive the generated presentation.

## 🚀 Quick Start

1.  **Clone/Set Up:** Use the provided setup script or create the structure manually.
2.  **Virtual Environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure Environment:**
    ```bash
    cp .env.example .env
    # Now edit the .env file with your OpenAI API Key
    ```
5.  **Add Template:** Place your PowerPoint template file in `static/template.pptx`.
6.  **Run the App:**
    ```bash
    flask run
    ```
7.  Open your browser to `http://127.0.0.1:5000`.

## 📚 Documentation

For a deep dive into the setup process, architecture, and potential troubleshooting, please refer to the documents in the `docs/` folder.