"""
Name the two site designs by style instead of age, and give each one a
showcase project that the other design lists (see Project.DESIGN_SHOWCASES):

- "Creative Portfolio" (slug creative-portfolio) links to /creative/ and is
  listed on the professional design.
- "Professional Portfolio" (slug professional-portfolio) links to / and is
  listed on the creative design.

Earlier versions of these projects are renamed rather than duplicated:
migration 0012 created "Portfolio – Previous Design", and some databases
also have interim "Previous Design" / "Current Design" records.

Conservative like 0012: a title or description is only rewritten while it
still holds one of those known earlier texts (edits made in the admin are
kept), and projects are only created when missing. Reversing the migration
leaves the content as it is.
"""
import datetime

from django.db import migrations

CREATIVE = {
    'slug': 'creative-portfolio',
    'title': 'Creative Portfolio',
    'description': (
        'An interactive, animated edition of my portfolio website.\r\n'
        '• Runs on the same Django backend, MySQL database and admin panel as the rest of this site; '
        'only the front end is different.\r\n'
        '• Animated canvas background with floating particles that connect as they move.\r\n'
        '• Terminal-inspired sections, scroll animations and a dark mode toggle.\r\n'
        '• A parallax storytelling page and a small browser gaming zone (Snake, Breakout and tic-tac-toe).'
    ),
    'technologies_used': 'Django, Python, MySQL, Bootstrap 5, JavaScript, Canvas API, AOS',
}

PROFESSIONAL = {
    'slug': 'professional-portfolio',
    'title': 'Professional Portfolio',
    'description': (
        'A clean, client-focused edition of my portfolio website, built to be fast and easy to read.\r\n'
        '• Runs on the same Django backend, MySQL database and admin panel as the rest of this site; '
        'only the front end is different.\r\n'
        '• Clear sections for services, projects, experience, skills and contact.\r\n'
        "• Light and dark themes that follow the visitor's device settings.\r\n"
        '• Mobile-friendly, accessible pages with a simple contact form that emails new messages.'
    ),
    'technologies_used': 'Django, Python, MySQL, Bootstrap 5, JavaScript',
}

# Earlier versions of each project: slug, and the exact texts that may be
# replaced (anything else was edited by hand and is kept).
LEGACY = [
    (CREATIVE, {
        'slug': 'portfolio-previous-design',
        'titles': {'Portfolio – Previous Design', 'Previous Design'},
        'descriptions': {
            'The earlier design of this portfolio website, kept online so visitors can compare it with the current one.\r\n'
            '• Runs on the same Django backend, database and admin panel as this site; only the front end is different.\r\n'
            '• Animated canvas background with floating particles that connect as they move.\r\n'
            '• Terminal-inspired sections, scroll animations and a dark mode toggle.\r\n'
            '• A parallax storytelling page and a small browser gaming zone (Snake, Breakout and tic-tac-toe).',
        },
    }),
    (PROFESSIONAL, {
        'slug': 'portfolio-current-design',
        'titles': {'Portfolio – Current Design', 'Current Design'},
        'descriptions': {
            'The current design of this portfolio website: a clean, formal layout made to be easy for clients to read.\r\n'
            '• Runs on the same Django backend, database and admin panel as the previous design; only the front end is different.\r\n'
            '• Clear structure: introduction, services, selected work, experience, skills and contact.\r\n'
            "• Light and dark themes that follow the visitor's device, on a fully responsive layout.\r\n"
            '• Fast and calm: no loading screen or distracting animations, with accessible navigation and forms.',
        },
    }),
]

SHOWCASE_SLUGS = [new['slug'] for new, _ in LEGACY] + [old['slug'] for _, old in LEGACY]


def _place_after_real_work(Project, project):
    """Projects are listed newest first; date a showcase project just before
    the oldest real project so client work stays at the top."""
    oldest = Project.objects.exclude(slug__in=SHOWCASE_SLUGS).order_by('created_at').first()
    if oldest is not None:
        Project.objects.filter(pk=project.pk).update(
            created_at=oldest.created_at - datetime.timedelta(minutes=1))


def forwards(apps, schema_editor):
    Project = apps.get_model('main', 'Project')

    for new, old in LEGACY:
        if Project.objects.filter(slug=new['slug']).exists():
            continue
        project = Project.objects.filter(slug=old['slug']).first()
        if project is None:
            _place_after_real_work(Project, Project.objects.create(**new))
            continue
        project.slug = new['slug']
        if project.title in old['titles']:
            project.title = new['title']
        if project.description in old['descriptions']:
            project.description = new['description']
        project.save(update_fields=['slug', 'title', 'description'])


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_content_fixes_and_previous_design_project'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
