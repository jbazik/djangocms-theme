import re

from django.test import TestCase

from djangocms_theme.models import Theme, Image, Font, FontSrc, Stylesheet
from djangocms_theme.tests.util import MediaRoot


class RuleTests(TestCase):

    def setUp(self):
        self.mr = MediaRoot()
        self.settings_context = self.settings(MEDIA_ROOT=self.mr.root)
        self.settings_context.__enter__()

    def tearDown(self):
        self.mr = None
        self.settings_context.__exit__(None, None, None)

    def addimage(self, theme, name, filename):
        self.mr.create_file('img', filename)
        path = self.mr.rel('img', filename)
        image = Image.objects.create(name=name, image=path)
        image.image_path(filename)
        image.save()
        theme.images.add(image)
        return image

    def addfontsrc(self, font, name, format):
        if format == 'local':
            src = FontSrc.objects.create(font=font, local=name, format='local')
        else:
            self.mr.create_file('font', name)
            path = self.mr.rel('font', name)
            src = FontSrc.objects.create(font=font, format=format, file=path)
            src.fontsrc_file_path(path)
            src.save()
        font.srcs.add(src)
        return src

    def test_fontsrc_file(self):
        font = Font.objects.create(name='foo', family='FooFont')
        src = self.addfontsrc(font, 'test.ttf', 'ttf')
        self.assertEqual(src.value, u"url('%s') format('truetype')" %
                                                self.mr.url('font', 'foo.ttf'))

    def test_fontsrc_local(self):
        font = Font.objects.create(name='foo', family='FooFont')
        src = self.addfontsrc(font, 'Ariel', 'local')
        self.assertEqual(src.value, u"local('Ariel')")

    def test_font_rules(self):
        font = Font.objects.create(name='foo', family='FooFont',
                                          weight='bold', style='italic')
        self.addfontsrc(font, 'test.ttf', 'ttf')
        self.addfontsrc(font, 'test.woff', 'woff')
        self.addfontsrc(font, 'Ariel', 'local')

        #print "\n%s\n" % font.rule()
        self.assertEqual(font.rule(), "\n".join([
            "@font-face {",
            "    font-family: 'FooFont';",
            "    font-weight: bold;",
            "    font-style: italic;",
            "    src: local('Ariel'),",
            "         url('%s') format('woff'),",
            "         url('%s') format('truetype');",
            "}",
        ]) % (self.mr.url('font', 'foo.woff'),
              self.mr.url('font', 'foo.ttf')))

    def test_stylesheet_rules(self):
        css = 'body { background: #fff; }'
        theme = Theme.objects.create(name='test_theme')
        obj = Stylesheet.objects.create(theme=theme, css=css)
        self.assertEqual(obj.url, self.mr.url('css', 'test_theme_all.css'))
        self.assertEqual(obj.css_rules(), css)

    def test_stylesheet_rules_images(self):
        css = 'body { background: url("foo"); } p { background: url(\'bar\'); }'
        theme = Theme.objects.create(name='test_theme')
        obj = Stylesheet.objects.create(theme=theme, css=css)

        foo = self.addimage(theme, 'foo', 'foo.png')
        bar = self.addimage(theme, 'bar', 'bar.png')

        rules = re.sub('foo', foo.url, css)
        rules = re.sub('bar', bar.url, rules)
        self.assertEqual(obj.css_rules(), rules)

    def test_stylesheet_rules_fonts(self):
        theme = Theme.objects.create(name='test_theme')
        obj = Stylesheet.objects.create(theme=theme)

        foo = Font.objects.create(name='foo', family='FooFont',
                                  weight='bold', style='italic')
        theme.fonts.add(foo)

        self.addfontsrc(foo, 'foo.ttf', 'ttf')
        self.addfontsrc(foo, 'foo.woff', 'woff')

        bar = Font.objects.create(name='bar', family='BarFont',
                                  weight='normal', style='oblique')
        theme.fonts.add(bar)

        self.addfontsrc(bar, 'bar.ttf', 'ttf')
        self.addfontsrc(bar, 'bar.woff', 'woff')

        self.maxDiff = None
        self.assertEqual(obj.font_rules(), "\n".join([bar.rule(), foo.rule()]))
