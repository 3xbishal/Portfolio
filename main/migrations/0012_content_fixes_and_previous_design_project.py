"""
Content clean-up for the redesigned site, plus the built-in project that
links to the previous design (/classic/).

Everything here is conservative so it is safe to run on any copy of the
database (local or the live cPanel one):
- a field is corrected only while it still holds the exact old value, so
  anything already edited in the admin panel is left alone;
- records are only created when they don't exist yet.
Reversing the migration leaves the content as it is.
"""
import datetime

from django.db import migrations

PREVIOUS_DESIGN_SLUG = 'portfolio-previous-design'

OLD_BIO = (
    'Backend developer with 2 year of professional experience in Python, Django, and Django REST Framework.\r\n'
    'Skilled in building RESTful APIs, designing databases, developing secure backend systems, and creating template-based\r\n'
    'web applications. Familiar with frontend technologies to enable effective full-stack collaboration'
)
NEW_BIO = (
    'Backend developer with 2 years of professional experience in Python, Django, and Django REST Framework. '
    'Skilled in building RESTful APIs, designing databases, developing secure backend systems, and creating '
    'template-based web applications. Familiar with frontend technologies to enable effective full-stack collaboration.'
)

# (field, exact old value, new value)
PROFILE_FIXES = [
    ('name', 'MD MAKSUD HASAN BISHAL', 'Md Maksud Hasan Bishal'),
    ('email', '3xbishal@gmial.com', '3xbishal@gmail.com'),       # typo: "gmial"
    ('phone', '01703055918', '+880 1703-055918'),                # international format
    ('whatsapp_number', '01703055918', '8801703055918'),         # wa.me needs country code
    ('bio', OLD_BIO, NEW_BIO),                                   # grammar + broken line wraps
]

# Stray date lines sat in the middle of bullet lists; move them to the end.
PROJECT_DESCRIPTION_FIXES = {
    'gym': ('\r\nNovember 2024\r\n', '\r\n', 'Date: November 2024'),
    'origin_academy': ('\r\nJuly 2025\r\n', '\r\n', 'Date: July 2025'),
}

# name -> (icon, order). Existing skills only get an order if they have none.
SKILLS = {
    'Python': ('fa-brands fa-python', 1),
    'Django': ('fa-solid fa-d', 2),
    'Django REST Framework': ('fas fa-plug', 3),
    'JavaScript': ('fa-brands fa-js', 4),
    'MySQL': ('fas fa-database', 5),
    'PostgreSQL': ('fas fa-database', 6),
    'Git': ('fa-brands fa-git-alt', 7),
    'cPanel': ('fa-brands fa-cpanel', 8),
}

SERVICES = [
    ('Web application development',
     'Custom web applications built with Python and Django, from planning and database design '
     'to a secure, working product that is ready to launch.',
     'fas fa-laptop-code'),
    ('REST API development',
     'Well-structured APIs with Django REST Framework for web apps, mobile apps and third-party '
     'integrations, with authentication and role-based access built in.',
     'fas fa-plug'),
    ('Database design & deployment',
     'Reliable MySQL and PostgreSQL databases, plus deployment to cPanel hosting with domain and '
     'DNS set up, so your project runs smoothly after launch.',
     'fas fa-database'),
]

PREVIOUS_DESIGN_PROJECT = {
    'title': 'Portfolio – Previous Design',
    'description': (
        'The earlier design of this portfolio website, kept online so visitors can compare it with the current one.\r\n'
        '• Runs on the same Django backend, database and admin panel as this site; only the front end is different.\r\n'
        '• Animated canvas background with floating particles that connect as they move.\r\n'
        '• Terminal-inspired sections, scroll animations and a dark mode toggle.\r\n'
        '• A parallax storytelling page and a small browser gaming zone (Snake, Breakout and tic-tac-toe).'
    ),
    'technologies_used': 'Django, Python, MySQL, Bootstrap 5, JavaScript, Canvas API, AOS',
}


def forwards(apps, schema_editor):
    Profile = apps.get_model('main', 'Profile')
    Project = apps.get_model('main', 'Project')
    Experience = apps.get_model('main', 'Experience')
    Skill = apps.get_model('main', 'Skill')
    Service = apps.get_model('main', 'Service')

    # --- Profile ---
    for field, old, new in PROFILE_FIXES:
        Profile.objects.filter(**{field: old}).update(**{field: new})

    # --- Projects ---
    Project.objects.filter(slug='gym', title='Gym').update(title='Gym Management System')
    for slug, (stray, replacement, suffix) in PROJECT_DESCRIPTION_FIXES.items():
        for project in Project.objects.filter(slug=slug):
            if stray in project.description:
                project.description = (
                    project.description.replace(stray, replacement, 1).rstrip() + '\r\n' + suffix
                )
                project.save(update_fields=['description'])

    # --- Experience: one bullet was missing its marker ---
    for exp in Experience.objects.all():
        fixed = exp.description.replace(
            '\r\nIntegrated user authentication', '\r\n• Integrated user authentication')
        if fixed != exp.description:
            exp.description = fixed
            exp.save(update_fields=['description'])

    # --- Skills ---
    Skill.objects.filter(name='Cpanel').update(name='cPanel')
    for name, (icon, order) in SKILLS.items():
        skill = Skill.objects.filter(name__iexact=name).first()
        if skill is None:
            Skill.objects.create(name=name, icon_class=icon, order=order)
        elif skill.order == 0:
            skill.order = order
            skill.save(update_fields=['order'])

    # --- Services (only when none have been added yet) ---
    if not Service.objects.exists():
        for order, (title, description, icon) in enumerate(SERVICES, start=1):
            Service.objects.create(title=title, description=description, icon_class=icon, order=order)

    # --- Built-in "previous design" project ---
    if not Project.objects.filter(slug=PREVIOUS_DESIGN_SLUG).exists():
        project = Project.objects.create(slug=PREVIOUS_DESIGN_SLUG, **PREVIOUS_DESIGN_PROJECT)
        # Projects are listed newest first; place this one after the real
        # client work so that stays at the top.
        oldest = Project.objects.exclude(pk=project.pk).order_by('created_at').first()
        if oldest is not None:
            Project.objects.filter(pk=project.pk).update(
                created_at=oldest.created_at - datetime.timedelta(minutes=1))


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_projectmedia_delete_projectimage'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
