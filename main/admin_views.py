"""
Custom admin panel views for the portfolio application.
Provides CRUD functionality without using Django's built-in admin.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView, TemplateView
)
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Q, Max

from .models import (
    Profile,
    Skill,
    Project,
    ProjectMedia,
    Experience,
    Education,
    Testimonial,
    Service,
    ContactMessage,
)
from .admin_forms import (
    ProfileAdminForm,
    SkillAdminForm,
    ProjectAdminForm,
    ExperienceAdminForm,
    EducationAdminForm,
    TestimonialAdminForm,
    ServiceAdminForm,
)


# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------

def admin_login_required(view_func):
    """Require the user to be logged in and the single admin (superuser).

    Changed to require is_superuser so only the designated admin can control the
    portfolio. Regular visitors (non-superusers) will not be allowed into this
    custom admin UI.
    """
    decorated = user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='admin_panel:login')(view_func)
    return decorated


class AdminRequiredMixin:
    """Mixin to require superuser access for class-based views."""

    @method_decorator(user_passes_test(lambda u: u.is_active and u.is_superuser, login_url='admin_panel:login'))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


class AdminSearchMixin:
    """Mixin to add simple query-based searching for admin list views."""

    search_fields = []

    def get_search_query(self):
        return self.request.GET.get('q', '').strip()

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.get_search_query()
        if not query or not self.search_fields:
            return queryset

        q_objects = Q()
        for field in self.search_fields:
            q_objects |= Q(**{f'{field}__icontains': query})
        return queryset.filter(q_objects)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.get_search_query()
        return context


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin dashboard with overview statistics."""
    template_name = 'admin_panel/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = Profile.objects.filter(is_active=True).first()
        context['stats'] = {
            'projects': Project.objects.count(),
            'skills': Skill.objects.count(),
            'experiences': Experience.objects.count(),
            'educations': Education.objects.count(),
            'testimonials': Testimonial.objects.count(),
            'services': Service.objects.count(),
            'messages': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        }
        context['recent_projects'] = Project.objects.all()[:5]
        context['recent_messages'] = ContactMessage.objects.all()[:5]
        return context


# ---------------------------------------------------------------------------
# Profile (single instance - edit only)
# ---------------------------------------------------------------------------

class ProfileEditView(AdminRequiredMixin, TemplateView):
    """Edit the active profile instance."""
    template_name = 'admin_panel/profile_edit.html'

    def get_profile(self):
        return Profile.objects.filter(is_active=True).first() or Profile.objects.first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        context['form'] = self.form
        return context

    def get(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.form = ProfileAdminForm(instance=profile)
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        profile = self.get_profile()
        self.form = ProfileAdminForm(
            request.POST, request.FILES, instance=profile
        )
        if self.form.is_valid():
            self.form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('admin_panel:profile_edit')
        messages.error(request, 'Please correct the errors below.')
        return self.get(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Skill CRUD
# ---------------------------------------------------------------------------

class SkillListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Skill
    template_name = 'admin_panel/skill_list.html'
    context_object_name = 'skills'
    paginate_by = 50
    search_fields = ['name']


class SkillCreateView(AdminRequiredMixin, CreateView):
    model = Skill
    form_class = SkillAdminForm
    template_name = 'admin_panel/skill_form.html'
    success_url = reverse_lazy('admin_panel:skill_list')

    def form_valid(self, form):
        messages.success(self.request, 'Skill created successfully.')
        return super().form_valid(form)


class SkillUpdateView(AdminRequiredMixin, UpdateView):
    model = Skill
    form_class = SkillAdminForm
    template_name = 'admin_panel/skill_form.html'
    success_url = reverse_lazy('admin_panel:skill_list')

    def form_valid(self, form):
        messages.success(self.request, 'Skill updated successfully.')
        return super().form_valid(form)


class SkillDeleteView(AdminRequiredMixin, DeleteView):
    model = Skill
    template_name = 'admin_panel/skill_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:skill_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Skill deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Project CRUD
# ---------------------------------------------------------------------------

class ProjectListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Project
    template_name = 'admin_panel/project_list.html'
    context_object_name = 'projects'
    paginate_by = 20
    search_fields = ['title', 'description', 'technologies_used']


class ProjectCreateView(AdminRequiredMixin, CreateView):
    model = Project
    form_class = ProjectAdminForm
    template_name = 'admin_panel/project_form.html'
    success_url = reverse_lazy('admin_panel:project_list')

    def form_valid(self, form):
        messages.success(self.request, 'Project created successfully.')
        return super().form_valid(form)


class ProjectUpdateView(AdminRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectAdminForm
    template_name = 'admin_panel/project_form.html'
    success_url = reverse_lazy('admin_panel:project_list')

    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully.')
        return super().form_valid(form)


class ProjectDeleteView(AdminRequiredMixin, DeleteView):
    model = Project
    template_name = 'admin_panel/project_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:project_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully.')
        return super().delete(request, *args, **kwargs)


class ProjectMediaManageView(AdminRequiredMixin, TemplateView):
    """Manage a project's gallery of extra images/videos (beyond the single
    cover in Project.project_media). Plain POST actions, no Form class --
    same style as the File Manager and mark_message_read below."""
    template_name = 'admin_panel/project_media.html'

    def get_project(self):
        return get_object_or_404(Project, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        context['project'] = project
        context['media_items'] = project.media_items.all()
        return context

    def post(self, request, *args, **kwargs):
        project = self.get_project()
        action = request.POST.get('action')

        if action == 'upload':
            files = request.FILES.getlist('files')
            if not files:
                messages.error(request, 'No files selected.')
            else:
                next_order = (project.media_items.aggregate(Max('order'))['order__max'] or 0) + 1
                for i, f in enumerate(files):
                    ProjectMedia.objects.create(project=project, file=f, order=next_order + i)
                messages.success(request, f'Added {len(files)} file(s).')

        elif action == 'update':
            for media in project.media_items.all():
                caption_key = f'caption_{media.pk}'
                order_key = f'order_{media.pk}'
                if caption_key not in request.POST and order_key not in request.POST:
                    continue
                media.caption = request.POST.get(caption_key, media.caption)
                try:
                    media.order = int(request.POST.get(order_key, media.order))
                except (TypeError, ValueError):
                    pass
                media.save()
            messages.success(request, 'Gallery updated.')

        elif action == 'delete':
            deleted, _ = ProjectMedia.objects.filter(
                pk=request.POST.get('media_id'), project=project,
            ).delete()
            if deleted:
                messages.success(request, 'Item deleted.')
            else:
                messages.error(request, 'Item not found.')

        return redirect('admin_panel:project_media', pk=project.pk)


# ---------------------------------------------------------------------------
# Experience CRUD
# ---------------------------------------------------------------------------

class ExperienceListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Experience
    template_name = 'admin_panel/experience_list.html'
    context_object_name = 'experiences'
    paginate_by = 50
    search_fields = ['position', 'company', 'description']


class ExperienceCreateView(AdminRequiredMixin, CreateView):
    model = Experience
    form_class = ExperienceAdminForm
    template_name = 'admin_panel/experience_form.html'
    success_url = reverse_lazy('admin_panel:experience_list')

    def form_valid(self, form):
        messages.success(self.request, 'Experience entry created successfully.')
        return super().form_valid(form)


class ExperienceUpdateView(AdminRequiredMixin, UpdateView):
    model = Experience
    form_class = ExperienceAdminForm
    template_name = 'admin_panel/experience_form.html'
    success_url = reverse_lazy('admin_panel:experience_list')

    def form_valid(self, form):
        messages.success(self.request, 'Experience entry updated successfully.')
        return super().form_valid(form)


class ExperienceDeleteView(AdminRequiredMixin, DeleteView):
    model = Experience
    template_name = 'admin_panel/experience_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:experience_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Experience entry deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Education CRUD
# ---------------------------------------------------------------------------

class EducationListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Education
    template_name = 'admin_panel/education_list.html'
    context_object_name = 'educations'
    paginate_by = 50
    search_fields = ['degree', 'field_of_study', 'institution']


class EducationCreateView(AdminRequiredMixin, CreateView):
    model = Education
    form_class = EducationAdminForm
    template_name = 'admin_panel/education_form.html'
    success_url = reverse_lazy('admin_panel:education_list')

    def form_valid(self, form):
        messages.success(self.request, 'Education entry created successfully.')
        return super().form_valid(form)


class EducationUpdateView(AdminRequiredMixin, UpdateView):
    model = Education
    form_class = EducationAdminForm
    template_name = 'admin_panel/education_form.html'
    success_url = reverse_lazy('admin_panel:education_list')

    def form_valid(self, form):
        messages.success(self.request, 'Education entry updated successfully.')
        return super().form_valid(form)


class EducationDeleteView(AdminRequiredMixin, DeleteView):
    model = Education
    template_name = 'admin_panel/education_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:education_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Education entry deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Testimonial CRUD
# ---------------------------------------------------------------------------

class TestimonialListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Testimonial
    template_name = 'admin_panel/testimonial_list.html'
    context_object_name = 'testimonials'
    paginate_by = 50
    search_fields = ['name', 'position', 'company', 'content']


class TestimonialCreateView(AdminRequiredMixin, CreateView):
    model = Testimonial
    form_class = TestimonialAdminForm
    template_name = 'admin_panel/testimonial_form.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')

    def form_valid(self, form):
        messages.success(self.request, 'Testimonial created successfully.')
        return super().form_valid(form)


class TestimonialUpdateView(AdminRequiredMixin, UpdateView):
    model = Testimonial
    form_class = TestimonialAdminForm
    template_name = 'admin_panel/testimonial_form.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')

    def form_valid(self, form):
        messages.success(self.request, 'Testimonial updated successfully.')
        return super().form_valid(form)


class TestimonialDeleteView(AdminRequiredMixin, DeleteView):
    model = Testimonial
    template_name = 'admin_panel/testimonial_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:testimonial_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Testimonial deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Service CRUD
# ---------------------------------------------------------------------------

class ServiceListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = Service
    template_name = 'admin_panel/service_list.html'
    context_object_name = 'services'
    paginate_by = 50
    search_fields = ['name', 'description']


class ServiceCreateView(AdminRequiredMixin, CreateView):
    model = Service
    form_class = ServiceAdminForm
    template_name = 'admin_panel/service_form.html'
    success_url = reverse_lazy('admin_panel:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service created successfully.')
        return super().form_valid(form)


class ServiceUpdateView(AdminRequiredMixin, UpdateView):
    model = Service
    form_class = ServiceAdminForm
    template_name = 'admin_panel/service_form.html'
    success_url = reverse_lazy('admin_panel:service_list')

    def form_valid(self, form):
        messages.success(self.request, 'Service updated successfully.')
        return super().form_valid(form)


class ServiceDeleteView(AdminRequiredMixin, DeleteView):
    model = Service
    template_name = 'admin_panel/service_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:service_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Service deleted successfully.')
        return super().delete(request, *args, **kwargs)


# ---------------------------------------------------------------------------
# Contact Messages
# ---------------------------------------------------------------------------

class ContactMessageListView(AdminRequiredMixin, AdminSearchMixin, ListView):
    model = ContactMessage
    template_name = 'admin_panel/contactmessage_list.html'
    context_object_name = 'messages_list'
    paginate_by = 50
    search_fields = ['name', 'email', 'subject', 'message']


class ContactMessageDetailView(AdminRequiredMixin, DetailView):
    model = ContactMessage
    template_name = 'admin_panel/contactmessage_detail.html'
    context_object_name = 'message_obj'


class ContactMessageDeleteView(AdminRequiredMixin, DeleteView):
    model = ContactMessage
    template_name = 'admin_panel/contactmessage_confirm_delete.html'
    success_url = reverse_lazy('admin_panel:contactmessage_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Message deleted successfully.')
        return super().delete(request, *args, **kwargs)


@admin_login_required
def mark_message_read(request, pk):
    """Mark a contact message as read."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = True
    msg.save()
    messages.success(request, 'Message marked as read.')
    return redirect('admin_panel:contactmessage_list')


@admin_login_required
def mark_message_unread(request, pk):
    """Mark a contact message as unread."""
    msg = get_object_or_404(ContactMessage, pk=pk)
    msg.is_read = False
    msg.save()
    messages.success(request, 'Message marked as unread.')
    return redirect('admin_panel:contactmessage_list')


# ---------------------------------------------------------------------------
# Logout
# ---------------------------------------------------------------------------

def admin_logout(request):
    """Log out the admin user."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('admin_panel:login')
