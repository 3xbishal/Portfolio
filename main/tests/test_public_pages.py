"""
Tests for the client-facing pages: the `summary` card-teaser filter, a
smoke test that every page of the default (professional) design renders
cleanly, and the creative design under /creative/ (same views and data,
its own templates) together with the showcase projects that let visitors
move between the two designs.
"""
import datetime

from django.test import SimpleTestCase, TestCase
from django.urls import reverse

from main.models import (
    ContactMessage, Education, Experience, Profile, Project, Service, Skill, Testimonial,
)
from main.templatetags.main_tags import summary


class SummaryFilterTests(SimpleTestCase):

    def test_bullets_become_sentences(self):
        text = '• Built the API\n• Added auth\n- Wrote tests'
        self.assertEqual(summary(text, 50), 'Built the API. Added auth. Wrote tests')

    def test_wrapped_lines_are_joined_with_spaces(self):
        text = 'Skilled in building template-based\nweb applications.'
        self.assertEqual(summary(text, 50), 'Skilled in building template-based web applications.')

    def test_existing_punctuation_is_kept(self):
        self.assertEqual(summary('• One.\n• Two!', 50), 'One. Two!')

    def test_truncates_and_strips_html(self):
        self.assertEqual(summary('<p>one two three four</p>', 2), 'one two…')

    def test_no_punctuation_before_ellipsis(self):
        self.assertEqual(summary('• Built the API.\n• Added auth.', 3), 'Built the API…')

    def test_empty_and_bad_word_count(self):
        self.assertEqual(summary(None), '')
        self.assertEqual(summary('a b c', 'x'), 'a b c')


class PublicPagesTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        Profile.objects.create(
            name='Jane Developer', title='Web Developer', email='jane@example.com',
            bio='Backend developer.\nBuilds APIs.', location='Dhaka',
            linkedin_url='https://www.linkedin.com/in/example/',
        )
        cls.project = Project.objects.create(
            title='Shop', slug='shop', description='• Checkout\n• Payments',
            technologies_used='Django, DRF, PostgreSQL',
        )
        cls.experience = Experience.objects.create(
            company='Acme', position='Developer', description='• Shipped features',
            start_date=datetime.date(2024, 1, 1), is_current=True,
        )
        Education.objects.create(
            institution='Uni', degree='BSc', field_of_study='CSE',
            start_date=datetime.date(2020, 1, 1),
        )
        Skill.objects.create(name='Python', icon_class='fab fa-python')
        Service.objects.create(title='APIs', description='REST APIs')
        Testimonial.objects.create(name='Client', position='Founder', content='Great work.')

    def test_public_pages_render(self):
        urls = [
            reverse('home'),
            reverse('about'),
            reverse('projects'),
            reverse('project_detail', kwargs={'slug': 'shop'}),
            reverse('experience_detail', kwargs={'slug': self.experience.slug}),
            reverse('contact'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, reverse('contact'))
                self.assertContains(response, 'css/site.')  # hashed name when DEBUG=False
                self.assertNotContains(response, 'pageLoader')
                self.assertNotContains(response, 'js/main.')

    def test_home_shows_every_section_and_readable_summary(self):
        response = self.client.get(reverse('home'))
        for text in ('Jane Developer', 'How I can help', 'Selected work',
                     "Where I've worked", 'Technologies I use', 'Great work.'):
            with self.subTest(text=text):
                self.assertContains(response, text)
        self.assertContains(response, 'Checkout. Payments')

    def test_main_nav_hides_playground_pages(self):
        header = self.client.get(reverse('home')).content.decode()
        header = header[header.index('<header'):header.index('</header>')]
        self.assertNotIn(reverse('parallax'), header)
        self.assertNotIn(reverse('gaming_zone'), header)

    def test_playground_urls_redirect_to_creative_design(self):
        self.assertRedirects(self.client.get(reverse('parallax')), reverse('creative:parallax'))
        self.assertRedirects(self.client.get(reverse('gaming_zone')), reverse('creative:gaming_zone'))

    def test_project_detail_lists_technologies(self):
        response = self.client.get(self.project.get_absolute_url())
        for tech in ('Django', 'DRF', 'PostgreSQL'):
            self.assertContains(response, f'<li class="tag">{tech}</li>', html=True)


class DesignShowcaseTests(TestCase):
    """The creative design at /creative/ and the two showcase projects that
    link the designs to each other. The showcase projects are created by
    migrations 0012/0013, which also run for the test database."""

    @classmethod
    def setUpTestData(cls):
        Profile.objects.create(name='Jane Developer', title='Web Developer',
                               email='jane@example.com', bio='Backend developer.')
        cls.project = Project.objects.create(title='Shop', slug='shop', description='Checkout')
        cls.experience = Experience.objects.create(
            company='Acme', position='Developer', description='Features',
            start_date=datetime.date(2024, 1, 1))
        cls.creative = Project.objects.get(slug='creative-portfolio')
        cls.professional = Project.objects.get(slug='professional-portfolio')

    def test_creative_pages_render_with_own_assets_and_stay_in_creative(self):
        urls = [
            reverse('creative:home'),
            reverse('creative:about'),
            reverse('creative:projects'),
            reverse('creative:project_detail', kwargs={'slug': 'shop'}),
            reverse('creative:experience_detail', kwargs={'slug': self.experience.slug}),
            reverse('creative:contact'),
            reverse('creative:parallax'),
            reverse('creative:gaming_zone'),
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'css/style.')
                self.assertContains(response, 'js/main.')
                self.assertNotContains(response, 'css/site.')
                self.assertContains(response, 'name="robots" content="noindex')
                # Navigation keeps visitors inside the creative design.
                self.assertContains(response, f'href="{reverse("creative:contact")}"')

    def test_no_page_calls_a_design_old_or_new(self):
        urls = [
            reverse('home'),
            reverse('projects'),
            self.creative.get_absolute_url(),
            reverse('creative:home'),
            reverse('creative:projects'),
            reverse('creative:project_detail', kwargs={'slug': self.professional.slug}),
        ]
        for url in urls:
            with self.subTest(url=url):
                text = self.client.get(url).content.decode().lower()
                for phrase in ('previous design', 'current design', 'current site'):
                    self.assertNotIn(phrase, text)

    def test_creative_project_links_stay_in_creative(self):
        response = self.client.get(reverse('creative:projects'))
        self.assertContains(response, reverse('creative:project_detail', kwargs={'slug': 'shop'}))
        self.assertNotContains(response, 'href="/projects/shop/"')

    def test_creative_contact_saves_message_and_returns_to_creative(self):
        response = self.client.post(reverse('creative:contact'), {
            'name': 'Client', 'email': 'client@example.com',
            'subject': 'Quote', 'message': 'Hello',
        })
        self.assertRedirects(response, reverse('creative:contact'))
        self.assertTrue(ContactMessage.objects.filter(subject='Quote').exists())

    def test_showcase_projects_link_to_their_design(self):
        self.assertEqual(self.creative.title, 'Creative Portfolio')
        self.assertEqual(self.creative.showcased_design, 'creative')
        self.assertEqual(self.creative.live_url, reverse('creative:home'))
        self.assertIn('images/creative-portfolio', self.creative.media_gallery[0]['url'])

        self.assertEqual(self.professional.title, 'Professional Portfolio')
        self.assertEqual(self.professional.showcased_design, 'professional')
        self.assertEqual(self.professional.live_url, reverse('home'))
        self.assertIn('images/professional-portfolio', self.professional.media_gallery[0]['url'])

    def test_each_design_lists_only_the_other_design(self):
        for url in (reverse('home'), reverse('projects')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'Creative Portfolio')
                self.assertContains(response, f'href="{reverse("creative:home")}"')
                self.assertNotContains(response, 'Professional Portfolio')
        for url in (reverse('creative:home'), reverse('creative:projects'), reverse('creative:parallax')):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertContains(response, 'Professional Portfolio')
                self.assertNotContains(response, 'Creative Portfolio')
        detail = self.client.get(
            reverse('creative:project_detail', kwargs={'slug': self.professional.slug}))
        self.assertContains(detail, f'href="{reverse("home")}"')

    def test_client_work_is_listed_before_showcase_projects(self):
        listed = list(Project.objects.for_design('professional').values_list('slug', flat=True))
        self.assertEqual(listed, ['shop', 'creative-portfolio'])

    def test_regular_projects_keep_their_own_live_url(self):
        self.project.project_url = 'https://shop.example.com/'
        self.assertIsNone(self.project.showcased_design)
        self.assertEqual(self.project.live_url, 'https://shop.example.com/')
