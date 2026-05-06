from django.contrib import admin
from .models import ChatLog, ContactMessage, Project, ResumeFile

from dynamic_preferences.admin import GlobalPreferenceAdmin
from dynamic_preferences.models import GlobalPreferenceModel


# ── Override Dynamic Preferences admin to add CKEditor on textareas ──────────

class CKEditorGlobalPreferenceAdmin(GlobalPreferenceAdmin):
    """Extends the default preferences admin with CKEditor for textarea fields."""

    class Media:
        js = (
            'https://cdn.ckeditor.com/4.22.1/full/ckeditor.js',
        )

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['ckeditor_init'] = True
        return super().change_view(request, object_id, form_url, extra_context)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['ckeditor_init'] = True
        return super().add_view(request, form_url, extra_context)


# Unregister the default and register our custom one
admin.site.unregister(GlobalPreferenceModel)
admin.site.register(GlobalPreferenceModel, CKEditorGlobalPreferenceAdmin)

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Admin view for Project model.
    """
    list_display = ('title', 'tech_stack', 'display_order')
    search_fields = ('title', 'tech_stack', 'description')
    list_editable = ('display_order',)


@admin.register(ChatLog)
class ChatLogAdmin(admin.ModelAdmin):
    """
    Admin view for ChatLog model.
    """
    list_display = ('timestamp', 'user_message', 'agent_response')
    list_filter = ('timestamp',)
    search_fields = ('user_message', 'agent_response')
    readonly_fields = ('timestamp', 'user_message', 'agent_response')

    def has_add_permission(self, request):
        # Disable manual creation of logs in the admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deletion if needed, but can be restricted
        return True


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin view for ContactMessage model.
    """
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('name', 'email', 'subject', 'message', 'created_at')

    def has_add_permission(self, request):
        # Disable manual creation of contact messages in the admin
        return False

    def has_delete_permission(self, request, obj=None):
        # Allow deletion if needed
        return True


@admin.register(ResumeFile)
class ResumeFileAdmin(admin.ModelAdmin):
    """Admin view for ResumeFile model."""
    list_display = ('file', 'uploaded_at')
    readonly_fields = ('uploaded_at',)