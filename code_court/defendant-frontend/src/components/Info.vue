<template>
  <div>
    <h1 class="title is-1">Info</h1>
    <h2 class="title is-2">Contest Info</h2>
    <p>Contest ends in {{ contestEnd }}</p>
    <div v-html="convertToMarkdown(info)" class="content"></div>
  </div>
</template>

<script>
import moment from 'moment'
import marked from 'marked'
import 'moment-timezone'
import tzdata from '!json-loader!moment-timezone/data/packed/latest.json'
var instructions = `
# Instructions

- Go to <codecourt.org> and login.
- Select a problem from the navigation bar
- Read the problem description
- Select the language that you want to enter your solution in
- Enter your solution in the provided space
- Click the blue \`test\` button to test your solution against the sample input
    - You may enter your own input to test your own cases
- Click the yellow \`submit\` button when you think you've solved the problem
    - Your solution will be checked against a secret test case which will differ from the sample

Sample solutions to 2 problems are provided below:

## Hello World

Java:

\`\`\`Java
class Main {
    public static void main(String[] args) {
        System.out.println("Hello, world!");
    }
}
\`\`\`

Python3:

\`\`\`Python
print("Hello, World!")
\`\`\`

Python2:

\`\`\`Python
print "Hello, world!"
\`\`\`

C:

\`\`\`C
#include<stdio.h>

int main() {
    printf("Hello, world!\n");
    return 0;
}
\`\`\`

Rust:

\`\`\`Rust
fn main() {
    println!("Hello, World!");
}
\`\`\`

## Sum

Java:

\`\`\`Java
import java.util.Scanner;

class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int numCases = sc.nextInt();
        for (int i = 0; i < numCases; ++i) {
            int a = sc.nextInt();
            int b = sc.nextInt();
            System.out.printf("Case %d: %d\n", i+1, a+b);
        }
    }
}
\`\`\`

Python3:

\`\`\`Python
import sys

num = int(sys.stdin.readline().strip())

for n in range(1, num+1):
    x, y = map(int, sys.stdin.readline().strip().split())
    print("Case {}: {}".format(n, x+y))
\`\`\`

Python2:

\`\`\`Python
for i in range(int(raw_input())):
    nums = raw_input().split(' ')
    print 'Case ' + str(i+1) + ': ' + str(int(nums[1]) + int(nums[0]))
\`\`\`

C:

\`\`\`C
#include<stdio.h>

int main() {
    int numCases;
    scanf("%d", &numCases);

    for (int i = 0; i < numCases; ++i) {
        int a, b;
        scanf("%d %d", &a, &b);

        printf("Case %d: %d\n", i+1, a+b);
    }
    return 0;
}
\`\`\`

Rust:

\`\`\`Rust
use std::io::stdin;

fn main() {
    let num_cases: i32 = read_line().trim().parse().unwrap();

    for i in 1..num_cases+1 {
        let line = read_line();
        let nums: Vec<&str> = line.trim().split(" ").collect();
        let a: i32 = nums[0].parse().unwrap();
        let b: i32 = nums[1].parse().unwrap();

        println!("Case {}: {}", i, a+b);
    }
}

fn read_line() -> String {
    let mut line = String::new();
    stdin().read_line(&mut line).unwrap();

    line
}
\`\`\`
`

moment.tz.load(tzdata)

export default {
  data () {
    return {
      contestEnd: null
    }
  },
  methods: {
    convertToMarkdown: function (s) {
      return marked(s)
    },
    iso8601ToMoment (is8601Str) {
      return moment.tz(is8601Str, 'UTC').local()
    }
  },
  computed: {
    contest () {
      return this.$store.state.contest
    },

    info () {
      return instructions
    }
  },
  mounted: function () {
    this.contestEnd = this.iso8601ToMoment(this.contest.end_time).fromNow()
    setInterval(function () {
      this.contestEnd = this.iso8601ToMoment(this.contest.end_time).fromNow()
    }.bind(this), 30000)
  }
}
</script>

<style scoped>
</style>
