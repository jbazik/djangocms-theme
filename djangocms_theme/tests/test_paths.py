from django.test import TestCase

from djangocms_theme.models import Theme, Image, Font, FontSrc, Stylesheet
from djangocms_theme.tests.util import MediaRoot

class PathTests(TestCase):

    def setUp(self):
        self.mr = MediaRoot()
        self.settings_context = self.settings(MEDIA_ROOT=self.mr.root)
        self.settings_context.__enter__()

    def tearDown(self):
        self.mr = None
        self.settings_context.__exit__(None, None, None)

    def test_image_path(self):
        self.mr.create_file('img', 'test.png')
        obj = Image.objects.create(name='foo',
                                   image=self.mr.rel('img', 'test.png'))
        obj.image_path('test.png')
        self.assertEqual(obj.path_from_name(), self.mr.rel('img', 'foo.png'))

    def test_fontsrc_path(self):
        self.mr.create_file('font', 'test.ttf')
        font = Font.objects.create(name='foo', family='FooFont')
        obj = FontSrc.objects.create(font=font, format='ttf',
                                     file=self.mr.rel('font', 'test.ttf'))
        obj.fontsrc_file_path('test.ttf')
        self.assertEqual(obj.path_from_name(), self.mr.rel('font', 'foo.ttf'))

    def test_stylesheet_path(self):
        theme = Theme.objects.create(name='test_theme')
        obj = Stylesheet.objects.create(theme=theme)
        self.assertEqual(obj.path_from_name(),
                         self.mr.rel('css', 'test_theme_all.css'))
