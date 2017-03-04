import Vue from 'vue'
import Router from 'vue-router'
import Hello from '@/components/Hello'
import Scoreboard from '@/components/Scoreboard'
import Problem from '@/components/Problem'
import Login from '@/components/Login'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Hello',
      component: Hello
    },
    {
      path: '/problem/:slug',
      name: 'problem',
      component: Problem
    },
    {
      path: '/scoreboard',
      name: 'scoreboard',
      component: Scoreboard
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})
