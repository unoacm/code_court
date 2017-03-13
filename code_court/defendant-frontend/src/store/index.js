import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

import createPersistedState from 'vuex-persistedstate'

Vue.use(Vuex)

const store = new Vuex.Store({
  plugins: [createPersistedState()],
  state: {
    problems: {},
    user: null,
    langs: [],
    sourceCodes: {},
    loginToken: ''
  },
  actions: {
    LOAD_PROBLEMS: function ({ commit }) {
      axios.get('http://localhost:9191/api/problems').then((response) => {
        commit('SET_PROBLEMS', { problems: response.data })
      })
    },
    LOAD_USER: function (context) {
      axios.get('http://localhost:9191/api/current-user').then((response) => {
        context.commit('SET_USER', { user: response.data })
      })
    },
    LOAD_LANGS: function (context) {
      axios.get('http://localhost:9191/api/languages').then((response) => {
        context.commit('SET_LANGS', { langs: response.data })
      })
    },
    LOAD_RUNS: function (context) {
      axios.get('http://localhost:9191/api/current-user-runs').then((response) => {
        context.commit('SET_RUNS', { runs: response.data })
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
      }).catch(function (error) {
        console.log(error)
      })
    },
    LOGOUT: function (context) {
      // add timeout to make logout feel more real
      setTimeout(function () {
        context.commit('SET_LOGIN_TOKEN', { token: '' })
        context.commit('SET_USER', { user: null })
        context.commit('SET_PROBLEMS', { problems: {} })
      }, 200)
    }
  },
  mutations: {
    SET_PROBLEMS: (state, { problems }) => {
      state.problems = problems
    },
    SET_USER: (state, { user }) => {
      state.user = user
    },
    SET_LANGS: (state, { langs }) => {
      state.langs = langs
    },
    SET_LOGIN_TOKEN: (state, { token }) => {
      state.loginToken = token
    },
    UPDATE_SOURCE_CODE: (state, { problemSlug, sourceCode }) => {
      state.sourceCodes[problemSlug] = sourceCode
    },
    LOGOUT: (state) => {
      state.loginToken = false
      state.user = null
    }
  },
  getters: {
    get_problem: (state, { slug }) => state.problems[slug],
    isLoggedIn: (state) => !!state.user,
    getSourceCode: (state, getters) => (problemSlug) => {
      var code = state.sourceCodes[problemSlug]
      if (code) {
        return code
      } else {
        return ''
      }
    }
  }
})

export default store
