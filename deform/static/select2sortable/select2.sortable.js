(function($) {

  function getSortableUl($select) {
    return $select.prev('.select2-container').find('ul.select2-choices');
  };

  function initSortableUl($ul, options) {

    $ul.select2sortable({
      forcePlaceholderSize: true,
      items: 'li.select2-search-choice',
      placeholder : '<li>&nbsp;</li>'
    });

    // Only bind event at initialization
    if (options && options.bindSortEvent && options.$select) {
      $ul.bind('sortupdate', function(e, ui) {
        $($ul.find('li.select2-search-choice').get().reverse()).each(function() {
          var id = $(this).data('select2Data').id,
          $option = options.$select.find('option[value="' + id + '"]')[0];

          options.$select.prepend($option);
        });
      });
    }
  };

  function initSelect2Sortable($select) {

    var observer,
        $ul;

    $select.select2();
    $ul = getSortableUl($select);

    observer = new MutationObserver(function(mutations) {
      initSortableUl($ul);
      observer.disconnect();
    });

    $select.on('select2-selecting', function() {
      observer.observe($ul.get(0), { subtree: false, childList: true, attributes: false });
    });

    initSortableUl($ul, { bindSortEvent: true, $select: $select });

    $select.data('hasSelect2Sortable', true);
  };


  function sortSelect2Sortable($select, val) {
    var $ul = getSortableUl($select),
        $lis = $ul.find('.select2-search-choice');

    $.each(val, function(i, id) {
      $lis.each(function() {
        if (id == $(this).data('select2Data').id) {
          $(this).insertBefore($ul.find('.select2-search-field'));
        }
      });
    });

    $ul.trigger('sortupdate');
  }

  $.fn.extend({

    select2Sortable: function(val) {

      this.each(function() {

        var $select = $(this);

        if (!$select.prop('multiple')) {
          return;
        }

        if (!$select.data('hasSelect2Sortable')) {
          initSelect2Sortable($select);

          var values = $select.attr('data-order');

          if (values) {
            sortSelect2Sortable($select, values.split(','));
          }
        }

        if (val) {
          sortSelect2Sortable($select, val);
        }
      });

      return this;
    }
  });
}(window.jQuery));
