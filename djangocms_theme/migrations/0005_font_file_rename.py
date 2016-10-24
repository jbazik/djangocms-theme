# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from djangocms_theme.models import Theme, Font

def forward(apps, schema_editor):
    """
    The font refactor renamed all font files, so actually rename them
    and update all stylesheets that may reference them.
    """
    if not hasattr(Font, 'famptr'):
        return
    for font in Font.objects.all():
        font.rename()
    for theme in Theme.objects.all():
        theme.update_css_files()
    Font.update_all_rules_stylesheet()

class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_theme', '0004_font_refactor_2'),
    ]

    operations = [
        migrations.RunPython(forward)
    ]
