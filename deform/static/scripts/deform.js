function add_new_item(source) {
    var protonode = source.previousElementSibling;
    var code = protonode.attributes['prototype'].value;
    var html = decodeURIComponent(code);
    node = document.createElement('div')
    node.innerHTML = html;
    source.appendChild(node);
}
