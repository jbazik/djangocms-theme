try:
    from urllib.parse import urljoin
except ImportError:
    from urllib.parse import urljoin

from django.conf import settings


THEME_PATH = getattr(settings, 'THEME_PATH', 'theme')
CSS_PATH = getattr(settings, 'THEME_CSS_PATH', THEME_PATH + '/css')
IMAGE_PATH = getattr(settings, 'THEME_IMAGE_PATH', THEME_PATH + '/img')
FONT_PATH = getattr(settings, 'THEME_FONT_PATH', THEME_PATH + '/font')

THUMBSIZE = getattr(settings, 'THEME_THUMBSIZE', 160)
SHARE_DEFAULT = getattr(settings, 'THEME_SHARE_DEFAULT', None)
ACE_DIR = getattr(settings, 'THEME_ACE_DIR', '')
CODEMIRROR_DIR = getattr(settings, 'THEME_CODEMIRROR_DIR', '')
CSS_RESET_URL = getattr(settings, 'THEME_CSS_RESET_URL',
    urljoin(getattr(settings, 'STATIC_URL'), 'djangocms_theme/css/reset.css'))
TEMPLATE_TYPES = getattr(settings, 'THEME_TEMPLATE_TYPES',
                                   (('default', 'Default'),))
TEMPLATE_MAPPING = getattr(settings, 'THEME_TEMPLATE_MAPPING', None)
