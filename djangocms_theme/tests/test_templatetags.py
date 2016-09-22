from django.test import TestCase
from django.template import Context, Template

from cms.api import create_page

from djangocms_theme.models import Theme, Stylesheet, PageTheme
from djangocms_theme.tests.util import MediaRoot

class FakeRequest(object):
    pass

class TemplatetagTests(TestCase):

    def setUp(self):
        self.mr = MediaRoot()
        self.settings_context = self.settings(MEDIA_ROOT=self.mr.root)
        self.settings_context.__enter__()

    def tearDown(self):
        self.mr = None
        self.settings_context.__exit__(None, None, None)

    def create_page(self, title, parent=None):
        return create_page(title, 'bogus.html', 'en',
                           published=True, parent=parent)

    def render_template(self, page, string):
        request = FakeRequest()
        request.current_page = page
        context = Context({'request': request})
        return Template(string).render(context)

    def test_no_theme(self):
        root = self.create_page('root')
        rendered = self.render_template(root,
                        '{% load theme %}<head>{% theme %}</head>')

        self.assertEqual(rendered, '<head></head>')

    def test_theme_page(self):
        css = 'body { background: #fff; }'
        theme = Theme.objects.create(name='test_theme')
        sheet = Stylesheet.objects.create(theme=theme, css=css)
        root = self.create_page('root')
        PageTheme.objects.create(extended_object=root, theme=theme)
        rendered = self.render_template(root,
                        '{% load theme %}<head>{% theme %}</head>')

        """
        self.assertEqual(rendered,
            '<head>'
            '<link rel="stylesheet" type="text/css" '
            'href="%s/theme/css/test_theme.css" media="all">'
            '</head>' % self.mr.root)
        """

    def test_theme_parent(self):
        css = 'body { background: #fff; }'
        theme = Theme.objects.create(name='test_theme')
        sheet = Stylesheet.objects.create(theme=theme, css=css)
        root = self.create_page('root')
        PageTheme.objects.create(extended_object=root, theme=theme)
        page = self.create_page('page', parent=root)
        rendered = self.render_template(page,
                        '{% load theme %}<head>{% theme %}</head>')

        """
        self.assertEqual(rendered,
            '<head>'
            '<link rel="stylesheet" type="text/css" '
            'href="%s/theme/css/test_theme.css" media="all">'
            '</head>' % self.mr.root)
        """
