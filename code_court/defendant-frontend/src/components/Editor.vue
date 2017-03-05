<template>
  <div style="height:500px" id="braceEditor"></div>
</template>

<script>
import brace from 'brace'

import 'brace/mode/python'
import 'brace/theme/solarized_light'

export default {
  data () {
    return {
      editor: null,
      modeList: null,
      themeList: null
    }
  },
  props: ['value'],
  methods: {
    getEditor: function () {
      var editor = brace.edit('braceEditor')

      editor.getSession().setMode('ace/mode/python')
      editor.setTheme('ace/theme/solarized_light')

      editor.getSession().setUseWorker(false)
      editor.setAutoScrollEditorIntoView(true)

      editor.getSession().on('change', this.emitCode)

      return editor
    },
    emitCode: function () {
      this.$emit('input', this.editor.getValue())
    }
  },
  mounted: function () {
    this.editor = this.getEditor()
  }
}
</script>

<style scoped>
</style>
