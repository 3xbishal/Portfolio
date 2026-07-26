"""
Models for the portfolio application.
All content is managed through the Django admin panel.
"""

from django.db import models
from django.utils import timezone
from django.urls import reverse


class Profile(models.Model):
    """Developer profile - single instance for the site owner."""

    name = models.CharField(max_length=100, help_text="Full name")
    title = models.CharField(max_length=100, help_text="Professional title, e.g. 'Full Stack Developer'")
    bio = models.TextField(help_text="Short biography / about me text")
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, help_text="Phone number")
    location = models.CharField(max_length=100, blank=True, help_text="City, Country")
    profile_image = models.ImageField(
        upload_to='profile/',
        blank=True,
        null=True,
        help_text="Profile picture"
    )
    cv_file = models.FileField(
        upload_to='profile/',
        blank=True,
        null=True,
        help_text="Upload your CV/resume"
    )

    # Social links
    linkedin_url = models.URLField(blank=True, help_text="LinkedIn profile URL")
    github_url = models.URLField(blank=True, help_text="GitHub profile URL")
    twitter_url = models.URLField(blank=True, help_text="Twitter/X profile URL")
    stackoverflow_url = models.URLField(blank=True, help_text="Stack Overflow profile URL")
    dribbble_url = models.URLField(blank=True, help_text="Dribbble profile URL")

    # Availability
    available_for_work = models.BooleanField(
        default=True,
        help_text="Whether you are currently available for new opportunities"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only the active profile is shown on the site"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"

    def __str__(self):
        return f"{self.name} - {self.title}"

    def get_absolute_url(self):
        return reverse('home')


class Skill(models.Model):
    """Individual skill (simplified).

    Notes:
    - Removed SkillCategory relationship, proficiency percentage and featured flag
      per request. Skills are now simple named items with an optional icon and
      ordering only.
    """

    name = models.CharField(max_length=50)
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class, e.g. 'fab fa-python'"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")

    class Meta:
        verbose_name = "Skill"
        verbose_name_plural = "Skills"
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class Project(models.Model):
    """Portfolio project entry."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, help_text="URL-friendly slug")
    short_description = models.CharField(
        max_length=300,
        help_text="Brief description shown in project cards"
    )
    description = models.TextField(help_text="Full project description")
    project_image = models.ImageField(
        upload_to='projects/',
        blank=True,
        null=True,
        help_text="Main project image / screenshot"
    )
    project_url = models.URLField(blank=True, help_text="Live demo URL")
    github_url = models.URLField(blank=True, help_text="GitHub repository URL")
    technologies = models.ManyToManyField(
        Skill,
        related_name='projects',
        help_text="Technologies used in this project"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this project on the home page"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active projects are shown"
    )
    date_completed = models.DateField(
        blank=True,
        null=True,
        help_text="When the project was completed"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ['-date_completed', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('project_detail', kwargs={'slug': self.slug})

    @property
    def featured_technologies(self):
        """Return up to 5 technologies for display."""
        return self.technologies.all()[:5]


class ProjectImage(models.Model):
    """Additional images for a project gallery."""

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='gallery_images'
    )
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"Image for {self.project.title}"


class Experience(models.Model):
    """Work experience entry."""

    company = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True)
    company_website = models.URLField(blank=True)
    description = models.TextField(help_text="Job responsibilities and achievements")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(
        default=False,
        help_text="Check if this is your current position"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active entries are shown"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experience"
        ordering = ['-start_date', 'order']

    def __str__(self):
        return f"{self.position} at {self.company}"

    @property
    def duration(self):
        """Return a human-readable duration string."""
        if self.is_current:
            return f"{self.start_date.strftime('%b %Y')} – Present"
        if self.end_date:
            return f"{self.start_date.strftime('%b %Y')} – {self.end_date.strftime('%b %Y')}"
        return self.start_date.strftime('%b %Y')


class Education(models.Model):
    """Education history entry."""

    institution = models.CharField(max_length=150)
    degree = models.CharField(max_length=100, help_text="e.g. Bachelor of Science")
    field_of_study = models.CharField(max_length=100, help_text="e.g. Computer Science")
    location = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, help_text="Additional details")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(
        default=False,
        help_text="Check if you are currently studying here"
    )
    grade = models.CharField(max_length=50, blank=True, help_text="e.g. GPA: 3.8/4.0")
    is_active = models.BooleanField(
        default=True,
        help_text="Only active entries are shown"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
        ordering = ['-start_date', 'order']

    def __str__(self):
        return f"{self.degree} in {self.field_of_study} - {self.institution}"

    @property
    def duration(self):
        """Return a human-readable duration string."""
        if self.is_current:
            return f"{self.start_date.strftime('%b %Y')} – Present"
        if self.end_date:
            return f"{self.start_date.strftime('%b %Y')} – {self.end_date.strftime('%b %Y')}"
        return self.start_date.strftime('%b %Y')


class Testimonial(models.Model):
    """Testimonial from a client, colleague, or supervisor."""

    name = models.CharField(max_length=100)
    position = models.CharField(max_length=100, help_text="e.g. Senior Developer")
    company = models.CharField(max_length=100, blank=True)
    content = models.TextField(help_text="Testimonial text")
    image = models.ImageField(
        upload_to='testimonials/',
        blank=True,
        null=True,
        help_text="Photo of the person"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active testimonials are shown"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")

    class Meta:
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"
        ordering = ['order']

    def __str__(self):
        return f"{self.name} - {self.position}"


class ContactMessage(models.Model):
    """Message received through the contact form."""

    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(
        default=False,
        help_text="Mark as read after reviewing"
    )

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ['-sent_at']

    def __str__(self):
        return f"Message from {self.name} - {self.subject[:50]}"


class Service(models.Model):
    """Service offered by the developer."""

    title = models.CharField(max_length=100)
    description = models.TextField()
    icon_class = models.CharField(
        max_length=50,
        blank=True,
        help_text="Font Awesome icon class, e.g. 'fas fa-code'"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active services are shown"
    )
    order = models.PositiveIntegerField(default=0, help_text="Display order (lower = first)")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['order']

    def __str__(self):
        return self.title
