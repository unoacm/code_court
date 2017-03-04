<template>
  <div v-if="problem">
    <h1>{{ problem.name }}</h1>
    <div v-html="convertToMarkdown(problem.problem_statement)"></div>

    <h2>Sample Input</h2>
    <pre>{{ problem.sample_input }}</pre>

    <h2>Sample Output</h2>
    <pre>{{ problem.sample_output }}</pre>

    <h2>Code</h2>
    <textarea v-model="source_code" class="form-control" name="code"></textarea>
    <br/>
    <button v-on:click="submitCode" class="btn btn-primary">Run</button>
  </div>
</template>

<script>
import marked from 'marked'
import axios from 'axios'

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
    submitCode: function () {
      console.log(this.source_code)
      axios.post('http://localhost:9191/api/submit-run', {
        lang: 'python',
        problem_slug: this.problem.slug,
        source_code: this.source_code
      }).then((response) => {
      }).catch(function (error) {
        console.log(error)
      })
    }
  }
}
</script>

<style scoped>
</style>
