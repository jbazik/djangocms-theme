from __future__ import unicode_literals

import os, re
from io import StringIO

from PIL import Image as PImage

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.db import models
from django.db.models import Q, SET_NULL, CASCADE
from django.db.models.signals import m2m_changed
from django.utils.html import format_html
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from django.contrib.auth.models import Group

from cms.extensions import PageExtension
from cms.extensions.extension_pool import extension_pool
from cms.utils.conf import get_cms_setting

from djangocms_theme.settings import (THEME_PATH, CSS_PATH, IMAGE_PATH,
                                      FONT_PATH, SHARE_DEFAULT, THUMBSIZE,
                                      TEMPLATE_TYPES, CSS_RESET_URL)

SCREENSHOTS_PATH = THEME_PATH + '/screenshots'

SHARE_OWNER = 'owner'
SHARE_GROUP = 'group'
SHARE_ANY = 'any'
SHARE_DEFAULT = SHARE_DEFAULT or SHARE_ANY

def rename_fieldfile(field, newpath):
    """
    Change the storage path of a file.
    """
    oldpath = field.file.name
    if field.storage.exists(oldpath):
        field.storage.save(newpath, field)
        field.storage.delete(oldpath)
        field = newpath


class CanUseQuerySet(models.QuerySet):
    def can_use(self, user):
        if user.is_superuser:
            return self.all()
        if not user.is_staff:
            return self.none()
        return self.filter(Q(share=SHARE_ANY) |
                           Q(owner=user) |
                           Q(share=SHARE_GROUP) &
                               Q(group__in=user.groups.all()))
    def can_edit(self, user):
        if user.is_superuser:
            return self.all()
        if not user.is_staff:
            return self.none()
        return self.filter(Q(owner=user) |
                           Q(share=SHARE_GROUP) &
                               Q(group__in=user.groups.all()))

class RelatedManager(models.Manager):
    use_for_related_fields = True

CanUseManager = RelatedManager.from_queryset(CanUseQuerySet)

class PermissionBase(models.Model):
    PERMS = (
        (SHARE_OWNER, _('Owner')),
        (SHARE_GROUP, _('Group')),
        (SHARE_ANY, _('Any'))
    )

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=SET_NULL,
                              blank=True, null=True)
    group = models.ForeignKey(Group, on_delete=SET_NULL, blank=True, null=True)
    share = models.CharField(_('share'), max_length=20, choices=PERMS,
                                                        default=SHARE_DEFAULT)

    objects = CanUseManager()

    def can_use(self, user):
        """
        If SHARE_ANY, anyone may use the object.
        If SHARE_GROUP, only the owner or a member of the group may use it.
        If SHARE_OWNER, only the owner may use it.
        """
        if self.share == SHARE_ANY:
            return True
        if self.owner == user:
            return True
        if self.share == SHARE_GROUP:
            if self.group and self.group in user.groups:
                return True
        return False

    def can_edit(self, user):
        """
        Only superusers, owners or members of a group may edit the object.
        """
        if user.is_superuser:
            return True
        if self.owner and self.owner == user:
            return True
        if self.group and self.group in user.groups:
            return True
        return False

    def can_meta(self, user):
        """
        If an owner is set, only that person.
        If there is no owner, but a group is set, anyone in the group.
        If there is neither an owner or a group, then only a superuser.
        """
        if user.is_superuser:
            return True
        if self.owner:
            if self.owner == user:
                return True
        elif self.group and self.group in user.groups:
            return True
        return False

    class Meta:
        abstract = True

def screenshot_path(self, filename):
    """
    See ThemeForm.clean_screenshot() which resizes and converts
    screenshot uploads.
    """
    return '%s/%s.png' % (SCREENSHOTS_PATH, self.name)

@python_2_unicode_compatible
class Theme(PermissionBase):

    name = models.CharField(_('name'), max_length=120, unique=True)
    origin = models.CharField(_('origin'), max_length=120, blank=True,
                              help_text=_('Display name of theme provider.'))
    description = models.TextField(_('description'), blank=True)
    screenshot = models.ImageField(_('screenshot'), blank=True, null=True,
                                   upload_to=screenshot_path)
    reset = models.BooleanField(_('reset'), default=True,
                                help_text=_('Include CSS Reset.'))
    images = models.ManyToManyField('Image', related_name='themes', blank=True)
    fonts = models.ManyToManyField('Font', related_name='themes', blank=True)
    fontfams = models.ManyToManyField('FontFamily', related_name='themes',
                                                    blank=True)
    template_type = models.CharField(_('template type'), max_length=100,
             choices=TEMPLATE_TYPES, blank=True, help_text=_(
                 'CMS template type to which this theme can be applied.'))
    parent = models.ForeignKey('self', on_delete=CASCADE, blank=True, null=True)

    objects = CanUseManager()

    def __init__(self, *args, **kwargs):
        super(Theme, self).__init__(*args, **kwargs)
        self._name_orig = self.name

    def __str__(self):
        return self.name

    def path_from_name(self, name=None):
        return '%s/%s.png' % (SCREENSHOTS_PATH, name or self.name)

    def stylesheet_links(self, all=True):
        if all:
            if self.parent:
                links = self.parent.stylesheet_links(all)
            elif self.reset:
                links = [(CSS_RESET_URL, 'all')]
            else:
                links = []
        elif self.reset:
            links = [(CSS_RESET_URL, 'all')]
        links += [(s.url, s.media) for s in
                                   self.stylesheets.all().order_by('media')]
        return links

    def save(self, *args, **kwargs):
        oldname = self._name_orig if self._name_orig != self.name else None
        if self.screenshot and oldname:
            rename_fieldfile(self.screenshot, self.path_from_name())
        super(Theme, self).save(*args, **kwargs)
        self.update_css_files(oldname)
        self._name_orig = self.name

    def update_css_files(self, oldname=None):
        for stylesheet in self.stylesheets.all():
            stylesheet.save_css_file(oldname=oldname)

def image_path(self, filename):
    self.imext = os.path.splitext(filename)[1].lower()
    return '%s/%s%s' % (IMAGE_PATH, self.name, self.imext)

@python_2_unicode_compatible
class Image(PermissionBase):

    image_path = image_path

    name = models.CharField(_('name'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    image = models.ImageField(_('image'), upload_to=image_path)
    imext = models.CharField(max_length=10, blank=True, editable=False)
    origin = models.CharField(_('origin'), max_length=120, blank=True,
                              help_text=_('Image source.'))

    objects = CanUseManager()

    def __str__(self):
        return self.name

    def __init__(self, *args, **kwargs):
        super(Image, self).__init__(*args, **kwargs)
        self._name_orig = self.name

    @property
    def url(self):
        return '%s%s' % (settings.MEDIA_URL, self.path_from_name())

    @property
    def image_tag(self):
        return format_html(u'<img src="%s">' % self.url)

    def path_from_name(self, name=None):
        return '%s/%s%s' % (IMAGE_PATH, name or self.name, self.imext)

    def save(self, *args, **kwargs):
        if self._name_orig and self._name_orig != self.name:
            rename_fieldfile(self.image, self.path_from_name())
        super(Image, self).save(*args, **kwargs)
        self.update_themes()

    def update_themes(self):
        for theme in self.themes.all():
            theme.update_css_files()

@python_2_unicode_compatible
class FontFamily(PermissionBase):
    LICENSE_TERMS = (
        ('pd', _('Public Domain')),
        ('sil', _('SIL OFL')),
        ('oss', _('Other Open Source')),
        ('pu', _('Free for Personal Use')),
        ('com', _('Commercial')),
        ('unk', _('Unknown')),
    )
    family = models.CharField(_('family'), max_length=100, unique=True,
                    help_text=_('CSS Font family name for this font.'))
    origin = models.CharField(_('origin'), max_length=120, blank=True,
                    help_text=_('Font foundry, designer or website.'))
    license = models.CharField(_('license'), max_length=10,
                    choices=LICENSE_TERMS,
                    help_text=_('License terms.'))

    def __str__(self):
        return self.family;

@python_2_unicode_compatible
class Font(PermissionBase):
    STRETCH = [(None, _('None'))] + [(v,_(v.capitalize())) for v in (
        'normal',
        'condensed',
        'ultra-condensed',
        'extra-condensed',
        'semi-condensed',
        'expanded',
        'semi-expanded',
        'extra-expanded',
        'ultra-expanded',
    )]
    WEIGHT_CHOICES = (
        ( None,    _('None')),
        ('normal', _('Normal')),
        ('bold',   _('Bold')),
        ('100',    _('100 Thin (Hairline)')),
        ('200',    _('200 Extra Light (Ultra Light)')),
        ('300',    _('300 Light')),
        ('400',    _('400 Normal')),
        ('500',    _('500 Medium')),
        ('600',    _('600 Semi Bold (Demi Bold)')),
        ('700',    _('700 Bold')),
        ('800',    _('800 Extra Bold (Ultra Bold)')),
        ('900',    _('900 Black (Heavy)')),
    )
    STYLE = [(None, _('None'))] + [(v,_(v.capitalize())) for v in (
        'normal',
        'italic',
        'oblique',
    )]
    name = models.CharField(_('name'), max_length=100, unique=True,
                  help_text=_('Unique name for this font face definition.'))
    origin = models.CharField(_('origin'), max_length=120, blank=True,
                    help_text=_('Font foundry, designer or website.'))
    family = models.CharField(_('family'), max_length=100,
                    help_text=_('CSS Font family name for this font.'))
    famptr = models.ForeignKey(FontFamily, on_delete=CASCADE, null=True,
                                           related_name='fonts')
    weight = models.CharField(_('weight'), max_length=10, blank=True,
                                           choices=WEIGHT_CHOICES)
    style = models.CharField(_('style'), max_length=10, blank=True,
                                                        choices=STYLE)
    stretch = models.CharField(_('stretch'), max_length=20, blank=True,
                                             choices=STRETCH)
    variant = models.CharField(_('variant'), max_length=100, blank=True,
                     help_text=_('Typical values: normal, small-caps'))

    all_rules_path = THEME_PATH + '/fonts.css'
    all_rules_url = settings.MEDIA_URL + all_rules_path

    @classmethod
    def all_rules(cls):
        """
        Iterator returns font-face rules for all fonts.
        """
        for font in cls.objects.all():
            yield font.rule()

    @classmethod
    def update_all_rules_stylesheet(cls):
        if default_storage.exists(cls.all_rules_path):
            default_storage.delete(cls.all_rules_path)
        default_storage.save(cls.all_rules_path, ContentFile(
                             "\n".join(cls.all_rules())))

    def __str__(self):
        return self.name;

    def sample(self):
        return u'<span style="font-family:\'%s\'">ABCabc</span>' % self.family

    def __init__(self, *args, **kwargs):
        super(Font, self).__init__(*args, **kwargs)
        self._name_orig = self.name

    def save(self, *args, **kwargs):
        super(Font, self).save(*args, **kwargs)
        if self._name_orig and self._name_orig != self.name:
            for src in self.srcs:
                src.rename(self.name)
        self.update_themes()
        self.__class__.update_all_rules_stylesheet()

    def delete(self, *args, **kwargs):
        super(Font, self).delete(*args, **kwargs)
        self.__class__.update_all_rules_stylesheet()

    def rule(self):
        """
        Returns the font-face "at" rule to include in a css file.

        Although FontSrc has an "order" field, it is honored here only
        for multiple "local" sources.  The proper way to do this is to
        make the srcs list sortable in the admin.  The problem is that
        there is a well-known best practice ordering that most users
        will want, and they can't be expected to reproduce that order.
        But some experts may want a different order.  I'm going to make
        the order field hidden for now and leave this for another day.
        """
        rule = [
            "@font-face {",
            "    font-family: '%s';" % self.family,
        ]
        for attr in ('weight', 'style', 'stretch', 'variant'):
            if getattr(self, attr):
                rule.append("    font-%s: %s;" % (attr, getattr(self, attr)))
        locals = []
        files = {}
        eot = None
        for src in self.srcs.order_by('order'):
            if src.format == 'eot':
                eot = src
            if src.file:
                files[src.format] = src
            elif src.local:
                locals.append(src)
        if eot:
            # IE hack
            rule.append("    src: url('%s');" % eot.file)
        srcs = []
        for src in locals:
            srcs.append(src.value)
        for format in ('eot', 'woff2', 'woff', 'ttf', 'svg'):
            if format in files:
                srcs.append(files[format].value)
        rule.append("    src: %s;\n}" % ",\n         ".join(srcs))
        return "\n".join(rule)

    def update_themes(self):
        for theme in self.themes.all():
            theme.update_css_files()

def fontsrc_file_path(self, filename):
    self.filext = os.path.splitext(filename)[1].lower()
    return '%s/%s%s' % (FONT_PATH, self.font.name, self.filext)

@python_2_unicode_compatible
class FontSrc(models.Model):
    FORMATS = (
        ('eot', _('Embedded OpenType (eot)')),
        ('woff2', _('Web Open Font Format 2 (woff2)')),
        ('woff', _('Web Open Font Format (woff)')),
        ('ttf', _('TrueType (ttf)')),
        ('svg', _('Scalable Vector Graphics (svg)')),
        ('local', _('Local Browser Font')),
    )
    fontsrc_file_path = fontsrc_file_path

    font = models.ForeignKey(Font, on_delete=CASCADE, related_name='srcs')
    local = models.CharField(_('local'), max_length=100, blank=True, null=True)
    file = models.FileField(_('file'), null=True, upload_to=fontsrc_file_path)
    filext = models.CharField(max_length=10, blank=True, editable=False)
    format = models.CharField(_('format'), max_length=20, choices=FORMATS)
    order = models.PositiveIntegerField(default=0, blank=False, null=False,
                                        editable=False)

    def __str__(self):
        return self.name

    @property
    def name(self):
        if self.format == 'local':
            return self.local
        else:
            return '%s%s' % (self.font.name, self.filext)

    @property
    def url(self):
        return '%s%s' % (settings.MEDIA_URL, self.path_from_name())

    def path_from_name(self, name=None):
        return '%s/%s' % (FONT_PATH, name or self.name)

    @property
    def value(self):
        # handle font-face idiosyncrasies here
        if self.format == 'eot':
            return "url('%s?#iefix') format('embedded-opentype')" % self.url
        elif self.format == 'woff2':
            return "url('%s') format('woff2')" % self.url
        elif self.format == 'woff':
            return "url('%s') format('woff')" % self.url
        elif self.format == 'ttf':
            return "url('%s') format('truetype')" % self.url
        elif self.format == 'svg':
            return "url('%s#webfont') format('svg')" % self.url
        elif self.format == 'local':
            return "local('%s')" % self.local

    def rename(self, newname):
        rename_fieldfile(self.file, self.path_from_name(newname))

    def save(self, *args, **kwargs):
        super(FontSrc, self).save(*args, **kwargs)
        self.font.update_themes()
        Font.update_all_rules_stylesheet()

    def delete(self, *args, **kwargs):
        font = self.font
        super(FontSrc, self).delete(*args, **kwargs)
        font.update_themes()
        Font.update_all_rules_stylesheet()

@python_2_unicode_compatible
class Stylesheet(models.Model):
    css = models.TextField()
    media = models.CharField(_('media'), max_length=255, default='all')
    theme = models.ForeignKey(Theme, on_delete=CASCADE,
                              related_name='stylesheets')

    def __str__(self):
        return self.name

    @property
    def name(self):
        return '%s_%s.css' % (self.theme.name, self.media)

    @property
    def stylesheet(self):
        """
        This is the full css content of the stylesheet.
        """
        return "\n".join([self.font_rules(), self.css_rules()])

    @property
    def url(self):
        return '%s%s' % (settings.MEDIA_URL, self.path_from_name())

    def path_from_name(self, name=None):
        return '%s/%s_%s.css' % (CSS_PATH, name or self.theme.name, self.media)

    def font_rules(self):
        return "\n".join([f.rule() for f in self.theme.fonts.order_by('name')])

    def css_rules(self):
        images = dict((img.name, img) for img in self.theme.images.all())
        return re.sub(
            r'(url\([\'"])([^\'"]+)([\'"]\))', lambda m,i=images: ''.join([
                m.group(1),
                images[m.group(2)].url if m.group(2) in i else m.group(2),
                m.group(3),
            ]), self.css)

    def save(self, *args, **kwargs):
        super(Stylesheet, self).save(*args, **kwargs)
        self.save_css_file()

    def delete(self, *args, **kwargs):
        super(Stylesheet, self).delete(*args, **kwargs)
        default_storage.delete(self.path_from_name())

    def save_css_file(self, oldname=None):
        path = self.path_from_name()
        if default_storage.exists(path):
            default_storage.delete(path)
        default_storage.save(path, ContentFile(self.stylesheet))
        if oldname:
            default_storage.delete(self.path_from_name(oldname))

    class Meta:
        unique_together = ('theme', 'media')

class PageTheme(PageExtension):
    theme = models.ForeignKey(Theme, on_delete=CASCADE, blank=True,
                              related_name='pages')

def m2m_cascade(sender, instance, action, reverse, **kwargs):
    """
    Signal handler, deletes objects that are no longer referenced by a theme.
    """
    if reverse and action == 'post_remove':
        if instance.themes.count() == 0:
            instance.delete()

m2m_changed.connect(m2m_cascade, sender=Theme.images.through, dispatch_uid='')
m2m_changed.connect(m2m_cascade, sender=Theme.fonts.through, dispatch_uid='')

extension_pool.register(PageTheme)
