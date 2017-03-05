<template>
  <div v-if="problem">
    <h1>{{ problem.name }}</h1>
    <div v-html="convertToMarkdown(problem.problem_statement)"></div>

    <h2>Sample Input</h2>
    <pre>{{ problem.sample_input }}</pre>

    <h2>Sample Output</h2>
    <pre>{{ problem.sample_output }}</pre>

    <h2>Code</h2>
    <Editor v-model="source_code"></Editor>

    <br/>
    <button v-on:click="submitCode(false)" class="btn btn-primary">Run</button>
    <button v-on:click="submitCode(true)" class="btn btn-primary">Submit</button>

    <br/>

    <h2>Runs</h2>
    <Runs :runs="problem.runs"></Runs>

  </div>
</template>

<script>
import marked from 'marked'
import axios from 'axios'

import Editor from '@/components/Editor'
import Runs from '@/components/Runs'

export default {
  data () {
    return {
      source_code: ''
    }
  },
  computed: {
    problem () {
      return this.$store.state.problems[this.$route.params.slug]
    }
  },
  methods: {
    convertToMarkdown: function (s) {
      return marked(s)
    },
    submitCode: function (isSubmission) {
      console.log(this.source_code)
      axios.post('http://localhost:9191/api/submit-run', {
        lang: 'python',
        problem_slug: this.problem.slug,
        source_code: this.source_code,
        is_submission: isSubmission
      }).then((response) => {
      }).catch(function (error) {
        console.log(error)
      })
    }
  },
  components: {
    Editor,
    Runs
  }
}
</script>

<style scoped>
</style>
