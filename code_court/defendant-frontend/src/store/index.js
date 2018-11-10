import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'
import router from '../router'

import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

const store = new Vuex.Store({
  plugins: [createPersistedState()],
  state: {
    problems: {},
    contest: {},
    conf: {
      extra_signup_fields: [],
      run_refresh_interval_millseconds: 30 * 1000,
      score_refresh_interval_millseconds: 60 * 1000,
      misc_refresh_interval_millseconds: 120 * 1000
    },
    scores: [],
    langs: [],
    alerts: [],
    clars: [],
    user: null,
    sourceCodes: {},
    loginToken: ''
  },
  actions: {
    LOAD_PROBLEMS: function (context, userId) {
      const url = userId ? '/api/problems/' + userId : '/api/problems'
      axios.get(url).then((response) => {
        context.commit('SET_PROBLEMS', { problems: response.data })
      })
    },
    LOAD_SCORES: function (context, contestId) {
      axios.get('/api/scores/' + contestId).then((response) => {
        context.commit('SET_SCORES', { scores: response.data })
      })
    },
    LOAD_CONF: function (context, userId) {
      const url = userId ? '/api/conf/' + userId : '/api/conf'
      axios.get(url).then((response) => {
        context.commit('SET_CONF', { conf: response.data })
      })
    },
    LOAD_USER: function (context) {
      axios.get('/api/current-user').then((response) => {
        context.commit('SET_USER', { user: response.data })
      })
    },
    LOAD_CONTEST: function (context) {
      axios.get('/api/get-contest-info').then((response) => {
        context.commit('SET_CONTEST', { contest: response.data })
        context.dispatch('LOAD_SCORES', response.data.id)
      })
    },
    LOAD_LANGS: function (context) {
      axios.get('/api/languages').then((response) => {
        context.commit('SET_LANGS', { langs: response.data })
      })
    },
    LOAD_CLARS: function (context) {
      axios.get('/api/clarifications').then((response) => {
        context.commit('SET_CLARS', { clars: response.data })
      })
    },
    LOGIN: function (context, creds) {
      axios.post('/api/login', {
        username: creds.username,
        password: creds.password
      }).then((response) => {
        context.commit('SET_LOGIN_TOKEN', { token: response.data.access_token })

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + store.state.loginToken

        context.dispatch('LOAD_USER')
        context.dispatch('LOAD_PROBLEMS')
        context.dispatch('LOAD_CONTEST')
        context.dispatch('LOAD_CLARS')

        context.commit('DELETE_ALERTS')

        router.push({ path: '/' })
      }).catch(function (error) {
        console.log('Failed to login')
        console.log(error)
        context.commit('DELETE_ALERTS')
        context.commit('PUSH_ALERT', {text: 'Failed to login', severity: 'danger'})
      })
    },
    SIGNUP: function (context, creds) {
      axios.post('/api/signup', creds).then((response) => {
        context.commit('SET_LOGIN_TOKEN', { token: response.data.access_token })

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + store.state.loginToken

        context.dispatch('LOAD_USER')
        context.dispatch('LOAD_PROBLEMS')
        context.dispatch('LOAD_CONTEST')
        context.dispatch('LOAD_CLARS')

        context.commit('DELETE_ALERTS')

        router.push({ path: '/' })
      }).catch(function (error) {
        context.commit('DELETE_ALERTS')
        const errorReason = error.response.data.error
        context.commit('PUSH_ALERT', {text: 'Failed to signup: ' + errorReason, severity: 'danger'})
      })
    },
    LOGOUT: function (context) {
      // add timeout to make logout feel more real
      setTimeout(function () {
        context.commit('SET_LOGIN_TOKEN', { token: '' })
        context.commit('SET_USER', { user: null })
        context.commit('SET_PROBLEMS', { problems: {} })
        context.commit('SET_CONTEST', { contest: {} })
        context.commit('SET_SCORES', { scores: {} })
        context.commit('DELETE_ALERTS')
      }, 200)
      router.push({ path: '/login' })
    }
  },
  mutations: {
    SET_PROBLEMS: (state, { problems }) => {
      state.problems = problems
    },
    SET_USER: (state, { user }) => {
      state.user = user
    },
    SET_SCORES: (state, { scores }) => {
      state.scores = scores
    },
    SET_CONF: (state, { conf }) => {
      state.conf = conf
    },
    SET_LANGS: (state, { langs }) => {
      var langObj = {}
      for (var lang of langs) {
        langObj[lang.name] = lang
      }
      state.langs = langObj
    },
    SET_CONTEST: (state, { contest }) => {
      state.contest = contest
    },
    SET_CLARS: (state, { clars }) => {
      var clarObj = {}
      for (var clar of clars) {
        clarObj[clar.subject] = clar
      }
      state.clars = clarObj
    },
    PUSH_ALERT: (state, { text, severity }) => {
      state.alerts.push({
        text,
        severity
      })
    },
    DELETE_ALERTS: (state) => {
      state.alerts = []
    },
    ADD_FAKE_RUN: (state, run) => {
      state.problems[run.problemSlug].runs.push(run)
    },
    SET_LOGIN_TOKEN: (state, { token }) => {
      state.loginToken = token
    },
    UPDATE_SOURCE_CODE: (state, { problemSlug, lang, sourceCode }) => {
      if (!(problemSlug in state.sourceCodes)) {
        state.sourceCodes[problemSlug] = {}
      }
      state.sourceCodes[problemSlug][lang] = sourceCode
    },
    LOGOUT: (state) => {
      state.loginToken = false
      state.user = null
    }
  },
  getters: {
    get_problem: (state, { slug }) => state.problems[slug],
    isLoggedIn: (state) => !!state.user,
    getSourceCode: (state, getters) => (problemSlug, lang) => {
      if (!(problemSlug in state.sourceCodes) || !(lang.name in state.sourceCodes[problemSlug])) {
        if (lang.default_template) {
          return lang.default_template
        } else {
          return ''
        }
      }
      return state.sourceCodes[problemSlug][lang.name]
    }
  }
})

export default store
