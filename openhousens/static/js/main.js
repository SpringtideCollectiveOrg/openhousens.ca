$(function () {
  // @see https://dev.twitter.com/docs/share-bookmarklet
  $('.twitter').click(function (event) {
    event.preventDefault();
    var width = 550
      , height = 450
      , top = 0
      , left = Math.round((screen.width / 2) - (width / 2));
    if (screen.height > height) {
      top = Math.round((screen.height / 2) - (height / 2));
    }
    window.open(this.href, '', 'width=' + width +
      ',height=' + height + ',left=' + left, ',top=' + top +
      'personalbar=0,toolbar=0,scrollbars=1,resizable=1');
  });

  var $tablesorter = $('.tablesorter');
  if ($tablesorter.length) {
    $tablesorter.tablesorter({
      sortList: [[1, 0]]
    , textExtraction: function (node) {
        if (node.className.indexOf('modified') !== -1) {
          return node.children[0].getAttribute('datetime');
        }
        else {
          return node.innerHTML;
        }
      }
    , widgets: ['filter']
    , widgetOptions: {
        filter_columnFilters: false
      , filter_external: '.form-filter input'
      }
    });
  }

  $('.truncatable').each(function () {
    if (this.clientHeight < this.scrollHeight) {
      $('<div class="expand-fade"></div>').appendTo(this);
      $('<div class="expand-link"><span class="glyphicon glyphicon-chevron-down"></span> see more</div>').click(function () {
        $(this).hide()
          .parent().children('.expand-fade').hide()
          .parent().animate({
            maxHeight: '800px'
          }, {
            easing: 'linear'
          , complete: function () {
            $(this).css('max-height', 'none');
          }})
      }).appendTo(this);
    }
  });
});
