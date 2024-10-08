# -*- coding: utf-8 -*-


from django.db import migrations, models
import djangocms_theme.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '__first__'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Font',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('weight', models.CharField(blank=True, max_length=10, verbose_name='weight', choices=[(None, 'None'), ('normal', 'Normal'), ('bold', 'Bold'), ('100', '100 Thin (Hairline)'), ('200', '200 Extra Light (Ultra Light)'), ('300', '300 Light'), ('400', '400 Normal'), ('500', '500 Medium'), ('600', '600 Semi Bold (Demi Bold)'), ('700', '700 Bold'), ('800', '800 Extra Bold (Ultra Bold)'), ('900', '900 Black (Heavy)')])),
                ('style', models.CharField(blank=True, max_length=10, verbose_name='style', choices=[(None, 'None'), ('normal', 'Normal'), ('italic', 'Italic'), ('oblique', 'Oblique')])),
                ('stretch', models.CharField(blank=True, max_length=20, verbose_name='stretch', choices=[(None, 'None'), ('normal', 'Normal'), ('condensed', 'Condensed'), ('ultra-condensed', 'Ultra-condensed'), ('extra-condensed', 'Extra-condensed'), ('semi-condensed', 'Semi-condensed'), ('expanded', 'Expanded'), ('semi-expanded', 'Semi-expanded'), ('extra-expanded', 'Extra-expanded'), ('ultra-expanded', 'Ultra-expanded')])),
                ('variant', models.CharField(help_text='Typical values: normal, small-caps', max_length=100, verbose_name='variant', blank=True)),
            ],
            options={
                'ordering': ['family', 'weight', 'style', 'stretch', 'variant'],
            },
        ),
        migrations.CreateModel(
            name='FontFamily',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('share', models.CharField(default='any', max_length=20, verbose_name='share', choices=[('owner', 'Owner'), ('group', 'Group'), ('any', 'Any')])),
                ('name', models.CharField(help_text='CSS Font family name for this font.', unique=True, max_length=100, verbose_name='name')),
                ('origin', models.CharField(help_text='Font foundry, designer or website.', max_length=120, verbose_name='origin', blank=True)),
                ('license', models.CharField(help_text='License terms.', max_length=10, verbose_name='license', choices=[('pd', 'Public Domain'), ('sil', 'SIL OFL'), ('oss', 'Other Open Source'), ('pu', 'Free for Personal Use'), ('com', 'Commercial'), ('unk', 'Unknown')])),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='auth.Group', null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': 'font families',
            },
        ),
        migrations.CreateModel(
            name='FontSrc',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('local', models.CharField(max_length=100, null=True, verbose_name='local', blank=True)),
                ('file', models.FileField(upload_to=djangocms_theme.models.fontsrc_file_path, null=True, verbose_name='file')),
                ('filext', models.CharField(max_length=10, editable=False, blank=True)),
                ('format', models.CharField(max_length=20, verbose_name='format', choices=[('eot', 'Embedded OpenType (eot)'), ('woff2', 'Web Open Font Format 2 (woff2)'), ('woff', 'Web Open Font Format (woff)'), ('ttf', 'TrueType (ttf)'), ('svg', 'Scalable Vector Graphics (svg)'), ('local', 'Local Browser Font')])),
                ('order', models.PositiveIntegerField(default=0, editable=False)),
                ('font', models.ForeignKey(related_name='srcs', to='djangocms_theme.Font', on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['order'],
                'verbose_name': 'font source',
            },
            bases=(models.Model, djangocms_theme.models.RenameBase),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('share', models.CharField(default='any', max_length=20, verbose_name='share', choices=[('owner', 'Owner'), ('group', 'Group'), ('any', 'Any')])),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='name')),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('image', models.ImageField(upload_to=djangocms_theme.models.image_path, verbose_name='image')),
                ('imext', models.CharField(max_length=10, editable=False, blank=True)),
                ('origin', models.CharField(help_text='Image source.', max_length=120, verbose_name='origin', blank=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='auth.Group', null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, djangocms_theme.models.RenameBase),
        ),
        migrations.CreateModel(
            name='PageTheme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('extended_object', models.OneToOneField(editable=False, to='cms.Page', on_delete=models.CASCADE)),
                ('public_extension', models.OneToOneField(related_name='draft_extension', null=True, editable=False, to='djangocms_theme.PageTheme', on_delete=models.CASCADE)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stylesheet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('css', models.TextField()),
                ('media', models.CharField(default='all', max_length=255, verbose_name='media')),
            ],
            options={
                'ordering': ['media'],
            },
        ),
        migrations.CreateModel(
            name='Theme',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('share', models.CharField(default='any', max_length=20, verbose_name='share', choices=[('owner', 'Owner'), ('group', 'Group'), ('any', 'Any')])),
                ('name', models.CharField(unique=True, max_length=120, verbose_name='name')),
                ('origin', models.CharField(help_text='Display name of theme provider.', max_length=120, verbose_name='origin', blank=True)),
                ('description', models.TextField(verbose_name='description', blank=True)),
                ('screenshot', models.ImageField(upload_to=djangocms_theme.models.screenshot_path, null=True, verbose_name='screen shot', blank=True)),
                ('reset', models.BooleanField(default=True, help_text='Include CSS Reset.', verbose_name='reset')),
                ('template_type', models.CharField(blank=True, help_text='CMS template type to which this theme can be applied.', max_length=100, verbose_name='template type', choices=[(b'default', b'Default')])),
                ('fontfams', models.ManyToManyField(related_name='themes', verbose_name='font families', to='djangocms_theme.FontFamily', blank=True)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='auth.Group', null=True)),
                ('images', models.ManyToManyField(related_name='themes', to='djangocms_theme.Image', blank=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('parent', models.ForeignKey(blank=True, to='djangocms_theme.Theme', null=True, on_delete=models.CASCADE)),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(models.Model, djangocms_theme.models.RenameBase),
        ),
        migrations.AddField(
            model_name='stylesheet',
            name='theme',
            field=models.ForeignKey(related_name='stylesheets', to='djangocms_theme.Theme', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='pagetheme',
            name='theme',
            field=models.ForeignKey(related_name='pages', blank=True, to='djangocms_theme.Theme', on_delete=models.CASCADE),
        ),
        migrations.AddField(
            model_name='font',
            name='family',
            field=models.ForeignKey(related_name='fonts', verbose_name='font family', to='djangocms_theme.FontFamily', null=True, on_delete=models.CASCADE),
        ),
        migrations.AlterUniqueTogether(
            name='stylesheet',
            unique_together=set([('theme', 'media')]),
        ),
        migrations.AlterUniqueTogether(
            name='fontsrc',
            unique_together=set([('local', 'file')]),
        ),
        migrations.AlterUniqueTogether(
            name='font',
            unique_together=set([('family', 'weight', 'style', 'stretch', 'variant')]),
        ),
    ]
