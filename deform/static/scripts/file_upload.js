/**
* Nicer looking file inputs for bootstrap 3
* By Jeff Dairiki <dairiki@dairiki.org> based on ideas from
*  http://www.abeautifulsite.net/blog/2013/08/whipping-file-inputs-into-shape-with-bootstrap-3/
*/
(function ($) {

    var Upload = function (element, options) {
        this.$element = $(element);
        this.options = $.extend({}, Upload.DEFAULTS,
                                this.$element.data(),
                                options);

        this.orig_style = this.$element.attr('style');
        this.$input_group = $(this.options.template)
            .replaceAll(this.$element)
            .attr('style', this.orig_style)
            .css({position: 'relative', overflow: 'hidden'});
        this.$input_group.find(':text').before(this.$element);
        this.$element
            .on('change.deform.upload', $.proxy(this, 'update'))
            .css(this.options.element_style);
        this.update();
    };

    Upload.DEFAULTS = {
        filename: null,
        selectfile: 'Select file…',
        changefile: 'Change file…',

        template: '<div>'
            + '<div class="input-group">'
            + '<span class="input-group-btn">'
            + '<span class="btn btn-default btn-file"></span>'
            + '</span>'
            + '<input type="text" readonly=""'
            + ' class="form-control upload-filename"/>'
            + '</div>'
            + '</div>',

        element_style: {
            position: 'absolute',
            /* Older FF (3.5) seems to put a margin on the bottom of
            *  the file input (the margin is proportional to
            *  font-size, so in this case it's significant.)  Shift
            *  bottom a bit to allow for some slop.
            */
            //bottom: '0',
            bottom: '-40px',
            right: '0',
            minWidth: '100%',
            minHeight: '100%',
            fontSize: '999px',
            textAlign: 'right',
            filter: 'alpha(opacity=0)',
            opacity: '0',
            background: 'red',
            cursor: 'inherit',
            display: 'block'
        }
    };

    Upload.prototype.update = function () {
        var selected_filename = this.$element.val().replace(/.*[\\\/]/, ''),
            options = this.options,
            filename = selected_filename || options.filename;
        this.$input_group.find(':text')
            .val(filename);
        this.$input_group.find('.btn-file')
            .text(filename ? options.changefile : options.selectfile);
    };

    Upload.prototype.destroy = function () {
        this.$element
            .off('.deform.upload')
            .attr('style', this.orig_style || null)
            .replaceAll(this.$input_group)
            .removeData('deform.upload');
    };


    ////////////////////////////////////////////////////////////////
    // plugin definition

    var old = $.fn.upload;

    $.fn.upload = function (option) {
        return this.each(function () {
            var $this = $(this),
                data = $this.data('deform.upload');
            if (!data) {
                var options = typeof option == 'object' && option;
                data = new Upload(this, options);
                $this.data('deform.upload', data);
            }
            if (typeof option == 'string') {
                data[option]();
            }
        });
    };

    $.fn.upload.Constructor = Upload;

    $.fn.upload.noConflict = function () {
        $.fn.upload = old;
        return this;
    };

})(window.jQuery);
