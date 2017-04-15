<template>
  <div class="alert-body" v-if="!isHidden">
    <div :class="['notification', severity ? 'is-'+severity : '']">
      <button v-on:click="hide" class="delete"></button>
      {{ message }}
    </div>
  </div>
</template>

<script>
export default {
  data () {
    return {
      isHidden: false
    }
  },
  props: ['message', 'severity'],
  computed: {
  },
  created: function () {
  },
  methods: {
    hide: function () {
      this.isHidden = true
    }
  },
  components: {
  }
}
</script>

<style scoped>
.alert-body {
  margin-bottom:2px;
}
</style>
