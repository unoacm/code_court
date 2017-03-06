<template>
  <div v-bind:style="{ height: height + 'px' }" v-bind:id="id"></div>
</template>

<script>
import brace from 'brace'

import 'brace/mode/python'
import 'brace/theme/chrome'
import 'brace/theme/solarized_light'

export default {
  data () {
    return {
      editor: null
    }
  },
  props: {
    value: String,
    id: String,
    height: Number,
    readOnly: {
      type: Boolean,
      default: false
    },
    theme: {
      type: String,
      default: 'chrome'
    },
    initText: {
      type: String,
      default: null
    }
  },
  methods: {
    getEditor: function () {
      var editor = brace.edit(this.id)

      editor.getSession().setMode('ace/mode/python')
      editor.setTheme('ace/theme/' + this.theme)

      editor.getSession().setUseWorker(false)

      if (this.readOnly) {
        editor.setReadOnly(true)
        editor.renderer.$cursorLayer.element.style.display = 'none'
        editor.setOptions({ highlightActiveLine: false, highlightGutterLine: false })
        editor.$highlightTagPending = false
        editor.$highlightPending = false
      }

      if (this.initText) {
        editor.setValue(this.initText)
        editor.clearSelection()
      }

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
