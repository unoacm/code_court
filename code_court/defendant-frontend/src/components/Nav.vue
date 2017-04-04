<template>
  <div>
    <div class="container">
      <div class="navigation level">
        <div class="level-left">
          <span><router-link to="/" exact>Info</router-link></span>
          <span><router-link to="/scoreboard">Scoreboard</router-link></span>
          <!--<span v-if="user"><router-link to="/clarifications">Clarification <div class="tag is-dark">5</div></router-link></span>-->
        </div>

        <div>
          <span v-if="user" v-for="(problem, slug) in problems">
            <router-link :to="{ name: 'problem', params: { slug: slug }}" class="problem-link">
              {{ slug }}
            </router-link>
          </span>
        </div>

        <div class="level-right">
          <span v-if="!user"><router-link to="/login">Login</router-link></span>
          <span v-if="user"><a @click.prevent="logout()" class="logout">Logout {{ user.email }}</a></span>
        </div>
      </div>
    </div>
    <hr>

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
    },
    is_passed: function (problem) {
      for (var run of problem.runs) {
        if (run.is_submission && run.is_passed) {
          return true
        }
      }
      return false
    }
  }
}
</script>

<style scoped>
.slide-left-enter, .slide-right-leave-active {
  opacity: 0;
  transform: translate(30px, 0);
}
.slide-left-leave-active, .slide-right-enter {
  opacity: 0;
  transform: translate(-30px, 0);
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}

.navigation {
  margin-top: 3px;
  border-bottom: 2px solid black;
}

.navigation div a,
.navigation div button {
  display: inline-block;
  padding: 10px;
  margin: 0px 1px;
  border-top: 1px solid black;
  border-left: 1px solid black;
  border-right: 1px solid black;
  border-bottom: none;
  text-decoration: none;
  background-color: #EFECCA;
  transition: 0.3s;
  color: #000;
  border-radius: 5px 5px 0px 0px;
}

.navigation div a:hover {
  background-color: #ccc;
}

.navigation div a.problem-link {
  background-color: #046380;
  color: #fff;
}

.navigation div a.problem-link:hover {
  background-color: #002F2F;
}

.navigation div a.router-link-active {
  background-color: #fff;
  color: #000;
}

.navigation div a.router-link-active:hover {
  background-color: #fff;
  color: #000;
}

.navigation div a.logout {
  color: #fff;
  background-color: #b22525;
}

.navigation div a.logout:hover {
  background-color: #872323;
}

</style>
