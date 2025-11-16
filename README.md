# AI Portfolio Assistant

This is a Django-based portfolio website featuring a conversational AI assistant. The project uses Tabler for the UI, AOS for scroll animations, and a custom JavaScript chat widget.

## Features

- **AI Agent**: Answers questions about the developer's skills, projects, and contact information using Google's Gemini API.
- **Project Gallery**: Displays a portfolio of projects managed via the Django admin.
- **Interactive Actions**: Includes "Show project gallery," "Email me," and "Schedule a meeting" (which generates an ICS file).
- **Chat History**: Stores user messages in a local SQLite database.
- **Admin View**: Provides a simple admin interface to view chat logs and manage projects.

## Project Structure

```
/
├───db.sqlite3
├───manage.py
├───pyproject.toml
├───README.md
├───static/
│   ├───css/
│   └───js/
├───abdullafajal/
│   ├───settings.py
│   └───urls.py
└───portfolio/
    ├───models.py
    ├───views.py
    └───...
```

## Local Development Setup

### Prerequisites

- Python 3.8+
- `uv` package manager (`pip install uv`)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt
    ```
    The `requirements.txt` file includes `Django`, `google-generativeai`, `Pillow`, and other necessary packages.

4.  **Set up your environment variables:**
    Create a file named `.env.dev` in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY='your-gemini-api-key'
    ```
    *Note: For production, you should use a more secure method for managing secrets.*

5.  **Apply database migrations:**
    ```bash
    python manage.py migrate
    ```

6.  **Create a superuser to access the admin panel:**
    ```bash
    python manage.py createsuperuser
    ```

7.  **Run the development server:**
    ```bash
    python manage.py runserver
    ```
    The application will be available at `http://127.0.0.1:8000/`. The admin panel is at `http://127.0.0.1:8000/admin/`.

## How to Use

1.  Navigate to the admin panel (`/admin/`).
2.  Log in with your superuser account.
3.  Add a few projects via the "Projects" section.
4.  Go to the homepage and try out the AI assistant!

## AWS EC2 Deployment (Optional)

You can deploy the application to AWS EC2 for production. A simple approach is to provision an EC2 instance, install system dependencies, copy your project, configure environment variables, and run the application behind Gunicorn + Nginx. If you prefer containers, you can run Docker on EC2 (or use ECS/EKS) and deploy container images there.

Basic options:

- Quick local-style run on an EC2 instance: provision an instance, clone the repo, create a virtualenv, install requirements, setup `.env` and run Gunicorn behind Nginx.
- Container-based: build a Docker image and run it on EC2 (or push to ECR and run via ECS/EKS).

For local development continue using:
```bash
python manage.py runserver
```