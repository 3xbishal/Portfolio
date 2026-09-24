"""
URL configuration for the "creative" design of the portfolio, mounted at
/creative/ by portfolio_project/urls.py.

Every route reuses the view from main.views with a creative template, so this
design runs on the same domain, database, forms and admin content as the
default (professional) design. Each design lists the other one as a project:
"Creative Portfolio" on the professional design links here, and
"Professional Portfolio" on this design links back to / (see
Project.DESIGN_SHOWCASES).
"""

from django.urls import path

from . import views

app_name = 'creative'

urlpatterns = [
    path('', views.home,
         {'template_name': 'creative/home.html', 'design': 'creative'},
         name='home'),
    path('about/', views.about, {'template_name': 'creative/about.html'}, name='about'),
    path('projects/',
         views.ProjectListView.as_view(template_name='creative/projects.html', design='creative'),
         name='projects'),
    path('projects/<slug:slug>/',
         views.ProjectDetailView.as_view(template_name='creative/project_detail.html'),
         name='project_detail'),
    path('experience/<slug:slug>/',
         views.ExperienceDetailView.as_view(template_name='creative/experience_detail.html'),
         name='experience_detail'),
    path('contact/', views.contact,
         {'template_name': 'creative/contact.html', 'success_url': 'creative:contact'},
         name='contact'),
    path('parallax/', views.parallax, name='parallax'),
    path('gaming-zone/', views.gaming_zone, name='gaming_zone'),
]
