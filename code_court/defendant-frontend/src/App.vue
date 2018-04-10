<template>
  <div id="app">
    <section class="hero is-primary">
      <div class="hero-body">
        <div v-if="contest && user" class="container has-text-centered">
          <h1 class="title">
            {{ contest.name }}
          </h1>
          <div>
            <contest-countdown />
          </div>
        </div>
      </div>
    </section>
    <br/>
    <nav-disp></nav-disp>
  </div>
</template>

<script>
import Nav from '@/components/Nav'
import ContestCountdown from '@/components/ContestCountdown'

const RUN_REFRESH_INTERVAL = 5000
const SCORE_REFRESH_INTERVAL = 30000
const MISC_REFRESH_INTERVAL = 120000

export default {
  name: 'app',
  created: function () {
  },
  computed: {
    contest () {
      return this.$store.state.contest
    },
    user () {
      return this.$store.state.user
    }
  },
  mounted: function () {
    this.$store.dispatch('LOAD_USER')
    this.$store.dispatch('LOAD_LANGS')

    if (this.$store.getters.isLoggedIn) {
      this.$store.dispatch('LOAD_PROBLEMS', this.user.id)
      this.$store.dispatch('LOAD_CONTEST')
    }

    setInterval(function () {
      if (this.contest.id) {
        this.$store.dispatch('LOAD_SCORES', this.contest.id)
      }
    }.bind(this), SCORE_REFRESH_INTERVAL)

    setInterval(function () {
      if (this.$store.getters.isLoggedIn) {
        this.$store.dispatch('LOAD_PROBLEMS', this.user.id)
      }
    }.bind(this), RUN_REFRESH_INTERVAL)

    setInterval(function () {
      if (this.$store.getters.isLoggedIn) {
        this.$store.dispatch('LOAD_CONTEST')
        this.$store.dispatch('LOAD_LANGS')
        this.$store.dispatch('LOAD_USER')
      }
    }.bind(this), MISC_REFRESH_INTERVAL)
  },
  components: {
    'nav-disp': Nav,
    ContestCountdown
  }
}
</script>

<style>
.hero.is-primary {
  background-color: #046380;
}

@import "../node_modules/bulma/css/bulma.css"
</style>
