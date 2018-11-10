<template>
  <div>
    <h2 class="title is-2">Clarifications Page</h2>
    <div class="content">
      <h3>Welcome to the Clarifications page!</h3>
      <p>Here you can:</p>
      <ul>
        <li>Submit Clarifications</li>
        <li>Read Clarifications</li>
      </ul>
      <p>Clarifications are another way for you to ask questions about a specific problem and get an answer from a judge. NOTE: It may take up for a minute for the clarification list to load - Sorry!</p>

      <hr />
      <h3 class="title">Submit a Clarification</h3>
      <form @submit.prevent="submit()">
        <label class="label" for="problem">Problem</label>
          <p class="control">
            <span class="select">
              <select id="problem" v-model="problem">
                <option v-for="(problem, name) in problems" :value="problem['name']">{{ problem['name'] }}</option>
              </select>
            </span>
          </p>

        <label class="label" for="subject">Subject</label>
          <p class="control">
            <input v-model="subject" type="text" class="input" name="subject" required />
          </p>

        <label class="label" for="contents">Contents</label>
          <p class="control">
            <input v-model="contents" type="text" class="input" name="contents" required />
          </p>

        <input type="submit" class="button is-primary" value="submit" />
      </form>

      <hr />
      <h3 class="title">Clarifications list</h3>
      <div v-for="clar in clars">
        <div v-if="clar.is_public">
          <h4>Question: {{ clar.problem }} - {{ clar.subject }}</h4>
          <p>{{ clar.contents }}</p>
          <h5>Judge's Response: {{ clar.answer }}</h5>
          <br />
        </div>
        <div v-else-if="clar.initiating_user == user.username">
          <h4>Question: {{ clar.problem }} - {{ clar.subject }}</h4>
          <p>{{ clar.contents }}</p>
          <h5>Judge's Response: {{ clar.answer }}</h5>
          <br />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  data () {
    return {
      problem: 'FizzBuzz',
      subject: 'example',
      contents: 'halp',
      is_public: false
    }
  },
  computed: {
    clars () {
      return this.$store.state.clars
    },
    problems () {
      return this.$store.state.problems
    },
    user () {
      return this.$store.state.user
    }
  },
  methods: {
    submit: function () {
      axios.post('/api/submit_clarification', {
        problem: this.problem,
        subject: this.subject,
        contents: this.contents,
        is_public: false
      }).then((response) => {
        this.subject = ''
        this.contents = ''
      }).catch(function (error) {
        console.log(error)
      })
    }
  }
}
</script>

<style scoped>
</style>

