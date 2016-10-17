# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

from djangocms_theme.models import Font, FontFamily

def forward(apps, schema_editor):
    """
    Create FontFamily objects with data from Font, and link them in.
    """
    if not hasattr(Font, 'famptr'):
        return
    for font in Font.objects.all():
        fam, created = FontFamily.objects.get_or_create(family=font.family,
                           defaults={'origin': font.origin,
                                     'license': 'unk'})
        font.famptr = fam
        font.save()
        if created:
            fam.owner = font.owner
            fam.group = font.group
            fam.share = font.share
            fam.save()
            for theme in font.themes.all():
                theme.fontfams.add(fam)
                theme.save()


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_theme', '0002_font_refactor_1'),
    ]

    operations = [
        migrations.RunPython(forward),
    ]
