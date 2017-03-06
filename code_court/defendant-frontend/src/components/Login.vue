<template>
  <div class="row">
    <div class="col-md-offset-4 col-md-4">
      <h3>Please login</h3>
      <form @submit.prevent="login()">
        <p class="control">
          <input v-model="email" type="email" class="input" placeholder="email" name="email" />
        </p>

        <p class="control">
          <input v-model="password" type="password" class="input" placeholder="password" name="password" />
        </p>

        <input type="submit" class="button is-primary" value="login" />
      </form>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      email: '',
      password: ''
    }
  },
  computed: {
    problem () {
      return this.$store.state.problems[this.$route.params.slug]
    }
  },
  methods: {
    login: function () {
      this.$store.dispatch('LOGIN', {email: this.email, password: this.password})
      this.$router.push({ name: 'scoreboard' })
    }
  }
}
</script>

<style scoped>
</style>
