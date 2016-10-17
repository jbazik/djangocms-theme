# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('djangocms_theme', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FontFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('share', models.CharField(default='any', max_length=20, verbose_name='share', choices=[('owner', 'Owner'), ('group', 'Group'), ('any', 'Any')])),
                ('family', models.CharField(help_text='CSS Font family name for this font.', unique=True, max_length=100, verbose_name='family')),
                ('origin', models.CharField(help_text='Font foundry, designer or website.', max_length=120, verbose_name='origin', blank=True)),
                ('license', models.CharField(help_text='License terms.', max_length=10, verbose_name='license', choices=[('pd', 'Public Domain'), ('sil', 'SIL OFL'), ('oss', 'Other Open Source'), ('pu', 'Free for Personal Use'), ('com', 'Commercial'), ('unk', 'Unknown')])),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='auth.Group', null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='font',
            name='stretch',
            field=models.CharField(blank=True, max_length=20, verbose_name='stretch', choices=[(None, 'None'), ('normal', 'Normal'), ('condensed', 'Condensed'), ('ultra-condensed', 'Ultra-condensed'), ('extra-condensed', 'Extra-condensed'), ('semi-condensed', 'Semi-condensed'), ('expanded', 'Expanded'), ('semi-expanded', 'Semi-expanded'), ('extra-expanded', 'Extra-expanded'), ('ultra-expanded', 'Ultra-expanded')]),
        ),
        migrations.AlterField(
            model_name='font',
            name='style',
            field=models.CharField(blank=True, max_length=10, verbose_name='style', choices=[(None, 'None'), ('normal', 'Normal'), ('italic', 'Italic'), ('oblique', 'Oblique')]),
        ),
        migrations.AlterField(
            model_name='font',
            name='weight',
            field=models.CharField(blank=True, max_length=10, verbose_name='weight', choices=[(None, 'None'), ('normal', 'Normal'), ('bold', 'Bold'), ('100', '100 Thin (Hairline)'), ('200', '200 Extra Light (Ultra Light)'), ('300', '300 Light'), ('400', '400 Normal'), ('500', '500 Medium'), ('600', '600 Semi Bold (Demi Bold)'), ('700', '700 Bold'), ('800', '800 Extra Bold (Ultra Bold)'), ('900', '900 Black (Heavy)')]),
        ),
        migrations.AddField(
            model_name='font',
            name='famptr',
            field=models.ForeignKey(related_name='fonts', to='djangocms_theme.FontFamily', null=True),
        ),
        migrations.AddField(
            model_name='theme',
            name='fontfams',
            field=models.ManyToManyField(related_name='themes', to='djangocms_theme.FontFamily', blank=True),
        ),
    ]
