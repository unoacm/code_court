import Vue from 'vue'
import Notification from '@/components/Notification'

describe('Notification.vue', () => {
  it('should render correct contents', () => {
    const propsData = {
      message: 'hello'
    }

    const Constructor = Vue.extend(Notification)
    const vm = new Constructor({ propsData }).$mount()
    expect(vm.$el.querySelector('.notification').textContent.trim()).to.equal('hello')
  })
})
