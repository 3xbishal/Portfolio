"""
URL configuration for the portfolio application.
"""

from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('projects/', views.ProjectListView.as_view(), name='projects'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),
    path('experience/<slug:slug>/', views.ExperienceDetailView.as_view(), name='experience_detail'),
    path('contact/', views.contact, name='contact'),
    # These pages belong to the creative design; old links keep working.
    path('parallax/', RedirectView.as_view(pattern_name='creative:parallax'), name='parallax'),
    path('gaming-zone/', RedirectView.as_view(pattern_name='creative:gaming_zone'), name='gaming_zone'),
]
