function deformAddNewItem(protonode, before) {
    // - Clone the prototype node and add it before the "before" node.

    // In order to avoid breaking accessibility:
    //
    // - Find all the label tags within the prototype node.
    // - For each label referencing an id, find the node with that id.
    // - Change the label reference and the node id to a random string. 

    var code = protonode.attributes['prototype'].value;
    var html = decodeURIComponent(code);
    var $node = $(html);
    var $labels = $node.find('label');
    var labeled = {};

    // find all labels for each id
    for (var i = 0; i < $labels.length; i++) {
        var label = $labels.get(i);
        var labelid = label.htmlFor;
        if (labelid) {
            var tmp = labeled[labelid] || [];
            tmp.push(label);
            labeled[labelid] = tmp;
        };
    };

    // for each labelid, find the node it points to and replace its id
    // with a generated id; also set the for= attribute of the labels
    // which reference to the same generated id
    for (labelid in labeled) {
        var labels = labeled[labelid];
        var genid = randomString(10);
        $node.find('#' + labelid).attr('id', genid);
        for (var i = 0; i < labels.length; i++) {
            var label = labels[i];
            label.htmlFor = genid;
        };
    };
    $node.insertBefore(before);
}

function randomString(length) {
    var chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz';
    var chars = chars.split('');
    
    if (! length) {
        length = Math.floor(Math.random() * chars.length);
    }
    
    var str = '';
    for (var i = 0; i < length; i++) {
        str += chars[Math.floor(Math.random() * chars.length)];
    }
    return str;
}

function deformFocusFirstInput() {
    var input = $(':input').filter('[id ^= deformField]').first();
    if (input) {
        var raw = input.get(0);
        if (raw.type === 'text' || raw.type === 'file' || 
            raw.type == 'password' || raw.type == 'text' || 
            raw.type == 'textarea') { 
            input.focus();
        };
    };
};
