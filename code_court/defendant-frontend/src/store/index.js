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
    scores: [],
    langs: [],
    alerts: [],
    user: null,
    sourceCodes: {},
    loginToken: ''
  },
  actions: {
    LOAD_PROBLEMS: function (context) {
      axios.get('/api/problems').then((response) => {
        context.commit('SET_PROBLEMS', { problems: response.data })
      })
    },
    LOAD_SCORES: function (context, contestId) {
      axios.get('/api/scores/' + contestId).then((response) => {
        context.commit('SET_SCORES', { scores: response.data })
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
    LOGIN: function (context, creds) {
      axios.post('/api/login', {
        email: creds.email,
        password: creds.password
      }).then((response) => {
        context.commit('SET_LOGIN_TOKEN', { token: response.data.access_token })

        axios.defaults.headers.common['Authorization'] = 'Bearer ' + store.state.loginToken

        context.dispatch('LOAD_USER')
        context.dispatch('LOAD_PROBLEMS')
        context.dispatch('LOAD_CONTEST')
        context.dispatch('DELETE_ALERTS')

        router.push({ path: '/' })
      }).catch(function (error) {
        console.log(error)
        context.commit('PUSH_ALERT', {text: 'Failed to login', severity: 'danger'})
      })
    },
    LOGOUT: function (context) {
      // add timeout to make logout feel more real
      setTimeout(function () {
        context.commit('SET_LOGIN_TOKEN', { token: '' })
        context.commit('SET_USER', { user: null })
        context.commit('SET_PROBLEMS', { problems: {} })
      }, 200)
      router.push({ path: '/' })
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
