# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import djangocms_theme.models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_theme', '0003_font_refactor_data'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='font',
            options={'ordering': ['famptr', 'weight', 'style', 'stretch', 'variant']},
        ),
        migrations.AlterModelOptions(
            name='fontfamily',
            options={'ordering': ['family'], 'verbose_name_plural': 'font families'},
        ),
        migrations.AlterModelOptions(
            name='fontsrc',
            options={'ordering': ['order'], 'verbose_name': 'font source'},
        ),
        migrations.AlterModelOptions(
            name='image',
            options={'ordering': ['name']},
        ),
        migrations.AlterModelOptions(
            name='stylesheet',
            options={'ordering': ['media']},
        ),
        migrations.AlterModelOptions(
            name='theme',
            options={'ordering': ['name']},
        ),
        migrations.RemoveField(
            model_name='theme',
            name='fonts',
        ),
        migrations.AlterField(
            model_name='font',
            name='famptr',
            field=models.ForeignKey(related_name='fonts', verbose_name='font family', to='djangocms_theme.FontFamily', null=True),
        ),
        migrations.AlterField(
            model_name='theme',
            name='fontfams',
            field=models.ManyToManyField(related_name='themes', verbose_name='font families', to='djangocms_theme.FontFamily', blank=True),
        ),
        migrations.AlterField(
            model_name='theme',
            name='screenshot',
            field=models.ImageField(upload_to=djangocms_theme.models.screenshot_path, null=True, verbose_name='screen shot', blank=True),
        ),
        migrations.AlterUniqueTogether(
            name='font',
            unique_together=set([('famptr', 'weight', 'style', 'stretch', 'variant')]),
        ),
        migrations.AlterUniqueTogether(
            name='fontsrc',
            unique_together=set([('local', 'file')]),
        ),
        migrations.RemoveField(
            model_name='font',
            name='family',
        ),
        migrations.RemoveField(
            model_name='font',
            name='group',
        ),
        migrations.RemoveField(
            model_name='font',
            name='name',
        ),
        migrations.RemoveField(
            model_name='font',
            name='origin',
        ),
        migrations.RemoveField(
            model_name='font',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='font',
            name='share',
        ),
    ]
