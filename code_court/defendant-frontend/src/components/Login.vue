<template>
  <div class="row">
    <div class="col-md-offset-4 col-md-4">
      <h3>Please login</h3>
      <form @submit.prevent="login()">
        <input v-model="email" type="email" class="form-control input-sm" placeholder="email" name="email" />
        </br>

        <input v-model="password" type="password" class="form-control input-sm" placeholder="password" name="password" />
        </br>

        <input type="submit" class="btn btn-primary btn-md" value="login" />
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
