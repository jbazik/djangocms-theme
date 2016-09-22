import os

from django.forms import Textarea

from djangocms_theme.settings import ACE_DIR, CODEMIRROR_DIR


class TextareaAce(Textarea):
    def render(self, name, value, attrs=None):
        attrs.update({'style': "display:none"})
        html = super(TextareaAce, self).render(name, value, attrs)
        return mark_safe("\n".join([html,
            '<div id="edit_%s"></div>' % name,
            '<script type="text/javascript">',
            '  var session = ace.edit("edit_%s").getSession();' % name,
            '  session.setValue(textarea.val());',
            '  session.on("change", function(){',
            '    textarea.val(session.getValue());});',
            '</script>', '']))

    class Media:
        js = tuple(os.path.join(ACE_DIR, 'acejs', f) for f in (
            'ace.js',
            'mode-css.js',
            'ace_start.js',
        ))
        css = {'all': tuple(os.path.join(ACE_DIR, 'acecss', f) for f in (
            'defaultace.css',
        ))}

class TextareaCodeMirror(Textarea):
    def render(self, name, value, attrs=None):
        html = super(TextareaCodeMirror, self).render(name, value, attrs)
        return mark_safe("\n".join([html,
            '<script type="text/javascript">',
            'CodeMirror.fromTextArea(document.getElementById("id_%s")' % name,
            '</script>', '']))

    class Media:
        js = tuple(os.path.join(CODEMIRROR_DIR, f) for f in (
            'codemirror.js',
            os.path.join('mode', 'javascript', 'javascript.js'),
        ))
        css = {'all': tuple(os.path.join(CODEMIRROR_DIR, f) for f in (
            'codemirror.css',
        ))}

if ACE_DIR:
    TextWidget = TextareaAce
elif CODEMIRROR_DIR:
    TextWidget = TextareaCodeMirror
else:
    TextWidget = Textarea
