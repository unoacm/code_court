<template>
  <div>
    <div class="container">
      <ul class="navigation">
        <li><router-link to="/scoreboard">Scoreboard</router-link></li>
        <li v-if="user"><router-link to="/clarifications">Clarification</router-link></li>
        <li>&nbsp;&nbsp;</li>
        <li v-if="user" v-for="(problem, slug) in problems">
          <router-link :to="{ name: 'problem', params: { slug: slug }}" class="problem-link">
            {{ slug }}
          </router-link>
        </li>
        <li>&nbsp;&nbsp;</li>
        <li v-if="!user"><router-link to="/login">Login</router-link></li>
        <li v-if="user"><button v-on:click="logout" class="logout">Logout {{ user.email }}</button></li>
      </ul>
      <hr>
    </div>
    <div class="container">
      <router-view></router-view>
    </div>
  </div>
</template>

<script>
export default {
  name: 'app',
  created: function () {
  },
  computed: {
    problems () {
      return this.$store.state.problems
    },
    user () {
      return this.$store.state.user
    }
  },
  methods: {
    logout: function () {
      this.$store.dispatch('LOGOUT')
    }
  }
}
</script>

<style>
ul.navigation {
  list-style: none;
  overflow: hidden;
  padding: 0;
  margin: 0;
  margin-top: 3px;
  border-bottom: 2px solid black;
}

ul.navigation li {
  float:left;
}

ul.navigation li a,
ul.navigation li button {
  display: inline-block;
  padding: 15px 15px;
  margin: 0px 1px;
  border-top: 1px solid black;
  border-left: 1px solid black;
  border-right: 1px solid black;
  border-bottom: none;
  text-decoration: none;
  background-color: #eee;
  transition: 0.3s;
  color: #000;
}

ul.navigation li a:hover {
  background-color: #ccc;
}

ul.navigation li a.problem-link {
  background-color: #c4daef;
}

ul.navigation li a.problem-link.router-link-active {
  background-color: #fff;
}

ul.navigation li a.problem-link.router-link-active:hover {
  background-color: #fff;
}


ul.navigation li a.problem-link:hover {
  background-color: #aad1f7;
}

ul.navigation li button.logout {
  color: #fff;
  background-color: #b22525;
}

ul.navigation li button.logout:hover {
  background-color: #872323;
}

</style>
