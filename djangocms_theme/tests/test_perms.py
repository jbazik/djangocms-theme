from django.urls import reverse
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from django.contrib import admin

from cms.models.pagemodel import Page
from cms.models.permissionmodels import ACCESS_PAGE
from cms.api import create_page, assign_user_to_page

from djangocms_theme.models import Theme, PageTheme
from djangocms_theme.admin import PageThemeAdmin

class PermTests(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.user1 = User.objects.create(username='nbarnes',
                                         email='nbarnes@hudsucker.com',
                                         password='password',
                                         is_staff=True)
        self.user2 = User.objects.create(username='aarcher',
                                         email='aarcher@hudsucker.com',
                                         password='password',
                                         is_staff=True)
        self.root = create_page('root', 'bogus.html', 'en', published=True)
        assign_user_to_page(self.root, self.user1, grant_on=ACCESS_PAGE)

        self.page = create_page('page', 'bogus.html', 'en', published=True,
                                 parent=self.root)
        assign_user_to_page(self.page, self.user2, grant_on=ACCESS_PAGE)

        self.theme = Theme.objects.create(name='test_theme',
                                          origin='test_origin', share='any')

    def tearDown(self):
        self.rf = None
        self.user1= None
        self.user2= None
        self.root = None
        self.page = None

    def test_add_theme(self):
        draft_page = Page.objects.get(pk=self.page.pk).get_draft_object()
        req = self.rf.get(reverse('admin:cms_page_edit_title_fields',
                          args=[draft_page.pk, 'en']))
        req.user = self.user2
        ma = PageThemeAdmin(PageTheme, admin.site)
        form = ma.get_form(req, draft_page)
        data = {
            'theme': self.theme.pk,
            #'site': admin.site,
        }
        inst = form(data, None, instance=self.page)
        self.assertTrue(inst.is_valid())
        self.theme.share = 'owner'
        self.theme.save()
        inst = form(data, None, instance=self.page)
        self.assertFalse(inst.is_valid())
