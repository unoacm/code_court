<template>
  <span>{{ contestEnd }}</span>
</template>

<script>
import moment from 'moment'
import 'moment-timezone'
import tzdata from '!json-loader!moment-timezone/data/packed/latest.json'

moment.tz.load(tzdata)

export default {
  data () {
    return {
      contestEnd: null
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
  },
  mounted: function () {
    this.contestEnd = this.iso8601ToMoment(this.contest.end_time).fromNow()
    setInterval(function () {
      this.contestEnd = this.iso8601ToMoment(this.contest.end_time).fromNow()
    }.bind(this), 30000)
  }
}
</script>

<style scoped>
</style>
