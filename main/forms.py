"""
Forms for the portfolio application.
"""

from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Form for visitors to send messages via the contact page."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. Jane Smith',
                'autocomplete': 'name',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'you@company.com',
                'autocomplete': 'email',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g. New website for my business',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'A few lines about what you need, your goals and your timeline.',
                'rows': 6,
                'required': True,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add is-invalid class to fields with errors for Bootstrap styling
        for field_name, field in self.fields.items():
            if self.errors.get(field_name):
                field.widget.attrs['class'] += ' is-invalid'
