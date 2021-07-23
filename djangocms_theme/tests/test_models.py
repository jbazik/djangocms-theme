from django.conf import settings
from django.test import TestCase

from cms.api import create_page

from djangocms_theme.models import (Theme, Image, Font, FontSrc,
                                    Stylesheet, PageTheme)


class ModelTests(TestCase):

    def test_theme(self):
        obj = Theme()
        self.assertIsInstance(obj, Theme)

    def test_image(self):
        obj = Image()
        self.assertIsInstance(obj, Image)

    def test_font(self):
        obj = Font()
        self.assertIsInstance(obj, Font)

    def test_fontsrc(self):
        obj = FontSrc()
        self.assertIsInstance(obj, FontSrc)

    def test_stylesheet(self):
        obj = Stylesheet()
        self.assertIsInstance(obj, Stylesheet)

    def test_pagetheme(self):
        obj = PageTheme()
        self.assertIsInstance(obj, PageTheme)

    def test_page(self):
        theme = Theme.objects.create(name='foo')
        page = create_page('root', 'bogus.html', 'en', published=True)
        pagetheme = PageTheme.objects.create(extended_object=page, theme=theme)
        self.assertEqual(page.pagetheme, pagetheme)
