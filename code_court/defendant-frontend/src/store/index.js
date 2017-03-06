import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

const store = new Vuex.Store({
  state: {
    problems: {},
    user: null,
    isLoggedIn: !!localStorage.getItem('token')
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
        localStorage.setItem('token', response.data.access_token)
        context.commit('LOGIN')
        context.dispatch('LOAD_USER')
      }).catch(function (error) {
        console.log(error)
      })
    },
    LOGOUT: function (context) {
      localStorage.setItem('token', '')
      context.commit('LOGOUT')
      context.dispatch('LOAD_USER')
    }
  },
  mutations: {
    SET_PROBLEMS: (state, { problems }) => {
      state.problems = problems
    },
    SET_USER: (state, { user }) => {
      state.user = user
    },
    LOGIN: (state) => {
      state.isLoggedIn = true
    },
    LOGOUT: (state) => {
      state.isLoggedIn = false
      state.user = null
    }
  },
  getters: {
    get_problem: (state, { slug }) => state.problems[slug],
    get_auth: (state) => localStorage.getItem('token'),
    is_logged_in: (state) => state.isLoggedIn
  }
})

export default store
