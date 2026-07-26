"""
Forms for the custom admin panel.
"""

from django import forms
from .models import (
    Profile,
    Skill,
    Project,
    Experience,
    Education,
    Testimonial,
    Service,
)


class AdminBaseForm(forms.ModelForm):
    """Base form with consistent styling for all admin forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                continue
            field.widget.attrs.update({
                'class': 'form-control',
            })
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs.update({
                    'rows': 4,
                })


class ProfileAdminForm(AdminBaseForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'title', 'bio', 'email', 'phone', 'location',
            'profile_image', 'cv_file',
            'linkedin_url', 'github_url',
            'instagram_url', 'facebook_url', 'leetcode_url',
            'gmail_address', 'whatsapp_number',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
            'profile_image': forms.ClearableFileInput(),
            'cv_file': forms.ClearableFileInput(),
        }


class SkillAdminForm(AdminBaseForm):
    class Meta:
        model = Skill
        fields = ['name', 'icon_class', 'order']
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g. fab fa-python'}),
        }


class ProjectAdminForm(AdminBaseForm):
    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'description',
            'project_media', 'project_url', 'github_url',
            'technologies_used',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
            'technologies_used': forms.Textarea(attrs={'rows': 4}),
        }


class ExperienceAdminForm(AdminBaseForm):
    class Meta:
        model = Experience
        fields = [
            'company', 'company_website', 'position', 'location',
            'description', 'start_date', 'end_date', 'is_current',
            'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class EducationAdminForm(AdminBaseForm):
    class Meta:
        model = Education
        fields = [
            'institution', 'degree', 'field_of_study', 'location',
            'description', 'start_date', 'end_date', 'is_current',
            'grade', 'is_active', 'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class TestimonialAdminForm(AdminBaseForm):
    class Meta:
        model = Testimonial
        fields = [
            'name', 'position', 'company', 'content', 'image',
            'is_active', 'order',
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class ServiceAdminForm(AdminBaseForm):
    class Meta:
        model = Service
        fields = ['title', 'icon_class', 'description', 'is_active', 'order']
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g. fas fa-code'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
