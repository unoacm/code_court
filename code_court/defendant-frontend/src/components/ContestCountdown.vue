<template>
  <span :v-if="!isContestOver()">
      {{ contestEnd }}
  </span>
</template>

<script>
import {iso8601ToMoment, isContestOver} from '@/util'

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
    isContestOver () {
      console.log(isContestOver(this.contest))
      return isContestOver(this.contest)
    }
  },
  computed: {
    contest () {
      return this.$store.state.contest
    }
  },
  mounted: function () {
    this.contestEnd = iso8601ToMoment(this.contest.end_time).fromNow()
    setInterval(function () {
      this.contestEnd = iso8601ToMoment(this.contest.end_time).fromNow()
    }.bind(this), 30000)
  }
}
</script>

<style scoped>
</style>
