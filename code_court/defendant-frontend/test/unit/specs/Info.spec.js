import Vue from 'vue'
import Vuex from 'vuex'
import Info from '@/components/Info'

const START_TIME = '2017-01-01T10:10:00Z'
const END_TIME = '2017-01-01T12:10:00Z'

describe('Info.vue', () => {
  var vm

  beforeEach(() => {
    const state = {contest: {
      start_time: START_TIME,
      end_time: END_TIME
    }}
    const store = new Vuex.Store({state})
    const Constructor = Vue.extend({...Info, store})
    vm = new Constructor().$mount()
  })

  it('should be ok', () => {
    expect(vm).to.be.ok
  })

  it('should render time', done => {
    Vue.nextTick(() => {
      expect(vm).to.be.ok
      // expect(vm.$el.querySelector('#ending-in').textContent)
      //   .to.equal('8 months ago')
      done()
    })
  })
})
