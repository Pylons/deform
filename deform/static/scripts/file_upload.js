/* Ripped off from
*  http://www.abeautifulsite.net/blog/2013/08/whipping-file-inputs-into-shape-with-bootstrap-3/
*/

$(document).on('change', '.btn-file :file', function() {
    var $file_input = $(this);
    var filename = $file_input.val().replace(/\\/g, '/').replace(/.*\//, '');
    var $group = $file_input.parents('.input-group')
    $group.find(':text').val(filename);
    $group.find('.btn-file').addClass('upload-have-file');
});
