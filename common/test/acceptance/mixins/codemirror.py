class CodeMirrorMixin(object):
    """Adds convenient methods to work with CodeMirror"""
    def type_in_codemirror(self, index, text, find_prefix="$"):
        script = """
        var cm = {find_prefix}('div.CodeMirror:eq({index})').get(0).CodeMirror;
        CodeMirror.signal(cm, "focus", cm);
        cm.setValue(arguments[0]);
        CodeMirror.signal(cm, "blur", cm);""".format(index=index, find_prefix=find_prefix)
        self.browser.execute_script(script, str(text))
        self.wait_for_ajax()

    def get_codemirror_value(self, index=0, find_prefix="$"):
        return self.browser.execute_script(
            """
            return {find_prefix}('div.CodeMirror:eq({index})').get(0).CodeMirror.getValue();
            """.format(index=index, find_prefix=find_prefix)
        )
