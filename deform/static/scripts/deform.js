function last_sibling(node) {
    var tempObj=node.parentNode.lastChild;
    // nodeType 1 == element
    while(tempObj.nodeType != 1 && tempObj.previousSibling != null) {
        tempObj=tempObj.previousSibling;
    }
    return (tempObj.nodeType == 1) ? tempObj: false;
}

function insert_after(node, target) {
    target.parentNode.insertBefore(node, target);
}
    
function add_new_item(source) {
    var protonode = source.previousElementSibling;
    var code = protonode.attributes['prototype'].value;
    var html = decodeURIComponent(code);
    var node = document.createElement('div');
    node.innerHTML = html;
    insert_after(node.firstChild, last_sibling(source));
}
