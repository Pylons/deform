/*
 * deform client-side support (vanilla JS, no jQuery).
 *
 * Register a top-level callback with deform.addCallback(oid, fn); it will be
 * invoked once the DOM has finished loading (and again for cloned sequence
 * items and for content swapped in by an AJAX library).
 */

document.addEventListener("DOMContentLoaded", function () {
    deform.load();
});

var deform_loaded = false;

var deform = {
    callbacks: [],

    addCallback: function (oid, callback) {
        deform.callbacks.push([oid, callback]);
    },

    clearCallbacks: function () {
        deform.callbacks = [];
    },

    load: function () {
        if (!deform_loaded) {
            deform.processCallbacks();
            deform.ajaxify();
            deform_loaded = true;
        }
    },

    /*
     * Run (and then clear) all pending callbacks. An optional ``scope`` may be
     * passed to limit the run; callbacks always receive their oid, so scope is
     * only advisory and mostly used by the AJAX re-init hook.
     */
    processCallbacks: function (scope) {
        deform.callbacks.forEach(function (item) {
            var oid = item[0];
            var callback = item[1];
            callback(oid);
        });
        deform.clearCallbacks();
    },

    /*
     * Vanilla AJAX submission for forms with data-deform-ajax="true".
     * Intercepts the submit event, POSTs via fetch(), and swaps the form
     * element with the response (outerHTML).  Handles the H-Redirect response
     * header.  No external library required.
     */
    ajaxify: function () {
        document.addEventListener("submit", function (e) {
            var form = e.target;
            if (!form.matches || !form.matches("form[data-deform-ajax]")) {
                return;
            }
            e.preventDefault();
            var action = form.getAttribute("action") || location.href;
            var fd = new FormData(form);
            // Include the submit button's name/value (the browser does this
            // for native submissions but not for FormData constructed from
            // the form element).
            var submitter = e.submitter;
            if (submitter && submitter.name) {
                fd.append(submitter.name, submitter.value);
            }
            fetch(action, {
                method: "POST",
                body: fd,
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                },
            })
                .then(function (resp) {
                    var redirect = resp.headers.get("X-Redirect");
                    if (redirect) {
                        location.href = redirect;
                        return;
                    }
                    return resp.text().then(function (html) {
                        var tpl = document.createElement("template");
                        tpl.innerHTML = html.trim();
                        var next = tpl.content.firstElementChild;
                        if (next) {
                            form.replaceWith(next);
                        }
                        deform.processCallbacks();
                    });
                })
                .catch(function (err) {
                    console.error("deform AJAX submit failed:", err);
                });
        }, true);
    },

    addSequenceItem: function (protonode, before) {
        // - Clone the prototype node and add it before the "before" node.
        //   Also ensure any callbacks are run for the widget.
        //
        // In order to avoid breaking accessibility:
        //
        // - Find each tag within the prototype node with an id that has the
        //   string ``deformField(\d+)`` within it, and modify its id to have a
        //   random component.
        // - For each label referencing a changed id, change the label's ``for``
        //   attribute to the new id.

        var fieldmatch = /deformField(\d+)/;
        var code = protonode.getAttribute("prototype");
        var html = decodeURIComponent(code);

        // Parse the prototype HTML into a document fragment.
        var template = document.createElement("template");
        template.innerHTML = html.trim();
        var fragment = template.content;

        var genid = deform.randomString(6);
        var idmap = {};

        // Replace ids containing ``deformField`` and the ``for`` attribute of
        // any label pointing at them.
        var idnodes = fragment.querySelectorAll("[id]");
        idnodes.forEach(function (node) {
            var oldid = node.getAttribute("id");
            var newid = oldid.replace(fieldmatch, "deformField$1-" + genid);
            node.setAttribute("id", newid);
            idmap[oldid] = newid;
            var fornodes = fragment.querySelectorAll(
                'label[for="' + oldid + '"]'
            );
            fornodes.forEach(function (fornode) {
                fornode.setAttribute("for", newid);
            });
        });

        // Replace names containing ``deformField`` like we do for ids.
        var namednodes = fragment.querySelectorAll("[name]");
        namednodes.forEach(function (node) {
            var oldname = node.getAttribute("name");
            var newname = oldname.replace(fieldmatch, "deformField$1-" + genid);
            node.setAttribute("name", newname);
        });

        // Collect the top-level element nodes before they are moved into the
        // DOM (insertBefore empties the fragment).
        var inserted = Array.prototype.filter.call(
            fragment.childNodes,
            function (n) {
                return n.nodeType === 1;
            }
        );

        before.parentNode.insertBefore(fragment, before);

        // Scripts inserted via innerHTML/template are inert; re-execute them so
        // any ``deform.addCallback(...)`` in a widget prototype re-registers
        // its callback (keyed on the prototype's original oid). We then invoke
        // those callbacks with the cloned node's new id via ``idmap``.
        inserted.forEach(function (node) {
            var scripts =
                node.tagName === "SCRIPT"
                    ? [node]
                    : Array.prototype.slice.call(
                          node.querySelectorAll("script")
                      );
            scripts.forEach(function (old) {
                var s = document.createElement("script");
                if (old.type) {
                    s.type = old.type;
                }
                s.text = old.textContent;
                old.parentNode.replaceChild(s, old);
            });
        });

        // Run callbacks for the freshly inserted widgets.
        deform.callbacks.forEach(function (item) {
            var oid = item[0];
            var callback = item[1];
            var newid = idmap[oid];
            if (newid) {
                callback(newid);
            }
        });
        deform.clearCallbacks();

        var old_len = parseInt(before.getAttribute("now_len") || "0", 10);
        before.setAttribute("now_len", old_len + 1);

        // We added something to the DOM; trigger a change event so listeners
        // can react.
        inserted.forEach(function (node) {
            node.dispatchEvent(new Event("change", { bubbles: true }));
        });
    },

    appendSequenceItem: function (node) {
        var oid_node = node.closest(".deform-seq");
        var proto_node = oid_node.querySelector(".deform-proto");
        var before_nodes = oid_node.querySelectorAll(".deform-insert-before");
        var before_node = before_nodes[before_nodes.length - 1];
        var min_len = parseInt(before_node.getAttribute("min_len") || "0", 10);
        var max_len = parseInt(
            before_node.getAttribute("max_len") || "9999",
            10
        );
        var now_len = parseInt(before_node.getAttribute("now_len") || "0", 10);
        var orderable = parseInt(
            before_node.getAttribute("orderable") || "0",
            10
        );

        if (now_len < max_len) {
            deform.addSequenceItem(proto_node, before_node);
            deform.processSequenceButtons(
                oid_node,
                min_len,
                max_len,
                now_len + 1,
                orderable
            );
        }
        return false;
    },

    removeSequenceItem: function (clicked) {
        var item_node = clicked.closest(".deform-seq-item");
        var oid_node = item_node.closest(".deform-seq");
        var before_nodes = oid_node.querySelectorAll(".deform-insert-before");
        var before_node = before_nodes[before_nodes.length - 1];
        var min_len = parseInt(before_node.getAttribute("min_len") || "0", 10);
        var max_len = parseInt(
            before_node.getAttribute("max_len") || "9999",
            10
        );
        var now_len = parseInt(before_node.getAttribute("now_len") || "0", 10);
        var orderable = parseInt(
            before_node.getAttribute("orderable") || "0",
            10
        );
        if (now_len > min_len) {
            before_node.setAttribute("now_len", now_len - 1);
            item_node.remove();
            // We removed something from the DOM; trigger a change event.
            oid_node.dispatchEvent(new Event("change", { bubbles: true }));
            deform.processSequenceButtons(
                oid_node,
                min_len,
                max_len,
                now_len - 1,
                orderable
            );
        }
        return false;
    },

    /*
     * Show/hide the add, close and order buttons for the direct children of a
     * sequence, without touching nested sequences.
     */
    processSequenceButtons: function (
        oid_node,
        min_len,
        max_len,
        now_len,
        orderable
    ) {
        orderable = !!orderable; // convert to bool
        var has_multiple = now_len > 1;
        var show_closebutton = now_len > min_len;
        var show_addbutton = now_len < max_len;

        // Only operate on the sequence container(s) that belong directly to
        // this sequence, i.e. those whose nearest enclosing sequence container
        // is the sequence node itself (skip nested sub-sequences).
        var containers = Array.prototype.filter.call(
            oid_node.querySelectorAll(".deform-seq-container"),
            function (ul) {
                return deform._ownedBy(ul, oid_node);
            }
        );

        containers.forEach(function (ul) {
            var lis = Array.prototype.filter.call(
                ul.querySelectorAll(".deform-seq-item"),
                function (li) {
                    return deform._ownedBy(li, oid_node);
                }
            );
            lis.forEach(function (li) {
                deform._toggleOwned(
                    li,
                    ".deform-close-button",
                    oid_node,
                    show_closebutton
                );
                deform._toggleOwned(
                    li,
                    ".deform-order-button",
                    oid_node,
                    orderable && has_multiple
                );
            });
        });

        Array.prototype.filter
            .call(oid_node.querySelectorAll(".deform-seq-add"), function (btn) {
                return deform._ownedBy(btn, oid_node);
            })
            .forEach(function (btn) {
                deform._toggle(btn, show_addbutton);
            });
    },

    /*
     * True when the nearest ancestor of ``el`` that is a sequence
     * (``.deform-seq``) is exactly ``seq_node``. This is how we distinguish
     * elements belonging to this sequence from those in nested sequences.
     */
    _ownedBy: function (el, seq_node) {
        return el.parentElement
            ? el.parentElement.closest(".deform-seq") === seq_node
            : false;
    },

    _toggleOwned: function (root, selector, seq_node, show) {
        Array.prototype.filter
            .call(root.querySelectorAll(selector), function (el) {
                return el.closest(".deform-seq") === seq_node;
            })
            .forEach(function (el) {
                deform._toggle(el, show);
            });
    },

    _toggle: function (el, show) {
        el.style.display = show ? "" : "none";
    },

    /*
     * Apply an input mask using IMask, translating the legacy
     * jquery.maskedinput mask syntax so existing widget ``mask`` strings keep
     * working:
     *   9 -> 0 (digit)      a -> a (letter)     * -> * (alphanumeric)
     *   ? -> optional marker (everything after ? is optional)
     * The placeholder char controls IMask's ``lazy``/``placeholderChar``.
     */
    maskInput: function (el, mask, placeholder) {
        if (!el || typeof IMask === "undefined" || !mask) {
            return null;
        }
        // Register the legacy jquery.maskedinput placeholders as IMask
        // definitions so existing widget ``mask`` strings keep working:
        //   9 = digit, a = letter, * = alphanumeric.
        var definitions = {
            "9": /[0-9]/,
            a: /[A-Za-z]/,
            "*": /[A-Za-z0-9]/
        };
        // jquery.maskedinput showed placeholder characters (e.g.
        // ``0__-__-____``) only while a field is focused or holds input, and
        // left an empty field blank. Reproduce that by toggling IMask's
        // ``lazy`` flag on focus/blur.
        var opts = {
            mask: mask,
            definitions: definitions,
            lazy: true,
            placeholderChar:
                placeholder && placeholder.length === 1 ? placeholder : "_"
        };
        // A native ``autofocus`` on the field would immediately switch the
        // mask into eager mode (showing the full placeholder before any
        // input), which is confusing and interferes with programmatic typing.
        // Drop it; the field enters eager mode on genuine user focus.
        if (el.hasAttribute("autofocus")) {
            el.removeAttribute("autofocus");
        }
        var imask = IMask(el, opts);
        el.addEventListener("focus", function () {
            imask.updateOptions({ lazy: false });
        });
        el.addEventListener("blur", function () {
            // Keep placeholders visible only if the user entered something.
            imask.updateOptions({ lazy: imask.unmaskedValue === "" });
        });
        // Persist the raw (unmasked-with-placeholder) value on submit so the
        // server receives what the user typed, matching the old behavior.
        el._imask = imask;
        return imask;
    },

    /*
     * Apply a currency/number mask using IMask's Number mask, translating the
     * legacy jquery.maskMoney options object so existing widget ``options``
     * keep working.
     */
    maskMoney: function (el, options) {
        if (!el || typeof IMask === "undefined") {
            return null;
        }
        options = options || {};
        var imask = IMask(el, {
            mask: Number,
            scale: options.precision != null ? options.precision : 2,
            signed: !!options.allowNegative,
            thousandsSeparator:
                options.thousands != null ? options.thousands : ",",
            radix: options.decimal != null ? options.decimal : ".",
            mapToRadix: ["."],
            normalizeZeros: true,
            padFractionalZeros: false
        });
        el._imask = imask;
        return imask;
    },

    /*
     * Free-text input with autocomplete suggestions, backed by Tom Select
     * (replaces the old bootstrap typeahead). ``options`` may contain:
     *   local:     array of suggestion strings
     *   remote:    URL returning a JSON array of strings for ?term=<query>
     *   minLength: characters before searching
     *   limit:     max suggestions shown
     */
    autocomplete: function (oid, options, autofocus) {
        var el = document.getElementById(oid);
        if (!el || typeof TomSelect === "undefined") {
            return null;
        }
        options = options || {};
        var toOption = function (v) {
            return { value: v, text: v };
        };
        var config = {
            create: true, // allow arbitrary free-text values
            maxItems: 1, // single-value text field
            persist: false,
            selectOnTab: true,
            maxOptions: options.limit || 8,
            shouldLoad: function (query) {
                return query.length >= (options.minLength || 1);
            },
            render: {
                option_create: function (data, escape) {
                    return (
                        '<div class="create">' + escape(data.input) + "</div>"
                    );
                }
            }
        };

        if (options.local) {
            config.options = options.local.map(toOption);
        }

        if (options.remote) {
            config.load = function (query, callback) {
                var url =
                    options.remote +
                    (options.remote.indexOf("?") === -1 ? "?" : "&") +
                    "term=" +
                    encodeURIComponent(query);
                fetch(url, { headers: { Accept: "application/json" } })
                    .then(function (r) {
                        return r.json();
                    })
                    .then(function (data) {
                        callback((data || []).map(toOption));
                    })
                    .catch(function () {
                        callback();
                    });
            };
        }

        var ts = new TomSelect(el, config);
        // Preserve any initial value.
        if (el.value) {
            ts.addOption(toOption(el.value));
            ts.addItem(el.value, true);
        }
        // Do not auto-open the dropdown on load; its overlay would intercept
        // clicks on nearby controls (autofocus on selects is undesirable UX).
        ts.close();
        ts.control_input.blur();
        setTimeout(function () {
            ts.close();
        }, 0);
        el._tomselect = ts;
        return ts;
    },

    /*
     * Date / time picker backed by flatpickr (replaces pickadate + Modernizr).
     *
     * ``kind`` is "date" or "time". ``options`` may still carry the legacy
     * pickadate keys (``format``, ``formatSubmit``, ``selectMonths``,
     * ``selectYears``, ``interval``); they are translated to flatpickr config.
     *
     * The visible field shows a localized value while the submitted value is
     * kept in the input itself in a server-friendly ISO format (Y-m-d /
     * H:i:S), so no separate hidden "_submit" field is required.
     */
    datepicker: function (oid, options, kind) {
        var el = document.getElementById(oid);
        if (!el || typeof flatpickr === "undefined") {
            return null;
        }
        options = options || {};

        var config = {
            allowInput: true,
            // The input's value is always the machine format the server wants.
            enableTime: kind === "time" || kind === "datetime",
            noCalendar: kind === "time",
            dateFormat: kind === "time" ? "H:i" : "Y-m-d"
        };

        // Map pickadate time interval -> flatpickr minuteIncrement.
        if (options.interval) {
            config.minuteIncrement = options.interval;
        }
        // 12h vs 24h: pickadate "h:i A" implies 12h clock.
        if (options.format && /a/i.test(String(options.format))) {
            config.time_24hr = false;
        } else if (kind === "time") {
            config.time_24hr = true;
        }

        var fp = flatpickr(el, config);
        el._flatpickr = fp;
        return fp;
    },

    /*
     * Enhance a native ``<select>`` with Tom Select (replaces select2 and
     * selectize). ``options`` accepts a small normalized config:
     *   placeholder, allowClear (bool), create/tags (bool), multiple (bool)
     * plus any extra native Tom Select options (e.g. from selectize_options).
     */
    tomselect: function (oid, options) {
        var el = document.getElementById(oid);
        if (!el || typeof TomSelect === "undefined") {
            return null;
        }
        options = options || {};

        var config = {
            plugins: []
        };
        if (options.placeholder) {
            config.placeholder = options.placeholder;
        }
        if (options.create || options.tags) {
            config.create = true;
        }
        if (options.allowClear) {
            config.plugins.push("clear_button");
        }
        if (options.multiple || el.multiple) {
            config.plugins.push("remove_button");
        }

        // Carry through any additional native Tom Select options.
        Object.keys(options).forEach(function (k) {
            if (
                [
                    "placeholder",
                    "allowClear",
                    "create",
                    "tags",
                    "multiple"
                ].indexOf(k) === -1
            ) {
                config[k] = options[k];
            }
        });

        // The native ``autofocus`` attribute makes the browser focus the
        // <select> after load, which opens Tom Select's dropdown and leaves
        // its overlay covering nearby controls (intercepting clicks). Drop the
        // attribute before initializing; auto-opening a select dropdown on page
        // load is undesirable anyway.
        if (el.hasAttribute("autofocus")) {
            el.removeAttribute("autofocus");
        }

        var ts = new TomSelect(el, config);

        // Readonly -> lock the control (mirrors selectize .lock()).
        if (el.hasAttribute("readonly")) {
            ts.lock();
        }

        // Ensure the dropdown is not left open on initial load (e.g. from a
        // browser autofocus), where its overlay could intercept clicks.
        ts.close();
        ts.control_input.blur();
        setTimeout(function () {
            ts.close();
        }, 0);

        el._tomselect = ts;
        return ts;
    },

    randomString: function (length) {
        var chr =
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXTZabcdefghiklmnopqrstuvwxyz";
        chr = chr.split("");

        if (!length) {
            length = Math.floor(Math.random() * chr.length);
        }

        var str = "";
        for (var i = 0; i < length; i++) {
            str += chr[Math.floor(Math.random() * chr.length)];
        }
        return str;
    }
};
