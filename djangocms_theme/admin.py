from django.db import models
from django.forms import ValidationError, RadioSelect
from django.contrib import admin

from cms.extensions import PageExtensionAdmin

from djangocms_theme.widgets import TextWidget
from djangocms_theme.forms import (ThemeForm, PageThemeForm,
                                   GridModelChoiceField, GridRadioSelect)
from djangocms_theme.models import (Theme, Image, FontFamily, Font, FontSrc,
                                    Stylesheet, PageTheme)


class PermissionMixin(object):

    def get_readonly_fields(self, request, obj=None):
        if obj:
            if not obj.can_meta(request.user):
                return ('owner', 'group', 'share')
        return ()

    def has_change_permission(self, request, obj=None):
        if obj:
            return obj.can_edit(request.user)
        return super(PermissionMixin, self).has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj:
            return obj.can_meta(request.user)
        return super(PermissionMixin, self).has_delete_permission(request, obj)

    def get_queryset(self, request):
        qs = super(PermissionMixin, self).get_queryset(request)
        return qs.can_edit(request.user)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        obj.save()

class ImageInline(admin.TabularInline):
    model = Theme.images.through
    verbose_name_plural = "Images used by this theme"
    extra = 0
    fields = ('name', 'origin', 'owner', 'group')

class FontFamilyInline(admin.TabularInline):
    model = Theme.fontfams.through
    verbose_name_plural = "Font families used by this theme"
    extra = 0
    fields = ('name', 'origin', 'license', 'owner', 'group')

class FontInline(admin.TabularInline):
    model = Font
    verbose_name_plural = "Fonts in this font family"
    extra = 0
    show_change_link = True
    #fields = ('family',)

class FontSrcInline(admin.TabularInline):
    model = FontSrc
    verbose_name_plural = "Font files"
    extra = 0
    fields = ('format', 'local', 'file')

class StylesheetInline(admin.TabularInline):
    model = Stylesheet
    extra = 0
    fields = ('css', 'media')

@admin.register(Image)
class ImageAdmin(PermissionMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'image', 'description'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('share', 'owner', 'group'),
        }),
    )
    list_display = ('name', 'origin', 'owner', 'group')
    list_filter = ('origin',
                   ('owner', admin.RelatedOnlyFieldListFilter),
                   ('group', admin.RelatedOnlyFieldListFilter))
    search_fields = ('name', 'origin', 'description')

@admin.register(FontFamily)
class FontFamilyAdmin(PermissionMixin, admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('name', 'origin', 'license'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('share', 'owner', 'group'),
        }),
    )
    list_display = ('name', 'origin', 'owner', 'group')
    list_filter = ('origin', 'license',
                   ('owner', admin.RelatedOnlyFieldListFilter),
                   ('group', admin.RelatedOnlyFieldListFilter))
    search_fields = ('name', 'origin')
    inlines = [FontInline]

@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {
            'fields': ('family', 'variant', 'stretch', 'weight', 'style'),
        }),
    )
    readonly_fields = ('family',)
    list_display = ('family',  'weight', 'style', 'stretch', 'variant')
    list_filter = ('weight', 'style', 'stretch', 'variant')
    search_fields = ('family',)
    inlines = [FontSrcInline]

@admin.register(Theme)
class ThemeAdmin(PermissionMixin, admin.ModelAdmin):
    form = ThemeForm
    fieldsets = (
        (None, {
            'fields': (('name', 'origin'),
                       ('description', 'screenshot'),
                       ('parent', 'reset'),
                       'images', 'fontfams'),
        }),
        ('Permissions', {
            'classes': ('collapse',),
            'fields': ('share', 'owner', 'group'),
        }),
    )
    formfield_overrides = {
        models.TextField: {'widget': TextWidget()},
    }
    list_display = ('name', 'origin', 'owner', 'group')
    list_filter = ('origin',
                   ('owner', admin.RelatedOnlyFieldListFilter),
                   ('group', admin.RelatedOnlyFieldListFilter))
    filter_horizontal = ('images', 'fontfams')
    search_fields = ('name', 'origin', 'description')
    inlines = [StylesheetInline]

    def get_form(self, request, obj=None, **kwargs):
        """
        The parent relationship isn't where you want to add or modify themes.
        """
        form = super(ThemeAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['parent'].widget.can_add_related = False
        form.base_fields['parent'].widget.can_change_related = False
        return form

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """
        Only show choices that a user can use.
        """
        if db_field.name == 'images':
            kwargs['queryset'] = Image.objects.can_use(request.user)
        elif db_field.name == 'fontfams':
            kwargs['queryset'] = FontFamily.objects.can_use(request.user)
        return super(ThemeAdmin, self).formfield_for_manytomany(
                                       db_field, request, **kwargs)

    class Media:
        css = {
            "all": (Font.all_rules_url,),
        }

@admin.register(PageTheme)
class PageThemeAdmin(PageExtensionAdmin):
    form = PageThemeForm

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """
        Replace the form field for theme selection to one that renders
        a grid of screenshots.  Doing this here, rather than directly
        in the form, prevents interfering with the related model wrapper
        the admin adds (which appends the "change" and "add" links).

        Only show themes that request.user can use.  It might make
        more sense to show themes that request.current_page can use,
        but the logic there is dense and changes to page permissions
        would require listening to cms signals, etc.
        """
        if db_field.name == 'theme':
            kwargs['queryset'] = Theme.objects.can_use(request.user)
            kwargs['widget'] = GridRadioSelect()
            kwargs['empty_label'] = 'No Theme'
            kwargs['form_class'] = GridModelChoiceField
        return super(PageThemeAdmin, self).formfield_for_foreignkey(
                                               db_field, request, **kwargs)
