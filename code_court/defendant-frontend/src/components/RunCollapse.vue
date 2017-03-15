<template>
  <div>
    <article class="message" :class="run_status">
      <div class="message-header" :class="{ hasToggle: !disableToggle }" v-on:click="isToggled = !isToggled">
        <p>Run #{{ run.id }}</p>
        <a class="card-header-icon">
          <span class="tag">{{ run.language }}</span>
          <span v-if="run.is_passed == null" class="tag is-info">
            Judging <pulse-loader :loading="true" size="4px" color="#fff" />
          </span>

          <span v-if="run.is_submission" class="tag is-warning">Submission</span>
          <span v-if="!run.is_submission" class="tag">Test Run</span>
          <span class="icon" v-if="!disableToggle">
            <i class="fa fa-angle-down"></i>
          </span>
        </a>
      </div>
      <div class="message-body" v-if="disableToggle || isToggled">
        <h5 class="subtitle is-5">Code</h5>
        <Editor v-model="run.source_code"
                :init-text="run.source_code"
                :id="'run-editor-' + run.id"
                :read-only="true"
                :lang="run.language"
                :minLines="5"
                :maxLines="30" />

        <div v-if="run.run_input != null">
          <h5 class="subtitle is-5">Input</h5>
          <pre class="input-text"><code>{{ run.run_input }}</code></pre>
        </div>

        <div v-if="run.run_output != null">
          <h5 class="subtitle is-5">Output</h5>
          <pre class="output-text"><code>{{ truncate(run.run_output, 500) }}</code></pre>
        </div>
      </div>
    </article>
    <br/>
  </div>
</template>

<script>
import Editor from '@/components/Editor'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

export default {
  data () {
    return {
      isToggled: false
    }
  },
  props: ['run', 'disableToggle'],
  computed: {
    istoggled () {
      return this.isToggled
    },
    run_status () {
      if (this.run.is_passed == null) {
        return ''
      } else if (this.run.is_passed) {
        return 'is-success'
      } else if (!this.run.is_passed) {
        return 'is-danger'
      }
    }
  },
  created: function () {
    this.isToggled = this.initIsToggled
  },
  methods: {
    truncate: function (str, maxLines) {
      let lines = str.split('\n')
      if (lines.length > maxLines) {
        return lines.slice(0, maxLines).join('\n') + '\n...'
      } else {
        return str
      }
    }
  },
  components: {
    Editor,
    PulseLoader
  }
}
</script>

<style scoped>
.slide-fade-enter-active {
  transition: all .3s ease;
}
.slide-fade-enter, .slide-fade-leave-to {
  transform: translateX(10px);
  opacity: 0;
}

.message-header.hasToggle {
  cursor: pointer;
}

.message-header a {
  text-decoration: none;
}

.message-header a .tag {
  margin-right:3px;
}

.input-text {
  max-height:500px;
  overflow: auto;
}

.output-text {
  max-height:500px;
  overflow: auto;
}
</style>
