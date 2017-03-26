import Vue from 'vue'
import Router from 'vue-router'
import Scoreboard from '@/components/Scoreboard'
import Problem from '@/components/Problem'
import Login from '@/components/Login'
import Info from '@/components/Info'

Vue.use(Router)

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'Info',
      component: Info
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
