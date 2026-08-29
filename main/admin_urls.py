"""
URL configuration for the custom admin panel.
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from . import admin_views
from . import admin_filemanager_views as fmv
from . import admin_github_views as ghv

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
    path('projects/<int:pk>/media/', admin_views.ProjectMediaManageView.as_view(), name='project_media'),

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

    # File Manager (sandboxed to the project/media/static roots; see main/file_manager.py)
    path('files/', fmv.file_manager, name='fm_list'),
    path('files/upload/', fmv.file_upload, name='fm_upload'),
    path('files/mkdir/', fmv.file_mkdir, name='fm_mkdir'),
    path('files/rename/', fmv.file_rename, name='fm_rename'),
    path('files/delete/', fmv.file_delete, name='fm_delete'),
    path('files/clipboard/', fmv.file_clipboard, name='fm_clipboard'),
    path('files/paste/', fmv.file_paste, name='fm_paste'),
    path('files/download/', fmv.file_download, name='fm_download'),
    path('files/download-zip/', fmv.file_download_zip, name='fm_download_zip'),
    path('files/edit/', fmv.file_edit, name='fm_edit'),

    # GitHub repo browser (read-only via the GitHub API; see main/github_client.py)
    path('github/', ghv.github_repo_list, name='github_repo_list'),
    path('github/<str:owner>/<str:repo>/', ghv.github_tree, name='github_tree'),
    path('github/<str:owner>/<str:repo>/file/', ghv.github_file, name='github_file'),
    path('github/<str:owner>/<str:repo>/commits/', ghv.github_commits, name='github_commits'),
    path('github/<str:owner>/<str:repo>/download/', ghv.github_download, name='github_download'),
]
