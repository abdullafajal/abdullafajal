from django.db import models
from django.utils.text import slugify

class Project(models.Model):
    """
    Represents a single portfolio project.
    """
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    description = models.TextField()
    tech_stack = models.CharField(max_length=200)
    image = models.ImageField(upload_to='project_images/', blank=True, null=True, help_text="Optional image for the project.")
    image_url = models.URLField(blank=True, help_text="Use this if you are hosting the image externally.")
    link = models.URLField(blank=True)
    display_order = models.PositiveIntegerField(default=0, help_text="Projects with a lower number will be displayed first.")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['display_order', 'title']

class ChatLog(models.Model):
    """
    Stores a record of a single user-agent interaction.
    """
    user_message = models.TextField(help_text="The user's message or prompt.")
    agent_response = models.TextField(help_text="The agent's generated response.")
    timestamp = models.DateTimeField(auto_now_add=True, help_text="The date and time the interaction occurred.")

    def __str__(self):
        return f"Message from user at {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Chat Log"
        verbose_name_plural = "Chat Logs"


class ContactMessage(models.Model):
    """
    Stores messages submitted through the contact form.
    """
    name = models.CharField(max_length=150)
    email = models.EmailField()
    subject = models.CharField(max_length=200, blank=True, default='')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact from {self.name} <{self.email}> at {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"


class ResumeFile(models.Model):
    """Stores the uploaded resume PDF. The latest upload is used for download buttons."""
    file = models.FileField(upload_to='resumes/', help_text='Upload your resume PDF.')
    uploaded_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = "Resume File"
        verbose_name_plural = "Resume Files"

    def __str__(self):
        return f"Resume uploaded {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
