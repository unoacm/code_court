<template>
  <span :v-if="!isContestOver()">
    <span :title="localEndTime">{{ contestEnd }}</span>
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
      return isContestOver(this.contest)
    }
  },
  computed: {
    contest () {
      return this.$store.state.contest
    },
    localEndTime () {
      return moment(this.contest.end_time).local().format('YYYY-MM-DD HH:mm:ss')
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
