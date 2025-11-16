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
        "BEGIN:VCALENDAR", "VERSION:2.0", "PRODID:-//MyPortfolio//EN",
        "BEGIN:VEVENT", f"UID:{now.strftime('%Y%m%dT%H%M%SZ')}@mydomain.com",
        f"DTSTAMP:{now.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTSTART:{start_time.strftime('%Y%m%dT%H%M%SZ')}",
        f"DTEND:{end_time.strftime('%Y%m%dT%H%M%SZ')}",
        "SUMMARY:Meeting with Abdulla", "DESCRIPTION:A brief introductory call.",
        "LOCATION:Virtual", "END:VEVENT", "END:VCALENDAR"
    ]
    return "\r\n".join(ics_content)


def get_database_context():
    """Fetches project information from the database to provide as context."""
    projects = Project.objects.all()
    if not projects:
        return "There are currently no projects in the portfolio."

    project_list = []
    for p in projects:
        project_list.append(f"- Title: {p.title}, Tech: {p.tech_stack}, Description: {p.description}, Link: {p.link}")
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

    if "meeting" in prompt.lower() or "schedule" in prompt.lower():
        ics_file = generate_ics()
        response = HttpResponse(ics_file, content_type='text/calendar')
        response['Content-Disposition'] = 'attachment; filename="meeting.ics"'
        ChatLog.objects.create(user_message=prompt, agent_response="[Generated ICS file for meeting]")
        return response

    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        db_context = get_database_context()
        system_prompt = f"""
        You are Abdulla, a professional full-stack developer, and this is your portfolio.
        Your name is Abdulla.
        You are acting as an AI assistant on your own portfolio website.
        Be friendly, professional, and helpful.
        Use the following database context about your projects to answer questions.
        Do not make up projects. Only use the information provided below.

        If the user asks for your email or contact info, respond with:
        "You can reach me at Email: abdullafajal@gmail.com Or call me at Mobile: +91-8958468602"

        DATABASE CONTEXT:
        {db_context}

        Based on this, answer the user's prompt.
        """
        response = model.generate_content([system_prompt, f"User prompt: {prompt}"])
        agent_response_text = response.text
        response_data = {
            "text": agent_response_text,
            "action": None,
            "data": None
        }
        if "project" in prompt.lower():
            response_data["action"] = "show_projects"
        elif "contact" in prompt.lower() or "email" in prompt.lower():
            response_data["action"] = "email"
            response_data["data"] = {"email": "abdullafajal@gmail.com"}

    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        response_data = {
            "text": "Sorry, I'm having trouble connecting to my brain right now. Please try again later.",
            "action": None, "data": None
        }

    ChatLog.objects.create(user_message=prompt, agent_response=response_data["text"])
    return JsonResponse(response_data)