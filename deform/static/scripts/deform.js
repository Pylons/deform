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
    // - Clone the prototype node.
    // - Find all the labels in the prototype node.
    // - For each label referencing an id, find the node with that id.
    // - Change the label reference and the node id to a random string. 
    // - Add the cloned node to the sequence.
    var protonode = source.previousElementSibling;
    var code = protonode.attributes['prototype'].value;
    var html = decodeURIComponent(code);
    var $node = $(html);
    var $labels = $node.find('label');
    for (var i = 0; i < $labels.length; i++) {
        var label = $labels.get(i);
        var labelid = label.htmlFor;
        if (labelid) {
            genid = randomString(10);
            $node.find('#' + labelid).attr('id', genid);
            label.htmlFor = genid;
        };
    };
    insert_after($node[0], last_sibling(source));
}

function remove_parent(source) {
    source.parentNode.parentNode.removeChild(source.parentNode);
}

function randomString(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz'.split('');
    
    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }
    
    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}

