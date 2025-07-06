# SlideGuru: System Architecture

This document outlines the architecture of the SlideGuru MVP, detailing the components and the flow of data through the system.

## Components

The application consists of four main logical components:

1.  **Frontend (Web UI)**: A single-page HTML interface (`index.html`) rendered by Flask. It's responsible for providing the user with a file upload form and displaying feedback.

2.  **Backend (Flask Web Server)**: The `app.py` script serves as the application's backbone. It handles HTTP requests, manages file uploads, orchestrates the processing pipeline, and serves the final generated file.

3.  **AI Synthesis Engine**: This is not a physical component but a logical process within `app.py`. It uses the `openai` library to connect to a Large Language Model (LLM) API (e.g., GPT-4). Its sole responsibility is to transform a large block of unstructured text into a structured, presentation-ready JSON object.

4.  **Presentation Generator**: This process uses the `python-pptx` library. It takes the structured JSON data from the AI Engine and a master template (`template.pptx`) to programmatically build a new `.pptx` file, slide by slide, ensuring all content conforms to the template's design.

## Data Flow (Request Lifecycle)

Here is the step-by-step flow when a user generates a presentation:

1.  **User Upload**: The user selects a file (`.docx`, `.pdf`, `.txt`) in the browser and clicks "Generate Slides". An HTTP POST request containing the file is sent to the Flask server.

2.  **File Reception & Validation**: `app.py` receives the request. It validates the file extension and saves the file securely to a temporary `uploads/` directory.

3.  **Text Extraction**: The `extract_text_from_file` function is called. Based on the file extension, it uses the appropriate library (`python-docx` for Word, `PyMuPDF` for PDF) to read the file and extract all its text content into a single string.

4.  **AI Synthesis**: The extracted text is passed to the `synthesize_content_with_ai` function. A carefully engineered prompt is sent to the OpenAI API, instructing it to return a structured JSON object representing the slides.

5.  **JSON Parsing**: The backend receives the JSON response from the AI and parses it into a Python dictionary.

6.  **PPTX Generation**: The `create_presentation` function is invoked with the parsed data.
    -   It first loads the `static/template.pptx` file.
    -   It iterates through the `slides` array in the JSON data.
    -   For each slide object, it adds a new slide to the presentation using the appropriate master layout from the template (e.g., "Title Slide" or "Title and Content").
    -   It populates the placeholders (title, content text box) on the new slide with the data from the JSON.

7.  **File Download**: Once the new `.pptx` file is saved to the `uploads/` directory, the Flask server sends it back to the user's browser as a file attachment, initiating a download.