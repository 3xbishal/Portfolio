"""
Views for the portfolio application.
All content is fetched from the database (admin-managed).

The same views serve both site designs: "professional", the default
(templates/*.html, routed by main/urls.py), and "creative" under /creative/
(templates/creative/*.html, routed by main/creative_urls.py). The creative
URLs just pass a different template name and design='creative', so both
designs always share the same data, forms and behaviour; the design name only
decides which built-in showcase project is listed (see
ProjectQuerySet.for_design).
"""

import logging

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.core.mail import EmailMessage
from django.db.models import Q

from .models import (
    Profile,
    Skill,
    Project,
    Experience,
    Education,
    Testimonial,
    ContactMessage,
    Service,
)
from .forms import ContactForm

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Parallax Portfolio Page
# ---------------------------------------------------------------------------

def parallax(request):
    """Full portfolio page with parallax scrolling effects (creative design)."""
    profile = get_active_profile()
    projects = Project.objects.for_design('creative')
    experiences = Experience.objects.all()
    educations = Education.objects.filter(is_active=True)
    skills = Skill.objects.all()
    services = Service.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)

    context = {
        'profile': profile,
        'projects': projects,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
        'services': services,
        'testimonials': testimonials,
    }
    return render(request, 'creative/parallax.html', context)


def gaming_zone(request):
    """A lightweight collection of browser games (creative design)."""
    return render(request, 'creative/gaming_zone.html', {'profile': get_active_profile()})


def get_active_profile():
    """Return the active profile or the first profile if none are active."""
    return Profile.objects.filter(is_active=True).first() or Profile.objects.first()


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------

def home(request, template_name='home.html', design='professional'):
    """Home page with featured projects, skills, and testimonials."""
    profile = get_active_profile()
    featured_projects = Project.objects.for_design(design).prefetch_related('media_items')[:6]
    skills = Skill.objects.all()
    services = Service.objects.filter(is_active=True)
    testimonials = Testimonial.objects.filter(is_active=True)[:6]
    experiences = Experience.objects.all()[:3]

    context = {
        'profile': profile,
        'featured_projects': featured_projects,
        'skills': skills,
        'services': services,
        'testimonials': testimonials,
        'experiences': experiences,
    }
    return render(request, template_name, context)


# ---------------------------------------------------------------------------
# About Page
# ---------------------------------------------------------------------------

def about(request, template_name='about.html'):
    """About page with profile, experience, and education."""
    profile = get_active_profile()
    experiences = Experience.objects.all()
    educations = Education.objects.filter(is_active=True)
    skills = Skill.objects.all()

    context = {
        'profile': profile,
        'experiences': experiences,
        'educations': educations,
        'skills': skills,
    }
    return render(request, template_name, context)


# ---------------------------------------------------------------------------
# Projects List
# ---------------------------------------------------------------------------

class ProjectListView(ListView):
    """List all projects with pagination."""
    model = Project
    template_name = 'projects.html'
    context_object_name = 'projects'
    paginate_by = 9
    design = 'professional'

    def get_queryset(self):
        return Project.objects.for_design(self.design).prefetch_related('media_items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_active_profile()
        return context


# ---------------------------------------------------------------------------
# Project Detail
# ---------------------------------------------------------------------------

class ProjectDetailView(DetailView):
    """Detail view for a single project."""
    model = Project
    template_name = 'project_detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Project.objects.prefetch_related('media_items').all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_active_profile()
        return context


 # ---------------------------------------------------------------------------
 # Experience Detail
 # ---------------------------------------------------------------------------

class ExperienceDetailView(DetailView):
    """Detail view for a single experience."""
    model = Experience
    template_name = 'experience_detail.html'
    context_object_name = 'experience'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Experience.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_active_profile()
        return context


 # ---------------------------------------------------------------------------
 # Contact Page
 # ---------------------------------------------------------------------------

def contact(request, template_name='contact.html', success_url='contact'):
    """Contact page with a contact form. `success_url` is the URL name to
    redirect to after a successful submission, so each design returns the
    visitor to its own contact page."""
    profile = get_active_profile()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact_message = form.save()
            notify_email = profile.gmail_address if profile else ''
            if notify_email:
                try:
                    EmailMessage(
                        subject=f'New portfolio message: {contact_message.subject}',
                        body=(
                            f'From: {contact_message.name} <{contact_message.email}>\n\n'
                            f'{contact_message.message}'
                        ),
                        to=[notify_email],
                        reply_to=[contact_message.email],
                    ).send(fail_silently=False)
                except Exception:
                    logger.exception('Failed to send contact form notification email')
            messages.success(
                request,
                'Your message has been sent successfully! I will get back to you soon.'
            )
            return redirect(success_url)
        else:
            messages.error(
                request,
                'There was an error sending your message. Please check the form and try again.'
            )
    else:
        form = ContactForm()

    context = {
        'profile': profile,
        'form': form,
    }
    return render(request, template_name, context)
