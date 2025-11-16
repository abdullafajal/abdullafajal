from django.contrib import admin
from .models import ChatLog, ContactMessage, Project

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