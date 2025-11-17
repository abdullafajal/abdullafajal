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

from .forms import ContactForm
from .models import ChatLog, Project, ContactMessage

# --- Configure Gemini API ---
try:
    genai.configure(api_key=settings.GEMINI_API_KEY)
except AttributeError:
    print("Warning: GEMINI_API_KEY not found in settings. The agent will not work.")
    pass

def _send_mail_async(subject, message, from_email, recipient_list, html_message):
    """Helper function to send email in a separate thread."""
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False,
        )
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
    context = {"projects": projects, "resume": resume}
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
    return render(request, 'portfolio/resume.html', resume_data)


def get_resume_data():
    """Return structured resume data.

    Currently returns a hard-coded dict derived from the PDF in static files.
    This central helper allows templates and views to share the same data.
    """
    return {
        "name": "ABDULLA",
        "address": "C-39, Street No 10, Brijpuri Extension, Parwana Road, Delhi - 110051",
        "email": "abdullafajal@gmail.com",
        "mobile": "+91-8958468602",
        "summary": "To obtain a challenging position as a Django and Flask Developer in a dynamic organization where I can apply my technical expertise, problem-solving abilities, and passion for building scalable applications to contribute to organizational success.",
        "experience": [
            {
                "title": "Senior Django Developer",
                "company": "Aquevix Pvt. Ltd.",
                "slug": "aquevix",
                "location": "New Delhi, India",
                "duration": "Apr 2024 – Present",
                "points": [
                    "Developed video/audio streaming, live podcast, and subscription management modules for The News Junkie platform.",
                    "Built secure REST APIs and implemented authentication systems using Django REST Framework.",
                    "Managed PostgreSQL databases for efficient file storage and retrieval.",
                    "Collaborated with frontend developers using Bootstrap and Unpoly to improve user experience.",
                ],
                "tech_stack": "Python, Django, Django REST Framework, PostgreSQL, Bootstrap, Tabler, GitHub"
            },
            {
                "title": "Freelance Django Developer",
                "company": "Espere Project",
                "slug": "espere",
                "location": "Remote",
                "duration": "2023 – 2024",
                "points": [
                    "Designed and developed a multi-feature platform with blogging, live chat, social networking, and an embedded online compiler.",
                    "Integrated Redis server, WebSockets, and social authentication for real-time communication.",
                ],
                "tech_stack": "Python, Django, Redis, WebSockets, PostgreSQL, AWS"
            }
        ],
        "skills": {
            "Languages": ["Python"],
            "Frameworks": ["Django", "Django REST Framework", "Flask"],
            "Databases": ["PostgreSQL"],
            "Tools": ["PyCharm", "VS Code"],
            "Miscellaneous": ["AWS EC2", "GIT", "Linux", "HTML", "CSS", "Bootstrap"],
        },
        "education": {
            "degree": "B.Sc. Computer Science",
            "university": "Mahatma Jyotiba Phule Rohilkhand University"
        }
    }


def get_resume_summary(resume_data):
    """Generates a concise text summary of the resume data."""
    summary = f"Name: {resume_data['name']}\n"
    summary += f"Email: {resume_data['email']}\n"
    summary += f"Phone: {resume_data['mobile']}\n"
    summary += f"Professional Summary: {resume_data['summary']}\n\n"
    
    summary += "Experience:\n"
    for job in resume_data['experience']:
        summary += f"- {job['title']} at {job['company']} ({job['duration']}).\n"
        
    summary += "\nKey Skills:\n"
    for category, items in resume_data['skills'].items():
        summary += f"- {category}: {', '.join(items)}\n"
        
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