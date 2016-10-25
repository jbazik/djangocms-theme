# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_theme', '0005_font_file_rename'),
    ]

    operations = [
        migrations.RenameField('FontFamily', 'family', 'name'),
        migrations.RenameField('Font', 'famptr', 'family'),
        migrations.AlterModelOptions(
            name='font',
            options={'ordering': ['family', 'weight', 'style', 'stretch', 'variant']},
        ),
        migrations.AlterModelOptions(
            name='fontfamily',
            options={'ordering': ['name'], 'verbose_name_plural': 'font families'},
        ),
        migrations.AlterField(
            model_name='fontfamily',
            name='name',
            field=models.CharField(help_text='CSS Font family name for this font.', unique=True, max_length=100, verbose_name='name'),
        ),
    ]
