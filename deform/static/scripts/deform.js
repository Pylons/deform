function add_new_item(protonode, before) {
    // - Clone the prototype node.
    // - Find all the labels in the prototype node.
    // - For each label referencing an id, find the node with that id.
    // - Change the label reference and the node id to a random string. 
    // - Add the cloned node to the sequence before the "before" node
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
    $node.insertBefore(before);
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
