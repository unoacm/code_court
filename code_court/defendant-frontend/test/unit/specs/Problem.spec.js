import Vue from 'vue'
import Vuex from 'vuex'
import Info from '@/components/Problem'

describe('Info.vue', () => {
  var vm

  beforeEach(() => {
    const state = {contest: {
    }}
    const store = new Vuex.Store({state})
    const Constructor = Vue.extend({...Info, store, router})
    vm = new Constructor().$mount()
  })

  it('should be ok', () => {
    expect(vm).to.be.ok
  })
})
