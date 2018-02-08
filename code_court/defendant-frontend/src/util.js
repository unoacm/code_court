import moment from 'moment'

function iso8601ToMoment (is8601Str) {
  return moment.tz(is8601Str, 'UTC').local()
}

function isContestOver (contest) {
  return iso8601ToMoment(contest.end_time) <= moment().local()
}

export { iso8601ToMoment, isContestOver }
