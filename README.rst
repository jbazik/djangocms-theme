==============================
Per-Page Themes for Django-CMS
==============================

Allow page owners to manage stylesheets.  Adds a "theme" field to the
Django-CMS page model (via a PageExtension) and an admin interface for
uploading and managing themes.

Themes are collections of images, fonts and stylesheets that can be
applied to your site's templates.  Djangocms-theme allows page authors
to apply existing themes to their pages or create new ones.

Features
--------

* Themes can be applied to all of a page's descendents.

* New themes can be based on existing themes.

* Themes have owner and group permissions, and can be restricted or
  made available to all.

* Stylesheets can be edited directly in the admin interface, optionally
  using popular browser-based editors.

Requirements
------------

Requires:

* Django 1.8+

* Django-CMS 3.0+

* Pillow

Installation and Configuration
------------------------------
1. Install djangocms_theme

::

    pip install djangocms_theme

2. Create djangocms_theme's database tables

::

    python manage.py migrate djangocms_theme

3. Add djangocms_theme to your INSTALLED_APPS

::

    INSTALLED_APPS = (
        ...,
        djangocms_theme,
        ...,
    )

4. Add the "theme" tag to your template(s)

::

    {% load theme %}
    <html>
    <head>
    ...
    {% theme %}
    ...
    </head>
    ...

Settings
--------

THEME_THUMBSIZE
  Integer size, in pixels, of the longest dimension of a screenshot image.
  Larger images are automatically resized.  Default is 160.

THEME_SHARE_DEFAULT
  One of 'owner', 'group' or 'any' (fix this, use symbols)

THEME_ACE_PATH
  Absolute filesystem path of the
  `Ace javascript code editor <https://ace.c9.io/>_`.
  If set, the stylesheet textarea widget uses the Ace editor.

THEME_CODEMIRROR_PATH
  Absolute filesystem path of the
  `CodeMirror javascript code editor <http://codemirror.net/>_`.
  If set, the stylesheet textarea widget uses the CodeMirror editor.

THEME_CSS_RESET_URL
  Url of a CSS reset to use for themes that require one.  The default
  is a built-in copy of Eric Meyer's well-known (and public domain) reset.

THEME_TEMPLATE_TYPES
  A list of template types for associating themes with templates.
  A template type represents all templates that provide a common html
  structure, including ids and classes, that are referenced by a theme.
  Defaults to a single "default" type.  Example::

    THEME_TEMPLATE_TYPES = (
        ('page', _('Page')),
        ('blog', _('Blog')),
    )

THEME_TEMPLATE_MAPPING
  A dictionary that associates template types to CMS templates.  Themes
  are offered only for templates of a particular type.  Mappings may
  overlap.  If there is only one THEME_TEMPLATE_TYPE, then defaults to
  a mapping of that theme to all templates in CMS_TEMPLATES. Example::

    THEME_TEMPLATE_MAPPING = {
        'page': ('simple_page.html', 'complex_page.html'),
        'blog': ('blog.html',),
    }
