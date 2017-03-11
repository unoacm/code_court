<template>
  <div v-if="problem">
    <h1 class="title is-1">{{ problem.name }}</h1>
    <div v-html="convertToMarkdown(problem.problem_statement)"></div>
    </br>

    <h3 class="subtitle is-3">Sample Input</h3>
    <pre><code>{{ problem.sample_input }}</code></pre>
    </br>

    <h3 class="subtitle is-3">Sample Output</h3>
    <pre><code>{{ problem.sample_output }}</code></pre>
    <br/>

    <h3 class="subtitle is-3">Code</h3>
    <label class="label" for="lang">Language:</label>
    <p class="control">
      <span class="select">
        <select id="lang" v-model="lang">
          <option v-for="lang in langs" :value="lang['name']">{{ lang['name'] }}</option>
        </select>
      </span>
    </p>
    <Editor v-model="sourceCode"
            id="main-editor"
            theme="solarized_light"
            :lang="lang"
            :height="500" />
    <br/>

    <div>
      <button v-on:click="submitCode(false)" class="button is-info">Test</button>
      <button v-on:click="submitCode(true)" class="button is-warning">Submit</button>
    </div>
    <br/>

    <h3 class="subtitle is-3">Runs</h3>
    <RunCollapse v-for="(run, i) in problem.runs.slice().reverse()"
                 :key="run.id"
                 :run="run"
                 :init-is-toggled="i == 0 ? true : false"/>

  </div>
</template>

<script>
import marked from 'marked'
import axios from 'axios'

import Editor from '@/components/Editor'
import RunCollapse from '@/components/RunCollapse'

export default {
  data () {
    return {
      sourceCode: '',
      lang: 'python'
    }
  },
  computed: {
    problem () {
      return this.$store.state.problems[this.$route.params.slug]
    },
    langs () {
      return this.$store.state.langs
    }
  },
  methods: {
    convertToMarkdown: function (s) {
      return marked(s)
    },
    submitCode: function (isSubmission) {
      axios.post('http://localhost:9191/api/submit-run', {
        lang: this.lang,
        problem_slug: this.problem.slug,
        source_code: this.sourceCode,
        is_submission: isSubmission
      }).then((response) => {
      }).catch(function (error) {
        console.log(error)
      })
    }
  },
  components: {
    Editor,
    RunCollapse
  }
}
</script>

<style scoped>
</style>
