var deform  = {

    addSequenceItem: function (protonode, before) {
        // - Clone the prototype node and add it before the "before" node.

        // In order to avoid breaking accessibility:
        //
        // - Find each tag within the prototype node with an id
        //   that has the string ``deformField(\d+)`` within it, and modify 
        //   its id to have a random component.
        // - For each label referencing an change id, change the label's
        //   htmlFor attribute to the new id.

        var fieldmatch = /deformField(\d+)/;
        var code = protonode.attributes['prototype'].value;
        var html = decodeURIComponent(code);
        var $htmlnode = $(html);
        var $idnodes = $htmlnode.find('[id]');
        var genid = deform.randomString(6);

        $idnodes.each(function(idx, node) {
            var $node = $(node);
            var oldid = $node.attr('id');
            var newid = oldid.replace(fieldmatch, "deformField$1-" + genid);
            $node.attr('id', newid);

            var labelselector = 'label[htmlFor=' + oldid + ']';
            var $fornodes = $htmlnode.find(labelselector);
            $fornodes.attr('htmlFor', newid);
            });

        $htmlnode.insertBefore(before);
    },

    focusFirstInput: function () {
        var input = $(':input').filter('[id ^= deformField]').first();
        if (input) {
            var raw = input.get(0);
            if (raw) {
                if (raw.type === 'text' || raw.type === 'file' || 
                    raw.type == 'password' || raw.type == 'text' || 
                    raw.type == 'textarea') { 
                    input.focus();
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
