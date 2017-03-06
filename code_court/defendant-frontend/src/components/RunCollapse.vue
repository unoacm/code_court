<template>
  <div>
    <article class="message" v-bind:class="run_status">
      <div class="message-header" v-on:click="isToggled = !isToggled">
        <p>Run #{{ run.id }}</p>
        <a  class="card-header-icon">
          <span v-if="run.is_passed == null" class="tag is-info">Judging</span>
          <span v-if="run.is_submission" class="tag is-warning">Submission</span>
          <span v-if="!run.is_submission" class="tag">Test Run</span>
          <span class="icon">
            <i class="fa fa-angle-down"></i>
          </span>
        </a>
      </div>
      <div class="message-body" v-if="isToggled">
        <h5 class="subtitle is-5">Code</h5>
        <Editor v-model="run.source_code"
                :init-text="run.source_code"
                :id="'run-editor-' + run.id"
                :read-only="true"
                :height="100"/>

        <div v-if="run.run_input != null">
          <h5 class="subtitle is-5">Input</h5>
          <pre><code>{{ run.run_input }}</code></pre>
        </div>

        <div v-if="run.run_output != null">
          <h5 class="subtitle is-5">Output</h5>
          <pre><code>{{ run.run_output }}</code></pre>
        </div>
      </div>
    </article>
    <br/>
  </div>
</template>

<script>
import Editor from '@/components/Editor'

export default {
  data () {
    return {
      isToggled: false
    }
  },
  props: ['run', 'initIsToggled'],
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
  components: {
    Editor
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

.message-header {
  cursor: pointer;
}

.message-header a {
  text-decoration: none;
}

.message-header a .tag {
  margin-right:3px;
}
</style>
