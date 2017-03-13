<template>
  <div>
    <div :style="{ height: height + 'px' }" :id="id"></div>
  </div>
</template>

<script>
import brace from 'brace'

import 'brace/mode/python'
import 'brace/mode/ruby'

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
    lang: String,
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
  computed: {
  },
  methods: {
    getEditor: function () {
      var editor = brace.edit(this.id)
      editor.$blockScrolling = Infinity

      editor.getSession().setMode('ace/mode/' + this.lang)
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
  watch: {
    lang: function () {
      this.editor.getSession().setMode('ace/mode/' + this.lang)
    },
    value: function () {
      var pos = this.editor.session.selection.toJSON()
      this.editor.setValue(this.value)
      this.editor.clearSelection()
      this.editor.session.selection.fromJSON(pos)
    }
  },
  mounted: function () {
    this.editor = this.getEditor()
  }
}
</script>

<style scoped>
</style>
