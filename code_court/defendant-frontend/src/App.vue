<template>
  <div id="app">
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
    this.$store.dispatch('LOAD_PROBLEMS')
    this.$store.dispatch('LOAD_USER')
  },
  components: {
    'nav-disp': Nav
  }
}
</script>

<style>
@import "../node_modules/bulma/css/bulma.css"
</style>
