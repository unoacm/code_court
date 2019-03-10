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

const MIN_POLL_RATE = 5000

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
    },
    conf () {
      return this.$store.state.conf
    }
  },
  mounted: function () {
    this.$store.dispatch('LOAD_CONF')
    this.$store.dispatch('LOAD_LANGS')

    if (this.$store.getters.isLoggedIn) {
      this.$store.dispatch('LOAD_USER')
      this.$store.dispatch('LOAD_PROBLEMS', this.user.id)
      this.$store.dispatch('LOAD_CONTEST')
    }

    setInterval(function () {
      if (this.contest.id) {
        this.$store.dispatch('LOAD_SCORES', this.contest.id)
      }
    }.bind(this), Math.max(MIN_POLL_RATE, this.conf.score_refresh_interval_millseconds))

    setInterval(function () {
      if (this.$store.getters.isLoggedIn) {
        this.$store.dispatch('LOAD_PROBLEMS', this.user.id)
      }
    }.bind(this), Math.max(MIN_POLL_RATE, this.conf.run_refresh_interval_millseconds))

    setInterval(function () {
      if (this.$store.getters.isLoggedIn) {
        this.$store.dispatch('LOAD_CONTEST')
        this.$store.dispatch('LOAD_LANGS')
        this.$store.dispatch('LOAD_USER')
        this.$store.dispatch('LOAD_CONF', this.user.id)
      }
    }.bind(this), Math.max(MIN_POLL_RATE, this.conf.misc_refresh_interval_millseconds))
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
