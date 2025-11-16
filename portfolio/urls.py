from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'portfolio'

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("projects/", views.projects, name="projects"),
    path("contact/", views.contact_view, name="contact"),
    path("resume/", views.resume_view, name="resume"),
    path("api/agent/query/", views.agent_query, name="agent_query"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)