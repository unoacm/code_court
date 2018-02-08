<template>
  <div>
    <div v-if="!isContestOver()">
      <span :title="'Ends at ' + localEndTime">Ends {{ contestEndStatement }}</span>
    </div>
    <div v-else>Contest is over</div>

  </div>
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
    },
    contestEndStatement () {
      return iso8601ToMoment(this.contest.end_time).fromNow()
    }
  },
  mounted: function () {
    setInterval(function () {
      this.$forceUpdate()
    }.bind(this), 5000)
  }
}
</script>

<style scoped>
</style>
