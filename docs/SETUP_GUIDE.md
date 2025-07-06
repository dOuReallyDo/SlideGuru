# SlideGuru: Developer Setup Guide

This guide provides detailed, step-by-step instructions for setting up and running the SlideGuru MVP on your local machine.

## 1. Prerequisites

-   **Python 3.8+**: Ensure Python is installed and accessible from your terminal. Check with `python --version`.
-   **Git**: Required for version control (best practice).
-   **PowerPoint Template**: Have a `.pptx` file ready to use as your template.

## 2. Setup Instructions

### Step 1: Create Project Structure
Run the provided setup script or create the structure manually as described in the main `README.md`.

### Step 2: Set Up a Python Virtual Environment
A virtual environment isolates your project's dependencies. This is a critical step.

```bash
# Navigate into your project directory
cd slideguru

# Create a virtual environment named 'venv'
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows (Command Prompt):
venv\Scripts\activate