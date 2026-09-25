"""
Forms for the custom admin panel.

Labels and help texts are written for the site owner, in plain language;
they only change what the admin forms show, not the database.
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

ORDER_HELP = 'Lower numbers are shown first.'
ICON_HELP = 'Font Awesome class, e.g. "fab fa-python". Leave blank for no icon.'
SHOW_LABEL = 'Show on website'


def _date_input():
    # <input type="date"> only accepts ISO dates, so pin the format.
    return forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'})


class AdminBaseForm(forms.ModelForm):
    """Base form with consistent styling for all admin forms."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs['class'] = 'form-check-input'
            elif isinstance(widget, forms.Select):
                widget.attrs['class'] = 'form-select'
            else:
                widget.attrs['class'] = 'form-control'
            if isinstance(widget, forms.ClearableFileInput):
                widget.template_name = 'widgets/admin_file_input.html'
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 4)


class ProfileAdminForm(AdminBaseForm):
    class Meta:
        model = Profile
        fields = [
            'name', 'title', 'bio', 'email', 'phone', 'location', 'company',
            'profile_image', 'logo', 'cv_file',
            'linkedin_url', 'github_url',
            'instagram_url', 'facebook_url', 'leetcode_url',
            'gmail_address', 'whatsapp_number',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
            'company': forms.TextInput(attrs={'placeholder': 'e.g. Acme Corp'}),
            'whatsapp_number': forms.TextInput(attrs={'placeholder': 'e.g. 8801XXXXXXXXX'}),
        }
        labels = {
            'name': 'Full name',
            'title': 'Job title',
            'bio': 'About you',
            'email': 'Public email',
            'phone': 'Phone',
            'location': 'Location',
            'company': 'Company or brand name',
            'profile_image': 'Profile photo',
            'logo': 'Logo',
            'cv_file': 'CV / résumé',
            'linkedin_url': 'LinkedIn',
            'github_url': 'GitHub',
            'instagram_url': 'Instagram',
            'facebook_url': 'Facebook',
            'leetcode_url': 'LeetCode',
            'gmail_address': 'Notification email',
            'whatsapp_number': 'WhatsApp number',
        }
        help_texts = {
            'name': '',
            'title': 'Shown under your name, e.g. "Web Developer".',
            'phone': 'Shown on the About and Contact pages.',
            'bio': 'A short introduction shown on the home and About pages.',
            'email': 'Shown on the website so clients can contact you.',
            'location': 'City and country, e.g. "Uttara, Dhaka".',
            'company': 'Shown in the website header.',
            'logo': 'Shown next to the name in the website header.',
            'cv_file': 'PDF recommended. Visitors can download it from the website.',
            'gmail_address': 'New messages from the contact form are emailed to this address.',
            'whatsapp_number': 'Include the country code, without "+" or spaces.',
        }


class SkillAdminForm(AdminBaseForm):
    class Meta:
        model = Skill
        fields = ['name', 'icon_class', 'order']
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g. fab fa-python'}),
        }
        labels = {'name': 'Skill', 'icon_class': 'Icon', 'order': 'Display order'}
        help_texts = {'icon_class': ICON_HELP, 'order': ORDER_HELP}


class ProjectAdminForm(AdminBaseForm):
    class Meta:
        model = Project
        fields = [
            'title', 'slug', 'description',
            'project_media', 'project_url', 'github_url',
            'technologies_used',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 7}),
            'technologies_used': forms.TextInput(attrs={'placeholder': 'e.g. Django, React, PostgreSQL'}),
        }
        labels = {
            'title': 'Project name',
            'slug': 'Web address (slug)',
            'description': 'Description',
            'project_media': 'Cover image or video',
            'project_url': 'Live site URL',
            'github_url': 'Source code URL',
            'technologies_used': 'Technologies',
        }
        help_texts = {
            'slug': 'Used in the project page address. Leave blank to create it from the name.',
            'description': 'What the project does and your role. Each line is shown as a separate line.',
            'project_media': 'Shown on the project card. Add more under "Screenshots & media" after saving.',
            'project_url': 'Link to the working project, if it is online.',
            'github_url': 'Link to the code repository, if it is public.',
            'technologies_used': 'Separate with commas. The first four are shown on the project card.',
        }


class ExperienceAdminForm(AdminBaseForm):
    class Meta:
        model = Experience
        fields = [
            'company', 'company_website', 'position', 'slug', 'location',
            'description', 'start_date', 'end_date', 'is_current',
            'order',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 7}),
            'start_date': _date_input(),
            'end_date': _date_input(),
        }
        labels = {
            'company': 'Company',
            'company_website': 'Company website',
            'position': 'Job title',
            'slug': 'Web address (slug)',
            'location': 'Location',
            'description': 'Responsibilities and achievements',
            'start_date': 'Start date',
            'end_date': 'End date',
            'is_current': 'I currently work here',
            'order': 'Display order',
        }
        help_texts = {
            'slug': 'Used in the page address. Leave blank to create it from the job title and company.',
            'description': 'One point per line.',
            'end_date': 'Leave blank if you still work here.',
            'is_current': '',
            'order': ORDER_HELP,
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
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_date': _date_input(),
            'end_date': _date_input(),
        }
        labels = {
            'institution': 'Institution',
            'degree': 'Degree',
            'field_of_study': 'Field of study',
            'location': 'Location',
            'description': 'Details',
            'start_date': 'Start date',
            'end_date': 'End date',
            'is_current': 'I am currently studying here',
            'grade': 'Result',
            'is_active': SHOW_LABEL,
            'order': 'Display order',
        }
        help_texts = {
            'degree': 'e.g. "Bachelor of Science" or "Diploma".',
            'field_of_study': 'e.g. "Computer Science".',
            'description': '',
            'end_date': 'Leave blank if you are still studying.',
            'is_current': '',
            'is_active': '',
            'grade': 'e.g. "CGPA 3.80 / 4.00".',
            'order': ORDER_HELP,
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
        labels = {
            'name': 'Name',
            'position': 'Job title',
            'company': 'Company',
            'content': 'Testimonial',
            'image': 'Photo',
            'is_active': SHOW_LABEL,
            'order': 'Display order',
        }
        help_texts = {
            'content': 'Their words, exactly as they gave them.',
            'position': 'e.g. "Founder" or "Project Manager".',
            'image': '',
            'is_active': '',
            'order': ORDER_HELP,
        }


class ServiceAdminForm(AdminBaseForm):
    class Meta:
        model = Service
        fields = ['title', 'icon_class', 'description', 'is_active', 'order']
        widgets = {
            'icon_class': forms.TextInput(attrs={'placeholder': 'e.g. fas fa-code'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'title': 'Service',
            'icon_class': 'Icon',
            'description': 'Description',
            'is_active': SHOW_LABEL,
            'order': 'Display order',
        }
        help_texts = {
            'title': 'e.g. "Web application development".',
            'icon_class': ICON_HELP,
            'description': 'One or two sentences about what you offer.',
            'is_active': '',
            'order': ORDER_HELP,
        }
