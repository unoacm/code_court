<template>
  <transition name="fade">
  <div class="row">
    <div class="col-md-offset-4 col-md-4">
      <h3 class="title">login</h3>
      <form @submit.prevent="login()">
        <p class="control">
          <input v-model="loginEmail" type="email" class="input" placeholder="email" name="email" required />
        </p>

        <p class="control">
          <input v-model="loginPassword" type="password" class="input" placeholder="password" name="password" required />
        </p>

        <input type="submit" class="button is-primary" value="login" />
      </form>

      </br >
      </br >

      <h3 class="title">signup</h3>
      <form @submit.prevent="signup()">
        <p class="control">
          <input v-model="signupEmail" type="email" class="input" placeholder="email" name="email" required />
        </p>

        <p class="control">
          <input v-model="signupUsername" type="text" class="input" placeholder="username" name="username" required />
        </p>

        <p class="control">
          <input v-model="signupName" type="text" class="input" placeholder="name" name="name" required />
        </p>

        <p class="control">
          <input v-model="signupPassword" type="password" class="input" placeholder="password" name="password" required />
        </p>

        <p class="control">
          <input v-model="signupPassword2" type="password" class="input" placeholder="re-enter password" name="password" required />
        </p>

        <p class="control">
          <input v-model="signupContest" type="text" class="input" placeholder="contest" name="contest" required />
        </p>

        <input type="submit" class="button is-primary" value="signup" />
      </form>
      </div>
    </div>
  </div>
  </transition>
</template>

<script>
export default {
  data () {
    return {
      loginEmail: '',
      loginPassword: '',
      signupEmail: '',
      signupUsername: '',
      signupName: '',
      signupPassword: '',
      signupPassword2: '',
      signupContest: ''
    }
  },
  computed: {
    problem () {
      return this.$store.state.problems[this.$route.params.slug]
    }
  },
  methods: {
    login: function () {
      this.$store.dispatch('LOGIN', {email: this.loginEmail, password: this.loginPassword})
    },
    signup: function () {
      this.$store.dispatch('SIGNUP', {
        email: this.signupEmail,
        username: this.signupUsername,
        name: this.signupName,
        password: this.signupPassword,
        password2: this.signupPassword2,
        contest_name: this.signupContest
      })
    }
  }
}
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
</style>
