"""
URL configuration for the custom admin panel.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views

app_name = 'admin_panel'

urlpatterns = [
    # Authentication
    path('login/', auth_views.LoginView.as_view(
        template_name='admin_panel/login.html'
    ), name='login'),
    path('logout/', admin_views.admin_logout, name='logout'),

    # Dashboard
    path('', admin_views.AdminDashboardView.as_view(), name='dashboard'),

    # Profile (single instance)
    path('profile/', admin_views.ProfileEditView.as_view(), name='profile_edit'),

    # Skill CRUD
    path('skills/', admin_views.SkillListView.as_view(), name='skill_list'),
    path('skills/add/', admin_views.SkillCreateView.as_view(), name='skill_add'),
    path('skills/<int:pk>/edit/', admin_views.SkillUpdateView.as_view(), name='skill_edit'),
    path('skills/<int:pk>/delete/', admin_views.SkillDeleteView.as_view(), name='skill_delete'),

    # Project CRUD
    path('projects/', admin_views.ProjectListView.as_view(), name='project_list'),
    path('projects/add/', admin_views.ProjectCreateView.as_view(), name='project_add'),
    path('projects/<int:pk>/edit/', admin_views.ProjectUpdateView.as_view(), name='project_edit'),
    path('projects/<int:pk>/delete/', admin_views.ProjectDeleteView.as_view(), name='project_delete'),

    # Experience CRUD
    path('experience/', admin_views.ExperienceListView.as_view(), name='experience_list'),
    path('experience/add/', admin_views.ExperienceCreateView.as_view(), name='experience_add'),
    path('experience/<int:pk>/edit/', admin_views.ExperienceUpdateView.as_view(), name='experience_edit'),
    path('experience/<int:pk>/delete/', admin_views.ExperienceDeleteView.as_view(), name='experience_delete'),

    # Education CRUD
    path('education/', admin_views.EducationListView.as_view(), name='education_list'),
    path('education/add/', admin_views.EducationCreateView.as_view(), name='education_add'),
    path('education/<int:pk>/edit/', admin_views.EducationUpdateView.as_view(), name='education_edit'),
    path('education/<int:pk>/delete/', admin_views.EducationDeleteView.as_view(), name='education_delete'),

    # Testimonial CRUD
    path('testimonials/', admin_views.TestimonialListView.as_view(), name='testimonial_list'),
    path('testimonials/add/', admin_views.TestimonialCreateView.as_view(), name='testimonial_add'),
    path('testimonials/<int:pk>/edit/', admin_views.TestimonialUpdateView.as_view(), name='testimonial_edit'),
    path('testimonials/<int:pk>/delete/', admin_views.TestimonialDeleteView.as_view(), name='testimonial_delete'),

    # Service CRUD
    path('services/', admin_views.ServiceListView.as_view(), name='service_list'),
    path('services/add/', admin_views.ServiceCreateView.as_view(), name='service_add'),
    path('services/<int:pk>/edit/', admin_views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<int:pk>/delete/', admin_views.ServiceDeleteView.as_view(), name='service_delete'),

    # Contact Messages
    path('messages/', admin_views.ContactMessageListView.as_view(), name='contactmessage_list'),
    path('messages/<int:pk>/', admin_views.ContactMessageDetailView.as_view(), name='contactmessage_detail'),
    path('messages/<int:pk>/delete/', admin_views.ContactMessageDeleteView.as_view(), name='contactmessage_delete'),
    path('messages/<int:pk>/mark-read/', admin_views.mark_message_read, name='message_mark_read'),
    path('messages/<int:pk>/mark-unread/', admin_views.mark_message_unread, name='message_mark_unread'),
]
