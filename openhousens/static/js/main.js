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

  $('.tablesorter').tablesorter({
    sortList: [[1, 0]],
    textExtraction: function (node) { 
      if (node.className === 'hidden-xs modified') {
        return node.getAttribute('data-modified');
      }
      else {
        return node.innerHTML;
      }
    } 
  });
});
