<template>
  <div>
    <h1 class="title is-1">Info</h1>
    <h2 class="title is-2">Contest Info</h2>
    <pre>{{ contest }}</pre>
    <pre>{{ iso8601ToMoment(contest.start_time) }}</pre>
  </div>
</template>

<script>
import moment from 'moment'
import 'moment-timezone'
import tzdata from '!json-loader!moment-timezone/data/packed/latest.json'

moment.tz.load(tzdata)

export default {
  data () {
    return {
    }
  },
  methods: {
    iso8601ToMoment (is8601Str) {
      return moment.tz(is8601Str, 'UTC').local()
    }
  },
  computed: {
    contest () {
      return this.$store.state.contest
    }
  }
}
</script>

<style scoped>
</style>
