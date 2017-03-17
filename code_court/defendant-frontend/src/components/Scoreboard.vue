<template>
  <div>
    <table class="table is-striped">
      <thead>
        <tr>
          <th></th>
          <th>Defendant</th>
          <th>Score</th>
          <th>Penalty</th>
          <th v-for="prob in problems">{{ prob.slug }}</th>
        </tr>
      </thead>
      <tbody is="transition-group" name="flip-list" tag="tbody">
        <tr v-for="(row, i) in scores" key="i">
          <td>{{ i+1 }}</td>
          <td :title="row.user.email">{{ row.user.name }}</td>
          <td>{{ row.num_solved }}</td>
          <td>{{ row.penalty }}</td>
          <td v-for="prob in problems">
            <span v-if="row.problem_states[prob.slug]" class="icon">
              <i class="fa fa-check"></i>
            </span>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script>
export default {
  data () {
    return {
    }
  },
  computed: {
    problems () {
      return this.$store.state.problems
    },
    scores () {
      return this.$store.state.scores
    }
  }
}
</script>

<style scoped>
.flip-list-move {
  transition: transform 1s;
}
</style>
