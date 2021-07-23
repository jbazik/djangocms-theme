import os
from io import BytesIO

from PIL import Image

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test import TestCase, RequestFactory

from django.contrib.auth.models import User
from django.contrib import admin

from djangocms_theme.models import Theme, SCREENSHOTS_PATH
from djangocms_theme.admin import ThemeAdmin
from djangocms_theme.tests.util import MediaRoot

class ScreenshotTests(TestCase):

    def setUp(self):
        self.rf = RequestFactory()
        self.mr = MediaRoot()
        self.settings_context = self.settings(MEDIA_ROOT=self.mr.root)
        self.settings_context.__enter__()
        self.root = User.objects.create_user(username='root', password='pw')
        self.root.is_staff = True
        self.root.is_superuser = True
        self.root.save()

    def tearDown(self):
        self.rf = None
        self.mr = None
        self.settings_context.__exit__(None, None, None)
        self.root.delete()
        del self.root

    def _redbox(self, dim, format):
        size = (dim, dim)
        img = Image.new('RGB', size, (255,0,0))
        jpg = BytesIO()
        jpg.name = 'red.jpg'
        img.save(jpg, format)
        jpg.seek(0)
        return jpg

    def test_upload_resize_reformat(self):
        req = self.rf.post(
              reverse('admin:djangocms_theme_theme_add'),
              {
                  'name': 'test_theme',
                  'origin': 'test',
                  'share': 'any',
                  'screenshot': self._redbox(200, 'JPEG'),
              })

        req.user = self.root
        ThemeForm = ThemeAdmin(Theme, admin.site).get_form(req, None)
        form = ThemeForm(req.POST, req.FILES)
        self.assertTrue(form.is_valid())
        form.save()
        theme = Theme.objects.get(name='test_theme')
        self.assertEqual(theme.screenshot.width, 160)
        self.assertEqual(theme.screenshot.height, 160)
        self.assertEqual(theme.screenshot.name,
                         os.path.join(SCREENSHOTS_PATH, theme.name + '.png'))

    def test_rename(self):
        theme = Theme.objects.create(name='test_theme', origin='test',
                                                        share='any')
        png = SimpleUploadedFile('redbox', self._redbox(160, 'PNG').read(),
                                           'image/png')
        theme.screenshot = png
        theme.save()
        dir = os.path.join(self.mr.root, SCREENSHOTS_PATH)
        self.assertTrue(os.path.exists(os.path.join(dir, 'test_theme.png')))
        theme = Theme.objects.get(name='test_theme')
        theme.name = 'new_name'
        theme.save()
        theme = Theme.objects.get(name='new_name')
        self.assertEqual(theme.screenshot.name,
                         os.path.join(SCREENSHOTS_PATH, 'new_name.png'))
        self.assertFalse(os.path.exists(os.path.join(dir, 'test_theme.png')))
        self.assertTrue(os.path.exists(os.path.join(dir, 'new_name.png')))
