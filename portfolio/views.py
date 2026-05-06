import threading
import json
import os
from datetime import datetime, timedelta

import google.generativeai as genai
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt

from .forms import ContactForm, ComposeEmailForm
from .models import ChatLog, Project, ContactMessage, ResumeFile
from django.contrib.auth.decorators import user_passes_test
from django.core.mail import EmailMultiAlternatives


# --- Configure Gemini API ---
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except AttributeError:
    print("Warning: GEMINI_API_KEY not found in settings. The agent will not work.")
    pass

def _send_mail_async(subject, message, from_email, recipient_list, cc=None, bcc=None, html_message=None):
    """Helper function to send email in a separate thread."""
    try:
        email = EmailMultiAlternatives(
            subject=subject,
            body=message,
            from_email=from_email,
            to=recipient_list,
            cc=cc or [],
            bcc=bcc or [],
        )

        if html_message:
            email.attach_alternative(html_message, "text/html")

        email.send(fail_silently=False)

    except Exception as e:
        print(f"Error sending email asynchronously: {e}")

# --- Helper Functions ---


def generate_ics():
    """Generates a simple .ics file for a meeting."""
    now = datetime.utcnow()
    start_time = now + timedelta(days=1)
    end_time = start_time + timedelta(hours=1)

    ics_content = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//MyPortfolio//EN",
        "BEGIN:VEVENT",
        f"UID:{now.strftime('%Y%m%dT%H%M%SZ')}@abdullafajal.pythonanywhere.com",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{start_time.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTEND:{end_time.strftime('%Y%m%dT%H%M%SZ')}",
        "SUMMARY:Meeting with Abdulla",
        "DESCRIPTION:A brief introductory call.",
        "LOCATION:Virtual",
        "END:VEVENT",
        "END:VCALENDAR"
    ]

    return "\r\n".join(ics_content)



def get_database_context():
    """Fetches project information from the database to provide as context."""
    projects = Project.objects.all()
    if not projects:
        return "There are currently no projects in the portfolio."

    project_list = []
    for p in projects:
        project_list.append(f"- Title: {p.title}, Slug: {p.slug}, Tech: {p.tech_stack}, Description: {p.description}, Link: {p.link}")
    return "Here are the projects in my portfolio:\n" + "\n".join(project_list)


# --- Main Views ---

def home(request):
    """Renders the main portfolio landing page."""
    # fetch projects from the database and pass to the home template
    projects = Project.objects.all().order_by('display_order')
    # include resume data so the home page can render the resume section as HTML
    resume = get_resume_data()
    # Get latest resume file for download button
    resume_file = ResumeFile.objects.first()
    resume_file_url = resume_file.file.url if resume_file else None
    context = {"projects": projects, "resume": resume, "resume_file_url": resume_file_url}
    return render(request, "portfolio/home.html", context)


def about(request):
    """Renders the about page."""
    return render(request, "portfolio/about.html")


def projects(request):
    """Renders the projects page."""
    projects = Project.objects.all().order_by('display_order')
    context = {"projects": projects}
    return render(request, "portfolio/projects.html", context)


def contact_view(request):
    """Handles the contact form page."""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_text = form.cleaned_data['message']
            subject = form.cleaned_data.get('subject') or 'New Contact Message'

            # --- Save submission to database ---
            try:
                ContactMessage.objects.create(name=name, email=email, subject=subject, message=message_text)
            except Exception as e:
                # If saving fails, log and continue so user still receives confirmation
                print(f"Warning: failed to save contact message: {e}")

            # --- Send Email to Admin ---
            admin_html_message = render_to_string('emails/admin_email.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message_text,
            })
            try:
                threading.Thread(
                    target=_send_mail_async,
                    args=(
                        f'New Portfolio Message from {name} ({subject})',
                        f'From: {name}\nEmail: {email}\n\n{message_text}',
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
                        [getattr(settings, 'ADMIN_EMAIL', 'abdullafajal@gmail.com')],
                        admin_html_message,
                    )
                ).start()
            except Exception as e:
                # don't break the user flow if email sending fails
                print(f"Error sending admin email: {e}")
                messages.warning(request, "There was a problem sending the admin notification email. The message was saved.")

            # --- Send Confirmation Email to User ---
            user_html_message = render_to_string('emails/user_email.html', {
                'name': name,
                'message': message_text,
            })
            try:
                threading.Thread(
                    target=_send_mail_async,
                    args=(
                        'Thank you for your message!',
                        f'Hi {name},\n\nThank you for your message. I will get back to you shortly.\n\nBest,\nAbdulla Fajal',
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
                        [email],
                        user_html_message,
                    )
                ).start()
            except Exception as e:
                print(f"Error sending confirmation email to user: {e}")
                messages.warning(request, "There was a problem sending the confirmation email, but your message was received.")

            messages.success(request, "Your message has been sent successfully! I'll get back to you soon.")
            return redirect('portfolio:home')
    else:
        form = ContactForm()

    return render(request, 'portfolio/home.html', {'form': form})

def resume_view(request):
    """Renders the resume page with data parsed from the PDF."""
    resume_data = get_resume_data()
    resume_file = ResumeFile.objects.first()
    resume_data['resume_file_url'] = resume_file.file.url if resume_file else None
    return render(request, 'portfolio/resume.html', resume_data)


def get_resume_data():
    """Return structured resume data from dynamic preferences.

    Reads all resume fields from the global preferences registry.
    HTML content fields (experience, skills) are stored as raw HTML.
    """
    from dynamic_preferences.registries import global_preferences_registry
    prefs = global_preferences_registry.manager()

    return {
        "name": prefs.get('resume__name', 'ABDULLA'),
        "address": prefs.get('resume__address', ''),
        "email": prefs.get('resume__email', 'abdullafajal@gmail.com'),
        "mobile": prefs.get('resume__mobile', '+91-8958468602'),
        "summary": prefs.get('resume__summary', ''),
        "experience": prefs.get('resume__experience', ''),
        "skills": prefs.get('resume__skills', ''),
        "education": {
            "degree": prefs.get('resume__education_degree', ''),
            "university": prefs.get('resume__education_university', ''),
        },
        "about_experience": prefs.get('resume__about_experience', ''),
    }


def get_resume_summary(resume_data):
    """Generates a concise text summary of the resume data."""
    summary = f"Name: {resume_data['name']}\n"
    summary += f"Email: {resume_data['email']}\n"
    summary += f"Phone: {resume_data['mobile']}\n"
    summary += f"Professional Summary: {resume_data['summary']}\n\n"

    # Experience and skills are now HTML strings; include as-is for AI context
    if resume_data.get('experience'):
        summary += f"Experience:\n{resume_data['experience']}\n\n"

    if resume_data.get('skills'):
        summary += f"Skills:\n{resume_data['skills']}\n"

    return summary


@csrf_exempt
def agent_query(request):
    """API endpoint to handle queries for the AI agent using Gemini."""
    if request.method != 'POST':

        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not prompt:
        return JsonResponse({'error': 'Prompt is required'}, status=400)

    # --- Handle meeting requests separately ---
    if "meeting" in prompt.lower() or "schedule" in prompt.lower():
        ics_file = generate_ics()
        response = HttpResponse(ics_file, content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="meeting.ics"'
        ChatLog.objects.create(user_message=prompt, agent_response="[Generated ICS file for meeting]")
        return response

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        prompt_lower = prompt.lower()
        
        # Level 0: Simple Greetings (no context needed)
        if prompt_lower in ["hi", "hello", "hey", "hola"]:
            system_prompt = f"""
You are "Abdulla's Assistant," a friendly and professional AI guide.
Your response MUST be a valid JSON object with "text" and "action" fields.
The "text" should be a brief, warm greeting. The "action" must be null.

**Response Format:**
{{
  "text": "Hi there! I'm Abdulla's AI assistant. How can I help you today?",
  "action": {{ "type": null, "value": null }}
}}

User prompt: {prompt}
"""
        else:
            # Build context selectively
            context_str = ""
            
            # Level 1 (Default): Resume Summary for most questions
            resume_data = get_resume_data()
            resume_summary = get_resume_summary(resume_data)
            context_str += f"\n**Core Information (Resume & Skills Summary):**\n{resume_summary}"

            # Level 2: Add Project context only if needed
            if "project" in prompt_lower or "work" in prompt_lower:
                project_context = get_database_context()
                context_str += f"\n\n**Project Details:**\n{project_context}"

            # --- Build the final system prompt ---
            system_prompt = f"""
            You are Abdulla, a professional full-stack developer, and this is your portfolio.
            Your name is Abdulla.
        You are acting as an AI assistant on your own portfolio website.
        Be friendly, professional, and helpful.
        Use the following database context about your projects to answer questions.
        Do not make up projects. Only use the information provided below.

        More information about me:
        {get_resume_data()}

**Core Instructions:**
- Answer Concisely: Provide answers in 1-2 short sentences.
- Use Provided Context: Base your answers *only* on the provided context. Do not invent details.
- Contact Information: If asked for contact details, use the info from the context.

**Context:**
{context_str}

**Response Format:**
Your response MUST be a valid JSON object with "text" and "action" fields.

**Action Guidance:**
- When the user asks to see something on the current page, use the `highlight` action.
- **Projects**: Use `{{ "type": "highlight", "value": "#portfolio" }}`.
- **Services**: Use `{{ "type": "highlight", "value": "#services" }}`.
- **Resume**: Use `{{ "type": "highlight", "value": "#resume" }}`.
- **Skills**: Use `{{ "type": "highlight", "value": "#resume-skills" }}`.
- **About Me**: Use `{{ "type": "highlight", "value": "#about" }}`.
- **Contact**: Use `{{ "type": "highlight", "value": "#contactus" }}`.
- When providing contact info, use the `email` action: `{{ "type": "email", "value": "abdullafajal@gmail.com" }}`.
- If no specific action is relevant, the action should be `null`.

---
User prompt: {prompt}
"""
        # Generate content and parse the JSON response
        response = model.generate_content([system_prompt])
        
        # Clean the response text to ensure it's valid JSON
        cleaned_response_text = response.text.strip().replace("`", "")
        if cleaned_response_text.startswith("json"):
            cleaned_response_text = cleaned_response_text[4:]

        response_data = json.loads(cleaned_response_text)
        
        # Ensure the response has the expected structure
        if 'text' not in response_data or 'action' not in response_data:
            raise ValueError("Invalid response structure from model")

    except (Exception, json.JSONDecodeError) as e:
        print(f"Error processing agent query: {e}")
        response_data = {
            "text": "Sorry, I'm having a bit of trouble thinking right now. Please try again later.",
            "action": {"type": None, "value": None}
        }

    ChatLog.objects.create(user_message=prompt, agent_response=response_data.get("text", ""))
    return JsonResponse(response_data)


@user_passes_test(lambda u: u.is_superuser)
def compose_email(request):
    """
    View for superusers to compose and send emails.
    """
    if request.method == 'POST':
        form = ComposeEmailForm(request.POST)
        if form.is_valid():
            recipient = form.cleaned_data['recipient']
            cc = form.cleaned_data['cc']
            bcc = form.cleaned_data.get('bcc', '')
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # --- Render HTML Email ---
            html_message = render_to_string('emails/special_template.html', {
                'subject': subject,
                'message': message,
            })
            
            # --- Send Email Async ---
            try:
                threading.Thread(
                    target=_send_mail_async,
                    args=(
                        subject,
                        message, # Plain text fallback
                        getattr(settings, 'DEFAULT_FROM_EMAIL', 'webmaster@localhost'),
                        [recipient],
                        [cc] if cc else [],
                        [bcc] if bcc else [],
                        html_message,
                    )
                ).start()
                messages.success(request, f"Email sent successfully to {recipient}!")
                return redirect('portfolio:compose_email')
            except Exception as e:
                print(f"Error sending email: {e}")
                messages.error(request, "Failed to send email. Check console logs.")
    else:
        form = ComposeEmailForm()
    
    return render(request, 'portfolio/compose_email.html', {'form': form})


@user_passes_test(lambda u: u.is_superuser)
def ai_generate_email(request):
    """API endpoint to generate email content using Gemini AI."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    try:
        data = json.loads(request.body)
        prompt = data.get('prompt', '').strip()
        subject = data.get('subject', '').strip()
        recipient = data.get('recipient', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    if not prompt:
        return JsonResponse({'error': 'Prompt is required'}, status=400)

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')

        system_prompt = f"""You are a professional email writing assistant for Abdulla Fajal, a Senior Django Developer.
Write a professional, well-structured email body based on the user's instructions.

Context:
- Sender: Abdulla Fajal (Softwere Developer)
- Recipient: {recipient if recipient else 'Not specified'}
- Subject: {subject if subject else 'Not specified'}

Instructions from user: {prompt}

Rules:
- Write ONLY the email body content (no subject line, no "Subject:" prefix).
- Use proper HTML formatting with <p>, <strong>, <em>, <ul>, <li> tags for structure.
- Keep it professional, concise, and well-formatted.
- Include appropriate greeting but do NOT include any sign-off like "Best regards", "Sincerely", "Thank you" etc.
- Do NOT wrap in ```html``` code blocks, just return raw HTML.
"""

        response = model.generate_content([system_prompt])
        generated_text = response.text.strip()

        # Clean any markdown code block wrappers
        if generated_text.startswith("```html"):
            generated_text = generated_text[7:]
        if generated_text.startswith("```"):
            generated_text = generated_text[3:]
        if generated_text.endswith("```"):
            generated_text = generated_text[:-3]
        generated_text = generated_text.strip()

        return JsonResponse({'content': generated_text})

    except Exception as e:
        print(f"Error generating email content: {e}")
        return JsonResponse({'error': 'Failed to generate content. Please try again.'}, status=500)