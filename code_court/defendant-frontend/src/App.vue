<template>
  <div id="app">
    <section class="hero is-primary">
      <div class="hero-body">
        <div class="container has-text-centered">
          <h1 class="title">
            code_court
          </h1>
        </div>
      </div>
    </section>
    <br/>
    <nav-disp></nav-disp>
  </div>
</template>

<script>
import Nav from '@/components/Nav'

export default {
  name: 'app',
  created: function () {
  },
  mounted: function () {
    if (this.$store.getters.isLoggedIn) {
      this.$store.dispatch('LOAD_PROBLEMS')
    }

    setInterval(function () {
      if (this.$store.getters.isLoggedIn) {
        this.$store.dispatch('LOAD_PROBLEMS')
      }
    }.bind(this), 10000)

    this.$store.dispatch('LOAD_USER')
    this.$store.dispatch('LOAD_LANGS')
  },
  components: {
    'nav-disp': Nav
  }
}
</script>

<style>
.hero.is-primary {
  background-color: #046380;
}

@import "../node_modules/bulma/css/bulma.css"
</style>
