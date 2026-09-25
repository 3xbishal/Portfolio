"""
Tests for the custom admin panel: every page renders for the site owner with
the admin's own assets, "Delete all messages" needs a POST confirmation and
the owner's login, opening a message marks it read, delete confirmations
show their notice, search works on every list, and a project saved without a
slug still gets a working page address.
"""
import datetime

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from main.models import (
    ContactMessage, Education, Experience, Profile, Project, Service, Skill, Testimonial,
)


class AdminPanelTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.owner = get_user_model().objects.create_superuser('owner', 'owner@example.com', 'pw-123456')
        Profile.objects.create(name='Jane Developer', title='Web Developer',
                               email='jane@example.com', bio='Backend developer.')
        cls.project = Project.objects.create(title='Shop', slug='shop', description='Checkout',
                                             technologies_used='Django, React')
        cls.skill = Skill.objects.create(name='Python', icon_class='fab fa-python')
        cls.experience = Experience.objects.create(
            company='Acme', position='Developer', description='Features',
            start_date=datetime.date(2024, 1, 1), is_current=True)
        cls.education = Education.objects.create(
            institution='Uni', degree='BSc', field_of_study='CSE', start_date=datetime.date(2020, 1, 1))
        cls.testimonial = Testimonial.objects.create(name='Client', position='Founder', content='Great work.')
        cls.service = Service.objects.create(title='API development', description='REST APIs')
        cls.unread = ContactMessage.objects.create(
            name='Client', email='client@example.com', subject='Quote please', message='Hello')
        cls.read = ContactMessage.objects.create(
            name='Recruiter', email='hr@example.com', subject='Job offer', message='Hi', is_read=True)

    def setUp(self):
        self.client.force_login(self.owner)

    def test_every_admin_page_renders_with_admin_assets(self):
        urls = [
            reverse('admin_panel:dashboard'),
            reverse('admin_panel:profile_edit'),
            reverse('admin_panel:contactmessage_list'),
            reverse('admin_panel:contactmessage_detail', args=[self.read.pk]),
            reverse('admin_panel:contactmessage_delete', args=[self.read.pk]),
            reverse('admin_panel:contactmessage_delete_all'),
            reverse('admin_panel:project_media', args=[self.project.pk]),
        ]
        for name, obj in [('project', self.project), ('skill', self.skill),
                          ('experience', self.experience), ('education', self.education),
                          ('testimonial', self.testimonial), ('service', self.service)]:
            urls += [
                reverse(f'admin_panel:{name}_list'),
                reverse(f'admin_panel:{name}_add'),
                reverse(f'admin_panel:{name}_edit', args=[obj.pk]),
                reverse(f'admin_panel:{name}_delete', args=[obj.pk]),
            ]
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, 'css/admin.')
                self.assertContains(response, 'js/admin.')
                # The public site's animated stylesheet and click-sound script are gone.
                self.assertNotContains(response, 'css/style.')
                self.assertNotContains(response, 'js/main.')

    def test_login_page_is_plain_sign_in_without_sidebar(self):
        self.client.logout()
        response = self.client.get(reverse('admin_panel:login'))
        self.assertContains(response, 'Sign in')
        self.assertNotContains(response, 'adminSidebar')

    def test_search_works_on_every_list(self):
        cases = [
            ('project', 'Shop', 'project_edit', self.project),
            ('skill', 'Python', 'skill_edit', self.skill),
            ('experience', 'Acme', 'experience_edit', self.experience),
            ('education', 'Uni', 'education_edit', self.education),
            ('testimonial', 'Great', 'testimonial_edit', self.testimonial),
            ('service', 'API', 'service_edit', self.service),
            ('contactmessage', 'Quote', 'contactmessage_detail', self.unread),
        ]
        for name, query, link_name, obj in cases:
            link = reverse(f'admin_panel:{link_name}', args=[obj.pk])
            with self.subTest(list=name):
                url = reverse(f'admin_panel:{name}_list')
                self.assertContains(self.client.get(url, {'q': query}), link)
                self.assertNotContains(self.client.get(url, {'q': 'no-such-thing'}), link)

    # --- Messages -----------------------------------------------------------

    def test_messages_page_offers_delete_all(self):
        response = self.client.get(reverse('admin_panel:contactmessage_list'))
        self.assertContains(response, reverse('admin_panel:contactmessage_delete_all'))
        self.assertContains(response, 'Delete all messages')

    def test_delete_all_asks_for_confirmation_first(self):
        response = self.client.get(reverse('admin_panel:contactmessage_delete_all'))
        self.assertContains(response, 'All 2 messages will be permanently deleted')
        self.assertContains(response, 'including 1 you have not read yet')
        self.assertEqual(ContactMessage.objects.count(), 2)

    def test_delete_all_removes_every_message(self):
        response = self.client.post(reverse('admin_panel:contactmessage_delete_all'), follow=True)
        self.assertRedirects(response, reverse('admin_panel:contactmessage_list'))
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertContains(response, 'Deleted all messages (2).')
        # With the inbox empty, the button is no longer offered.
        self.assertNotContains(response, reverse('admin_panel:contactmessage_delete_all'))

    def test_delete_all_requires_the_site_owner(self):
        self.client.logout()
        response = self.client.post(reverse('admin_panel:contactmessage_delete_all'))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse('admin_panel:login'), response['Location'])
        visitor = get_user_model().objects.create_user('visitor', password='pw-123456')
        self.client.force_login(visitor)
        self.client.post(reverse('admin_panel:contactmessage_delete_all'))
        self.assertEqual(ContactMessage.objects.count(), 2)

    def test_opening_a_message_marks_it_read(self):
        response = self.client.get(reverse('admin_panel:contactmessage_detail', args=[self.unread.pk]))
        self.assertContains(response, 'Reply by email')
        self.unread.refresh_from_db()
        self.assertTrue(self.unread.is_read)

    # --- Deleting and saving records ----------------------------------------

    def test_delete_shows_confirmation_notice(self):
        response = self.client.post(reverse('admin_panel:skill_delete', args=[self.skill.pk]))
        self.assertFalse(Skill.objects.filter(pk=self.skill.pk).exists())
        notices = [str(m) for m in get_messages(response.wsgi_request)]
        self.assertIn('Skill deleted successfully.', notices)

    def test_project_saved_without_slug_gets_a_working_address(self):
        response = self.client.post(reverse('admin_panel:project_add'), {
            'title': 'New Client Site', 'slug': '', 'description': 'A website.',
            'project_url': '', 'github_url': '', 'technologies_used': 'Django',
        })
        self.assertRedirects(response, reverse('admin_panel:project_list'))
        project = Project.objects.get(title='New Client Site')
        self.assertEqual(project.slug, 'new-client-site')
        self.assertEqual(self.client.get(project.get_absolute_url()).status_code, 200)

        duplicate = Project.objects.create(title='New Client Site', description='Again')
        self.assertEqual(duplicate.slug, 'new-client-site-1')

    def test_forms_use_plain_labels(self):
        response = self.client.get(reverse('admin_panel:project_edit', args=[self.project.pk]))
        for label in ('Project name', 'Live site URL', 'Source code URL', 'Technologies'):
            self.assertContains(response, label)
        response = self.client.get(reverse('admin_panel:profile_edit'))
        self.assertContains(response, 'Notification email')
        self.assertContains(response, 'New messages from the contact form are emailed to this address.')
