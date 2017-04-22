<template>
  <div :id="problem.slug" v-if="problem">
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
          <option v-for="(lang, name) in langs" :value="lang['name']">{{ lang['name'] }}</option>
        </select>
      </span>
    </p>
    <Editor v-model="sourceCode"
            :id="'main-editor-' + problem.slug"
            theme="solarized_light"
            :lang="lang"
            ref="editor" />
    <br/>

    <div>
      <button v-on:click="submitCode(true)" class="button is-warning">Submit</button>
    </div>

    <br/>

    <h3 class="subtitle is-3">Test Input</h3>
    <textarea class="textarea" v-model="testInput"></textarea>

    <br/>

    <div>
      <button v-on:click="submitCode(false)" class="button is-info">Test</button>
    </div>

    <br/>

    <h3 class="subtitle is-3">Runs</h3>
    <RunCollapse v-for="(run, i) in problem.runs.slice().reverse()"
                 :key="run.id"
                 :run="run"
                 :disable-toggle="i == 0 ? true : false"/>

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
      lang: 'python',
      testInputBySlug: {},
      testInput: ''
    }
  },
  computed: {
    problem () {
      return this.$store.state.problems[this.$route.params.slug]
    },
    problems () {
      return this.$store.state.problems
    },
    langs () {
      return this.$store.state.langs
    },
    sourceCode: {
      get () {
        if (this.problem) {
          return this.$store.getters.getSourceCode(this.problem.slug, this.langs[this.lang])
        }
      },
      set (value) {
        if (this.problem) {
          this.$store.commit('UPDATE_SOURCE_CODE', {
            problemSlug: this.problem.slug,
            lang: this.lang,
            sourceCode: value
          })
        }
      }
    }
  },
  watch: {
    testInput: function () {
      this.testInputBySlug[this.problem.slug] = this.testInput
    },
    problem: function () {
      if (this.problem) {
        this.testInput = this.testInputBySlug[this.problem.slug]
      }
    }
  },
  methods: {
    convertToMarkdown: function (s) {
      return marked(s)
    },
    submitCode: function (isSubmission) {
      axios.post('/api/submit-run', {
        lang: this.lang,
        problem_slug: this.problem.slug,
        source_code: this.$refs.editor.editor.getValue(),
        is_submission: isSubmission,
        user_test_input: isSubmission ? null : this.testInput
      }).then((response) => {
      }).catch(function (error) {
        console.log(error)
      })

      // add a fake entry to runs
      var runId = 0
      if (this.problem.runs.length === 0) {
        runId = 1
      } else {
        runId = this.problem.runs[this.problem.runs.length - 1].id + 1
      }
      this.$store.commit('ADD_FAKE_RUN', {
        id: runId,
        problemSlug: this.problem.slug,
        language: this.lang,
        source_code: this.sourceCode,
        run_input: isSubmission ? null : this.testInput,
        is_submission: isSubmission,
        is_passed: null,
        run_output: null,
        state: 'Judging'
      })
    }
  },
  mounted: function () {
    if (this.problem) {
      for (var problemSlug in this.problems) {
        this.testInputBySlug[problemSlug] = this.problems[problemSlug].sample_input
      }
      this.testInput = this.problem.sample_input
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
