from PIL import Image

from django.core.files.base import File
from django.utils.html import mark_safe, format_html, format_html_join
from django.utils.encoding import force_text
from django import forms

from djangocms_theme.settings import THUMBSIZE
from djangocms_theme.models import Theme


class ThemeForm(forms.ModelForm):
    """
    Implements image upload resizing and format conversion as a form
    validation method.  Note that the image is renamed by an "upload_to"
    method on the model field.
    """
    def clean_screenshot(self):
        ss = self.cleaned_data['screenshot']
        if ss:
            if isinstance(ss, File):
                # Pillow thinks that any django File is an actual file,
                # even if it is a stream.
                file = ss.file
            else:
                file = ss
            stream = (not file.closed and hasattr(file, 'seek')
                                      and callable(file.seek))
            img = Image.open(file)
            if img.width > THUMBSIZE or img.height > THUMBSIZE:
                img.thumbnail((THUMBSIZE, THUMBSIZE))
                if stream:
                    file.truncate()
                    file.seek(0)
                img.save(file, 'PNG')
                if stream:
                    file.seek(0)
        return ss

    class Media:
        # See https://github.com/divio/djangocms-admin-style/issues/372
        css = {
            'all': ('djangocms_theme/css/fix-related-image.css',)
        }

class GridModelChoiceField(forms.ModelChoiceField):
    """
    Subclass theme ForeignKey formfield to override the label so
    that it shows the theme screenshot if it's set.
    """
    def label_from_instance(self, obj):
        if obj.screenshot:
            return mark_safe('%s<br /><img src="%s" />' %
                             (obj.name, obj.screenshot.url))
        else:
            return obj.name

# -- can't do this anymore
#class GridRadioRenderer(forms.RadioSelect.renderer):
#    """
#    Subclass the Radio widget renderer to change the template for
#    selecting themes in the admin.
#    """
#    fmt = '<span style="max-width:%dpx;">{}</span>' % THUMBSIZE
#    def render(self):
#        return format_html('<div class="theme_radio_grid">\n{}\n</div>',
#            format_html_join('\n', self.fmt, ((force_text(w),) for w in self)))

class GridRadioSelect(forms.RadioSelect):
    """
    Subclass the Radio widget to wrap the template in a div that can be
    styled as a grid.
    """
    def render(self, *args, **kwargs):
        html = super(GridRadioSelect, self).render(*args, **kwargs)
        return mark_safe('<div class="theme_radio_grid">\n%s\n</div>' % html)

class PageThemeForm(forms.ModelForm):
    def clean_theme(self):
        # implements theme/page permissions
        theme = self.cleaned_data['theme']
        if theme and not theme.can_use(self.instance):
            raise forms.ValidationError('This theme is restricted.')
        return theme

    class Media:
        css = {
            'all': ('djangocms_theme/css/radio-grid.css',)
        }
        #
        # Before 1.9, the related widget change link only works on
        # select widgets.  This is a hack to make it work with our
        # radio widget.  Drop this when 1.8 support is dropped.
        #
        from django import VERSION
        if VERSION < (1,9):
            js = ('djangocms_theme/js/fix-related.js',)
