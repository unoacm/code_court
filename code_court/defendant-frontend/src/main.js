import Vue from 'vue'
import App from './App'
import router from './router'
import store from './store'

import axios from 'axios'
import { sync } from 'vuex-router-sync'

import 'font-awesome-webpack'

sync(store, router)

Vue.config.productionTip = false

if (store.state.loginToken) {
  axios.defaults.headers.common['Authorization'] = 'Bearer ' + store.state.loginToken
}

router.beforeEach((to, from, next) => {
  if (to.name !== 'login' && !store.state.loginToken) {
    next({name: 'login'})
  } else {
    next()
  }
})

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  store,
  template: '<App/>',

  components: { App }
})

