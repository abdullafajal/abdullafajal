from dynamic_preferences.types import IntegerPreference, StringPreference, LongStringPreference
from dynamic_preferences.preferences import Section
from dynamic_preferences.registries import global_preferences_registry

# Sections
general = Section('general')
resume = Section('resume')


# ── General ──────────────────────────────────────────────────────────────────

@global_preferences_registry.register
class TotalProject(IntegerPreference):
    section = general
    name = 'total_projects'
    default = 5
    required = True
    help_text = 'Total number of projects to display on the homepage.'


@global_preferences_registry.register
class TotalClient(IntegerPreference):
    section = general
    name = 'total_clients'
    default = 5
    required = True
    help_text = 'Total number of client to display on the homepage.'


# ── Resume ───────────────────────────────────────────────────────────────────

@global_preferences_registry.register
class ResumeName(StringPreference):
    section = resume
    name = 'name'
    default = 'ABDULLA'
    required = True
    help_text = 'Full name displayed on the resume.'


@global_preferences_registry.register
class ResumeAddress(LongStringPreference):
    section = resume
    name = 'address'
    default = 'C-39, Street No 10, Brijpuri Extension, Parwana Road, Delhi - 110051'
    required = False
    help_text = 'Address displayed on the resume.'


@global_preferences_registry.register
class ResumeEmail(StringPreference):
    section = resume
    name = 'email'
    default = 'abdullafajal@gmail.com'
    required = True
    help_text = 'Email displayed on the resume.'


@global_preferences_registry.register
class ResumeMobile(StringPreference):
    section = resume
    name = 'mobile'
    default = '+91-8958468602'
    required = True
    help_text = 'Phone number displayed on the resume.'


@global_preferences_registry.register
class ResumeSummary(LongStringPreference):
    section = resume
    name = 'summary'
    default = 'To obtain a challenging position as a Django and Flask Developer in a dynamic organization where I can apply my technical expertise, problem-solving abilities, and passion for building scalable applications to contribute to organizational success.'
    required = False
    help_text = 'Professional summary. You can paste HTML here.'


@global_preferences_registry.register
class ResumeExperience(LongStringPreference):
    section = resume
    name = 'experience'
    default = '''<div class="resume-job mt-3 pb-2 border-bottom">
  <h6 class="mb-0">Senior Django Developer <small class="text-muted">— Aquevix Pvt. Ltd.</small></h6>
  <p class="mb-1"><small class="text-muted">New Delhi, India · Apr 2024 – Present</small></p>
  <ul class="mb-2">
    <li>Developed video/audio streaming, live podcast, and subscription management modules for The News Junkie platform.</li>
    <li>Built secure REST APIs and implemented authentication systems using Django REST Framework.</li>
    <li>Managed PostgreSQL databases for efficient file storage and retrieval.</li>
    <li>Collaborated with frontend developers using Bootstrap and Unpoly to improve user experience.</li>
  </ul>
  <p class="mb-0"><strong>Tech:</strong> Python, Django, Django REST Framework, PostgreSQL, Bootstrap, Tabler, GitHub</p>
</div>
<div class="resume-job mt-3 pb-2 border-bottom">
  <h6 class="mb-0">Freelance Django Developer <small class="text-muted">— Espere Project</small></h6>
  <p class="mb-1"><small class="text-muted">Remote · 2023 – 2024</small></p>
  <ul class="mb-2">
    <li>Designed and developed a multi-feature platform with blogging, live chat, social networking, and an embedded online compiler.</li>
    <li>Integrated Redis server, WebSockets, and social authentication for real-time communication.</li>
  </ul>
  <p class="mb-0"><strong>Tech:</strong> Python, Django, Redis, WebSockets, PostgreSQL, AWS</p>
</div>'''
    required = False
    help_text = 'Experience section HTML. Paste formatted HTML here.'


@global_preferences_registry.register
class ResumeSkills(LongStringPreference):
    section = resume
    name = 'skills'
    default = '''<div class="row mt-2">
  <div class="col-md-6"><h6>Languages</h6><p class="mb-2">Python</p></div>
  <div class="col-md-6"><h6>Frameworks</h6><p class="mb-2">Django, Django REST Framework, Flask</p></div>
  <div class="col-md-6"><h6>Databases</h6><p class="mb-2">PostgreSQL</p></div>
  <div class="col-md-6"><h6>Tools</h6><p class="mb-2">PyCharm, VS Code</p></div>
  <div class="col-md-6"><h6>Miscellaneous</h6><p class="mb-2">AWS EC2, GIT, Linux, HTML, CSS, Bootstrap</p></div>
</div>'''
    required = False
    help_text = 'Skills section HTML. Paste formatted HTML here.'


@global_preferences_registry.register
class ResumeEducationDegree(StringPreference):
    section = resume
    name = 'education_degree'
    default = 'B.Sc. Computer Science'
    required = False
    help_text = 'Degree name.'


@global_preferences_registry.register
class ResumeEducationUniversity(StringPreference):
    section = resume
    name = 'education_university'
    default = 'Mahatma Jyotiba Phule Rohilkhand University'
    required = False
    help_text = 'University name.'


@global_preferences_registry.register
class AboutExperience(LongStringPreference):
    section = resume
    name = 'about_experience'
    default = '''<ul>
  <li>
    <div class="icon"><i class="bx bx-building-house i-waight-800"></i></div>
    <span class="time">Apr 2024 - Present</span>
    <h5>Senior Django Developer - Aquevix Solutions Pvt Ltd.</h5>
    <p>Working as a Django developer on backend systems: REST APIs with Django REST Framework, PostgreSQL optimization, and Celery background tasks.</p>
  </li>
  <li>
    <div class="icon"><i class="bx bx-wallet-note i-waight-800"></i></div>
    <span class="time">2023 - 2024</span>
    <h5>Freelance Django Developer - Espere Project</h5>
    <p>Delivered backend features, API endpoints, and deployment automation for the Espere Project as a freelance Django developer.</p>
  </li>
  <li>
    <div class="icon"><i class="bx bx-camping i-waight-800"></i></div>
    <span class="time">2023</span>
    <h5>Freelance Django Developer - Taj Mahal Tours</h5>
    <p>Built and deployed <a href="http://tajmahaltourspackages.com/" target="_blank" rel="noopener">tajmahaltourspackages.com</a> using Django &amp; Django REST Framework with PostgreSQL and Celery.</p>
    <p class="mt-2">Role: backend development, API design, payment integration, deployment (AWS EC2).</p>
  </li>
</ul>'''
    required = False
    help_text = 'About section experience HTML. Use Source mode to paste HTML with icons.'