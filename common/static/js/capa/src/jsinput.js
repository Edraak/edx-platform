/**
 * @fileoverview Initialize js inputs on current page.
 * @requires  easyXDM, underscore
 *
 * N.B.: No library assumptions about the iframe can be made (including,
 * most relevantly, jquery). Keep in mind what happens in which context
 * when modifying this file.
 */
(function (jsinput, undefined) {

    var USE_RPC = true;

    var dlog = {
        msg: "[ JSinput ] %c",
        green: function(st) { console.log(this.msg + st,'color: #bada55'); },
        red: function(st) { console.log(this.msg + st,'color: #b72467'); },
        blue: function(st) { console.log(this.msg + st, 'color: #1aa1e0'); },
        log: function(st) { console.log(this.msg + st, 'color: black'); },
    }

    // When all the problems are first loaded, we want to make sure the
    // constructor only runs once for each iframe; but we also want to make
    // sure that if part of the page is reloaded (e.g., a problem is
    // submitted), the constructor is called again.
    if (!jsinput) {
        jsinput = {
            runs : 1,
            arr : [],
            exists : function(id) {
                jsinput.arr.filter(function(e, i, a) {
                    return e.id = id;
                });
            }
        };
    }

    jsinput.runs++;


    /**
     * Take a string and find the nested object that corresponds to it. E.g.:
     *     deepKey(obj, "an.example") -> obj["an"]["example"]
     * @param {string} obj The base object
     * @param {string} path Any futher methods/attributes
     * @return The evaluated object
     */
    var _deepKey = function(obj, path){
        for (var i = 0, p=path.split('.'), len = p.length; i < len; i++){
            obj = obj[p[i]];
        }
        return obj;
    };



    /**
     * Retuns a new rpc and creates and iframe.
     * @param {string} cont The html element within which to put the iframe
     * @param {string} rem_src Url of the remote html file
     * @param {string|int} id The id number for the jsinput section
     * @return {easyXDM.Rpc} The rpc instance
     * @constructor
     */
    var rpc = function (cont, rem_src, id) {
        dlog.blue("Creating rpc...");
        dlog.log("Source:  " + rem_src);
        dlog.log("Container:  " + cont);
        dlog.log("Id:  " + id);
        return new easyXDM.Rpc({
            remote: rem_src
        },
        {
            container: cont,
            local: {
                // This function gets called by the provider.
                returnVal: function(r) {
                    result = r;
                }
            },
            remote: {
                callAny: {}
            }, 
            props: {
                id: id.toString(),
                width: "500px",
                height: "600px",
                seamless: "seamless",
                sandbox: "allow-scripts allow-popups allow-same-origin allow-forms allow-pointer-lock" 
            }
        });
    };

    
     
    /**
     * A synchronous wrapper around our RPC. 
     * @param {easyXDM.Rpc} anRPC The rpc to use
     * @param {string} fnName The function to call, in method (dot) syntax,
     *     not brackets (i.e. ("a.b.c", not "a['b'].c")
     * @return The return value of fnName
     */
    var rpcWrapper = function(anRPC, fnName) {
        var args = Array.prototype.slice.call(arguments, 0);
        var result = anRPC.callAny.apply(this,  args);
        dlog.red("Result: " + result);
        return result;
    };


    /**
     * A constructor for a jsinput instance.
     * @param {Object} spec An object with 'id' and 'elem' attributes.
     * @param {string} src The html file url
     * @return {Object} A jsinput object
     * @constructor
     */
    function jsinputConstructor(spec, src) {
        var that = {};


        var sect = $(spec.elem).parent().find('section[class="jsinput"]');
        var sectAttr = function (e) { return $(sect).attr(e); };
        var parent = $(spec.elem).parent();
        var inputField = parent.find('input[id^="input_"]');
        var gradeFn = sectAttr("data");  // The grade function name
        var stateGetter = sectAttr("data-getstate");
        var stateSetter = sectAttr("data-setstate");
        var storedState = sectAttr("data-stored");  
        var getUrl = sectAttr("data-src");  // Html file src url
        
        /**
         * funEval takes a string (and, optionally, more arguments) and evaluates 
         * the function with that name in the iframe, passing it the optional
         * arguments.
         * @param {string} The function name
         * @param {...*=} Optional variable arguments of any type to be passed. 
         * @return {*}
         * @expose
         */
        if (USE_RPC) {
            var container = parent.find('div[id^="container_"]');
            that.rpc = rpc(container.get(), getUrl, spec.id);
            that.funEval = _.partial(rpcWrapper, that.rpc);
        } else {
            var thisIFrame = $(spec.elem).
                            find('iframe[name^="iframe_"]').
                            get(0);
            var cWindow = thisIFrame.contentWindow;
            that.funEval = function(fnName){
                var args = Array.prototype.slice.call(arguments, 1);
                return _deepKey(cWindow, fnName).apply(this, args);
            };
        }
        // FOR DEBUGGING ONLY
        window.rpcW = that.funEval;

        /**
         * Put the return value of gradeFn in the hidden inputField.
         * @return {void}
         * @expose
         */
        var update = function () {
            var ans;

            ans = that.funEval(gradeFn);
            // setstate presumes getstate, so don't getstate unless setstate is
            // defined.
            if (stateGetter && stateSetter) {
                var state, store;
                state = unescape(that.funEval(stateGetter));
                store = {
                    answer: ans,
                    state:  state
                };
                inputField.val(JSON.stringify(store));
            } else {
                inputField.val(ans);
            }
            return;
        };
        that.update = update;

        jsinput.arr.push(that);

        /** 
         * Put the update function as the value of the inputField's "waitfor"
         * attribute so that it is called when the check button is clicked.
         * @return {void}
         * @private
         */
        function bindCheck() {
            inputField.data('waitfor', that.update);
            return;
        }
        bindCheck();


        // Check whether application takes in state and there is a saved
        // state to give it. If stateSetter is specified but calling it
        // fails, wait and try again, since the iframe might still be
        // loading.
        if (stateSetter && storedState) {
            var sval, jsonVal;

            try {
              jsonVal = JSON.parse(storedState);
            } catch (err) {
              jsonVal = storedState;
            }

            if (typeof(jsonVal) === "object") {
                sval = jsonVal["state"];
            } else {
                sval = jsonVal;
            }


            /** 
             * Try calling setstate every 200ms while it throws an exception,
             * up to five times; give up after that.
             * (Functions in the iframe may not be ready when we first try
             * calling it, but might just need more time. Give the functions
             * more time.)
             * @param {int} n Number of times called so far
             * @return {void}
             */
            function whileloop(n) {
                if (n < 5){
                    try {
                        that.funEval(stateSetter, sval);
                    } catch (err) {
                        setTimeout(whileloop(n+1), 200);
                    }
                }
                else {
                    console.debug("Error: could not set state");
                }
                return;
            }
            whileloop(0);

        }

        return that;
    }

    /**
     * Walk through the DOM creating a jsinput for each appropriate section
     * @return {void}
     */
    function walkDOM() {
        var newid;

        // Find all jsinput elements, and create a jsinput object for each one
        var all = $(document).find('section[class="jsinput"]');

        all.each(function(index, value) {
            // Get just the mako variable 'id' from the id attribute
            newid = $(value).attr("id").replace(/^inputtype_/, "");


            if (!jsinput.exists(newid)){
                var newJsElem = jsinputConstructor({
                    id: newid,
                    elem: value,
                });
            }
        });

        return ;
    }

    // This is ugly, but without a timeout pages with multiple/heavy jsinputs
    // don't load properly.
    if ($.isReady) {
        setTimeout(walkDOM, 300);
    } else {
        $(document).ready(setTimeout(walkDOM, 300));
    }

})(window.jsinput = window.jsinput || false);
