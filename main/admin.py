"""
Admin configuration for the portfolio application.
All portfolio content is managed through the Django admin panel.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile,
    Skill,
    Project,
    ProjectMedia,
    Experience,
    Education,
    Testimonial,
    ContactMessage,
    Service,
)


# ---------------------------------------------------------------------------
# Profile Admin
# ---------------------------------------------------------------------------

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'email', 'location', 'is_active']
    list_editable = ['is_active']
    list_filter = ['is_active']
    search_fields = ['name', 'title', 'email', 'location']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'title', 'bio', 'email', 'phone', 'location', 'company')
        }),
        ('Media', {
            'fields': ('profile_image', 'logo', 'cv_file')
        }),
        ('Social Links', {
            'fields': (
                'linkedin_url', 'github_url', 'instagram_url',
                'facebook_url', 'leetcode_url', 'gmail_address', 'whatsapp_number'
            )
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )

    def has_add_permission(self, request):
        """Only allow one profile instance."""
        if self.model.objects.count() >= 1:
            return False
        return super().has_add_permission(request)


# ---------------------------------------------------------------------------
# Skill Category Admin
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Skill Admin
# ---------------------------------------------------------------------------

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']
    search_fields = ['name']


# ---------------------------------------------------------------------------
# Project Image Inline
# ---------------------------------------------------------------------------

class ProjectMediaInline(admin.TabularInline):
    model = ProjectMedia
    extra = 1
    fields = ('file', 'caption', 'order')


# ---------------------------------------------------------------------------
# Project Admin
# ---------------------------------------------------------------------------

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'tech_list']
    search_fields = ['title', 'description', 'technologies_used']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectMediaInline]
    fieldsets = (
        ('Project Details', {
            'fields': ('title', 'slug', 'description')
        }),
        ('Media & Links', {
            'fields': ('project_media', 'project_url', 'github_url')
        }),
        ('Technologies', {
            'fields': ('technologies_used',)
        }),
    )

    def tech_list(self, obj):
        """Display a preview of the technologies used text."""
        if not obj.technologies_used:
            return '-'
        return obj.technologies_used if len(obj.technologies_used) <= 70 else f"{obj.technologies_used[:67]}..."
    tech_list.short_description = 'Technologies'


# ---------------------------------------------------------------------------
# Experience Admin
# ---------------------------------------------------------------------------

@admin.register(Experience)
class ExperienceAdmin(admin.ModelAdmin):
    list_display = ['position', 'company', 'location', 'is_current', 'duration', 'slug', 'order']
    list_editable = ['is_current', 'order']
    list_filter = ['is_current', 'company']
    search_fields = ['position', 'company', 'description', 'slug']
    prepopulated_fields = {'slug': ('position', 'company')}
    fieldsets = (
        ('Company Info', {
            'fields': ('company', 'company_website', 'position', 'slug', 'location')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('Order', {
            'fields': ('order',)
        }),
    )

    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'


# ---------------------------------------------------------------------------
# Education Admin
# ---------------------------------------------------------------------------

@admin.register(Education)
class EducationAdmin(admin.ModelAdmin):
    list_display = ['degree', 'field_of_study', 'institution', 'location', 'is_current', 'is_active', 'duration', 'order']
    list_editable = ['is_current', 'is_active', 'order']
    list_filter = ['is_current', 'is_active', 'institution']
    search_fields = ['degree', 'field_of_study', 'institution']
    fieldsets = (
        ('Institution Info', {
            'fields': ('institution', 'degree', 'field_of_study', 'location')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date', 'is_current')
        }),
        ('Details', {
            'fields': ('grade', 'description')
        }),
        ('Visibility', {
            'fields': ('is_active', 'order')
        }),
    )

    def duration(self, obj):
        return obj.duration
    duration.short_description = 'Duration'


# ---------------------------------------------------------------------------
# Testimonial Admin
# ---------------------------------------------------------------------------

@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['name', 'position', 'company', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active', 'company']
    search_fields = ['name', 'position', 'company', 'content']
    fieldsets = (
        ('Person Info', {
            'fields': ('name', 'position', 'company', 'image')
        }),
        ('Testimonial', {
            'fields': ('content',)
        }),
        ('Visibility', {
            'fields': ('is_active', 'order')
        }),
    )


# ---------------------------------------------------------------------------
# Contact Message Admin
# ---------------------------------------------------------------------------

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'sent_at', 'is_read']
    list_editable = ['is_read']
    list_filter = ['is_read', 'sent_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['name', 'email', 'subject', 'message', 'sent_at']

    actions = ['mark_as_read', 'mark_as_unread']

    @admin.action(description='Mark selected messages as read')
    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = 'Mark selected messages as read'

    @admin.action(description='Mark selected messages as unread')
    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = 'Mark selected messages as unread'

    def has_add_permission(self, request):
        """Messages are created via the contact form, not admin."""
        return False


# ---------------------------------------------------------------------------
# Service Admin
# ---------------------------------------------------------------------------

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
    fieldsets = (
        ('Service Info', {
            'fields': ('title', 'icon_class', 'description')
        }),
        ('Visibility', {
            'fields': ('is_active', 'order')
        }),
    )
