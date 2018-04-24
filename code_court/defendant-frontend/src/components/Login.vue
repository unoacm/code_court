<template>
  <transition name="fade">
  <div class="row">
    <div class="col-md-offset-4 col-md-4">
      <h3 class="title">login</h3>
      <form @submit.prevent="login()">
        <p class="control">
          <input v-model="loginUsername" type="text" class="input" placeholder="username" name="username" />
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

        <p v-for="extra_signup_field in conf.extra_signup_fields" class="control">
          <input type="text" :class="['input', 'extra-signup-field-' + extra_signup_field]" :placeholder="extra_signup_field" :name="extra_signup_field" required />
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
      loginUsername: '',
      loginPassword: '',
      signupUsername: '',
      signupName: '',
      signupPassword: '',
      signupPassword2: '',
      signupContest: ''
    }
  },
  computed: {
    conf () {
      return this.$store.state.conf
    }
  },
  mounted: function () {
    for (const extraSignupField of this.conf.extra_signup_fields) {
      console.log(this.$el.querySelector(`.extra-signup-field-${extraSignupField}`).value)
    }
  },
  methods: {
    login: function () {
      this.$store.dispatch('LOGIN', {username: this.loginUsername, password: this.loginPassword})
    },
    signup: function () {
      let fields = {
        username: this.signupUsername,
        name: this.signupName,
        password: this.signupPassword,
        password2: this.signupPassword2,
        contest_name: this.signupContest
      }

      for (const extraSignupField of this.conf.extra_signup_fields) {
        const selector = `.extra-signup-field-${extraSignupField}`
        fields[extraSignupField] = this.$el.querySelector(selector).value
      }

      this.$store.dispatch('SIGNUP', fields)
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
