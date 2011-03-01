var deform  = {
    callbacks: [],

    addCallback: function (oid, callback) {
        deform.callbacks.push([oid, callback])
    },

    clearCallbacks: function () {
        deform.callbacks = [];
    },

    load: function() {
        $(function() {
            deform.processCallbacks();
            deform.focusFirstInput();
            });
    },
            

    processCallbacks: function () {
        $(deform.callbacks).each(function(num, item) {
            var oid = item[0];
            var callback = item[1];
            callback(oid);
            }
            );
        deform.clearCallbacks();
    },

    addSequenceItem: function (protonode, before) {
        // - Clone the prototype node and add it before the "before" node.
        //   Also ensure any callbacks are run for the widget.

        // In order to avoid breaking accessibility:
        //
        // - Find each tag within the prototype node with an id
        //   that has the string ``deformField(\d+)`` within it, and modify 
        //   its id to have a random component.
        // - For each label referencing an change id, change the label's
        //   htmlFor attribute to the new id.

        var fieldmatch = /deformField(\d+)/;
        var namematch = /(.+)?-[#]{3}/;
        var code = protonode.attr('prototype');
        var html = decodeURIComponent(code);
        var $htmlnode = $(html);
        var $idnodes = $htmlnode.find('[id]');
        var $namednodes = $htmlnode.find('[name]');
        var genid = deform.randomString(6);
        var idmap = {};

        // replace ids containing ``deformField`` and associated label for= 
        // items which point at them

        $idnodes.each(function(idx, node) {
            var $node = $(node);
            var oldid = $node.attr('id');
            var newid = oldid.replace(fieldmatch, "deformField$1-" + genid);
            $node.attr('id', newid);
            idmap[oldid] = newid;
            var labelselector = 'label[htmlFor=' + oldid + ']';
            var $fornodes = $htmlnode.find(labelselector);
            $fornodes.attr('htmlFor', newid);
            });

        // replace names a containing ```deformField`` like we do for ids

        $namednodes.each(function(idx, node) {
            var $node = $(node);
            var oldname = $node.attr('name');
            var newname = oldname.replace(fieldmatch, "deformField$1-" + genid);
            $node.attr('name', newname);
            });

        var anchorid = genid + '-anchor';
        var anchortext = '<a name="' + anchorid +'" id="' + anchorid + '"/>' 
        $(anchortext).insertBefore(before);
        $htmlnode.insertBefore(before);

        $(deform.callbacks).each(function(num, item) {
            var oid = item[0];
            var callback = item[1];
            var newid = idmap[oid];
            if (newid) { 
                callback(newid)
                };
            });

        deform.clearCallbacks();
        var old_len = parseInt(before.attr('now_len')||'0');
        before.attr('now_len', old_len + 1);
        //deform.maybeScrollIntoView('#' + anchorid);
    },

    appendSequenceItem: function(node) {
        var $oid_node = $(node).parent();
        var $proto_node = $oid_node.children('.deformProto').first();
        var $before_node = $oid_node.children('ul').first().children(
                                              '.deformInsertBefore');
        var min_len = parseInt($before_node.attr('min_len')||'0');
        var max_len = parseInt($before_node.attr('max_len')||'9999');
        var now_len = parseInt($before_node.attr('now_len')||'0');
        if (now_len < max_len) {
            deform.addSequenceItem($proto_node, $before_node);
            deform.processSequenceButtons($oid_node, min_len, max_len, 
                                          now_len+1);
        };
        return false;
    },

    removeSequenceItem: function(clicked) {
        var $item_node = $(clicked).parent();
        var $oid_node = $item_node.parent().parent();
        var $before_node = $oid_node.find('.deformInsertBefore').first();
        var min_len = parseInt($before_node.attr('min_len')||'0');
        var max_len = parseInt($before_node.attr('max_len')||'9999');
        var now_len = parseInt($before_node.attr('now_len')||'0');
        if (now_len > min_len) {
            $before_node.attr('now_len', now_len - 1);
            $item_node.remove();
            deform.processSequenceButtons($oid_node, min_len, max_len, 
                                          now_len-1);
        };
        return false;
    },

    processSequenceButtons: function(oid_node, min_len, max_len, now_len) {
        var $ul = oid_node.children('ul');
        var $lis = $ul.children('li');
        $lis.find('.deformClosebutton').removeClass('deformClosebuttonActive');
        oid_node.children('.deformSeqAdd').show();
        if (now_len > min_len) {
            $lis.find('.deformClosebutton').addClass('deformClosebuttonActive');
        };
        if (now_len >= max_len) {
            oid_node.children('.deformSeqAdd').hide();
        };
    },

    maybeScrollIntoView: function(element_id) {
        var viewportWidth = $(window).width(),
            viewportHeight = $(window).height(),
            documentScrollTop = $(document).scrollTop(),
            documentScrollLeft = $(document).scrollLeft(),
            minTop = documentScrollTop,
            maxTop = documentScrollTop + viewportHeight,
            minLeft = documentScrollLeft,
            maxLeft = documentScrollLeft + viewportWidth,
            element = document.getElementById(element_id),
            elementOffset = $(element_id).offset();
        if (
            !(elementOffset.top > minTop && elementOffset.top < maxTop) &&
            !(elementOffset.left > minLeft && elementOffset.left < maxLeft)
            ) {
                element.scrollIntoView();
            };
    },

    focusFirstInput: function () {
        var input = $(':input').filter('[id ^= deformField]').first();
        if (input) {
            var raw = input.get(0);
            if (raw) {
                if (raw.type === 'text' || raw.type === 'file' || 
                    raw.type == 'password' || raw.type == 'text' || 
                    raw.type == 'textarea') { 
                    if (raw.className != "hasDatepicker") {
                        input.focus();
                    };
                };
            };
        };
    },

    randomString: function (length) {
        var chr='0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz';
        var chr = chr.split('');
    
        if (! length) {
            length = Math.floor(Math.random() * chr.length);
        };
    
        var str = '';
        for (var i = 0; i < length; i++) {
            str += chr[Math.floor(Math.random() * chr.length)];
        };
        return str;
    }

};
