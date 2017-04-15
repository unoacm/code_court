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
    LOAD_PROBLEMS: function (context, loginToken = null) {
      if (!loginToken) {
        if (!context.state.loginToken) {
          return
        } else {
          loginToken = context.state.loginToken
        }
      }

      axios.get(
        'http://localhost:9191/api/problems',
        {
          headers: {
            'Authorization': 'Bearer ' + loginToken
          }
        }
      ).then((response) => {
        context.commit('SET_PROBLEMS', { problems: response.data })
      })
    },
    LOAD_SCORES: function (context, loginToken = null) {
      if (!loginToken) {
        if (!context.state.loginToken) {
          return
        } else {
          loginToken = context.state.loginToken
        }
      }

      axios.get(
        'http://localhost:9191/api/scores',
        {
          headers: {
            'Authorization': 'Bearer ' + loginToken
          }
        }
      ).then((response) => {
        context.commit('SET_SCORES', { scores: response.data })
      })
    },
    LOAD_USER: function (context, loginToken = null) {
      if (!loginToken) {
        if (!context.state.loginToken) {
          return
        } else {
          loginToken = context.state.loginToken
        }
      }

      axios.get(
        'http://localhost:9191/api/current-user',
        {
          headers: {
            'Authorization': 'Bearer ' + loginToken
          }
        }
      ).then((response) => {
        context.commit('SET_USER', { user: response.data })
      })
    },
    LOAD_CONTEST: function (context, loginToken = null) {
      if (!loginToken) {
        if (!context.state.loginToken) {
          return
        } else {
          loginToken = context.state.loginToken
        }
      }

      axios.get(
        'http://localhost:9191/api/get-contest-info',
        {
          headers: {
            'Authorization': 'Bearer ' + loginToken
          }
        }
      ).then((response) => {
        context.commit('SET_CONTEST', { contest: response.data })
      })
    },
    LOAD_LANGS: function (context) {
      axios.get('http://localhost:9191/api/languages').then((response) => {
        context.commit('SET_LANGS', { langs: response.data })
      })
    },
    LOGIN: function (context, creds) {
      axios.post('http://localhost:9191/api/login', {
        email: creds.email,
        password: creds.password
      }).then((response) => {
        context.commit('SET_LOGIN_TOKEN', { token: response.data.access_token })

        context.dispatch('LOAD_USER')
        context.dispatch('LOAD_PROBLEMS')

        // clear old alerts here
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
      state.langs = langs
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
      if (!(problemSlug in state.sourceCodes) || !(lang in state.sourceCodes[problemSlug])) {
        return ''
      }
      return state.sourceCodes[problemSlug][lang]
    }
  }
})

export default store
