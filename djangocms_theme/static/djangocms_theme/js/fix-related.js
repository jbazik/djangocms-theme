django.jQuery(function($){
    //
    // This is a hacked version of admin/related-widget-wrapper.js
    // from django1.8.  Because we're using a radio in place of a select,
    // the django code does not work, so it is expediently munged here.
    // It appears this approach was abandoned in django1.9, so this is a
    // very specific hack.
    //
    function updateLinks() {
        var $this = $(this);
        var siblings = $this.closest('div').nextAll('.change-related, .delete-related');
        if (!siblings.length) return;
        var value = $this.val();
        if (value) {
            siblings.each(function(){
                var elm = $(this);
                elm.attr('href', elm.attr('data-href-template').replace('__fk__', value));
            });
        } else siblings.removeAttr('href');
    }
    var container = $(document);
    container.on('change', '.related-widget-wrapper input[type="radio"]', updateLinks);
    container.find('.related-widget-wrapper input[type="radio"][checked]').each(updateLinks);
    container.on('click', '.related-widget-wrapper-link', function(event){
        if (this.href) {
            showRelatedObjectPopup(this);
        }
        event.preventDefault();
    });
});
