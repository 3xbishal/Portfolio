"""
Views for the portfolio application.
All content is fetched from the database (admin-managed).
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView
from django.contrib import messages
from django.core.paginator import Paginator
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


def get_active_profile():
    """Return the active profile or the first profile if none are active."""
    return Profile.objects.filter(is_active=True).first() or Profile.objects.first()


# ---------------------------------------------------------------------------
# Home Page
# ---------------------------------------------------------------------------

def home(request):
    """Home page with featured projects, skills, and testimonials."""
    profile = get_active_profile()
    featured_projects = Project.objects.all()[:6]
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
    return render(request, 'home.html', context)


# ---------------------------------------------------------------------------
# About Page
# ---------------------------------------------------------------------------

def about(request):
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
    return render(request, 'about.html', context)


# ---------------------------------------------------------------------------
# Projects List
# ---------------------------------------------------------------------------

class ProjectListView(ListView):
    """List all projects with pagination."""
    model = Project
    template_name = 'projects.html'
    context_object_name = 'projects'
    paginate_by = 9

    def get_queryset(self):
        return Project.objects.all()

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
        return Project.objects.all()

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

    def get_queryset(self):
        return Experience.objects.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = get_active_profile()
        return context


 # ---------------------------------------------------------------------------
 # Contact Page
 # ---------------------------------------------------------------------------

def contact(request):
    """Contact page with a contact form."""
    profile = get_active_profile()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Your message has been sent successfully! I will get back to you soon.'
            )
            return redirect('contact')
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
    return render(request, 'contact.html', context)
