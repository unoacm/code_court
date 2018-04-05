<template>
  <div>
    <transition-group class="ul-table" name="table-row" tag="ul">
      <li class="table-row-item" key="0">
          <span></span>
          <span>Defendant</span>
          <span>Score</span>
          <span>Penalty</span>
          <span v-for="(state, prob) in scores[0].problem_states">{{ prob }}</span>
      </li>
      <li v-for="(row, i) in scores" :key="row.user.username" class="table-row-item" >
          <span>{{ i+1 }}</span>
          <span :title="row.user.username">{{ row.user.username }}</span>
          <span>{{ row.num_solved }}</span>
          <span>{{ row.penalty }}</span>
          <span v-for="(state, prob) in row.problem_states" :class="{'correct': state}">
            <div v-if="prob" class="icon">
              <i v-if="state" class="fa fa-check"></i>
            </div>
          </span>
      </li>
    </transition-group>
  </div>
</template>

<script>
export default {
  data () {
    return {
    }
  },
  computed: {
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
.table-row-move {
  transition: all 1s;
}

.table-row-item {
  backface-visibility: hidden;
  background-color: #fff;
}

.ul-table {
  width: 100%;
  display: table;
  border: 1px solid black;
  background-color: #fff;
}

.ul-table li:first-child {
  font-weight: bold;
}

.ul-table li {
  display: table-row;

}

.ul-table span {
  display: table-cell;
  padding: 10px;
  border: 1px solid black;
}

.ul-table span:first-child {
  width: 1%;
}

.correct {
  background-color:#60e760;
  text-align: center;
}

.incorrect {
  background-color:#e87272;
}
</style>
