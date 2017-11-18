<template>
  <div>
    <h1 class="title is-1">Info</h1>
    <h2 class="title is-2">Contest Info</h2>
    <p>Contest ends in {{ contestEnd }}</p>

<h1><a id="Instructions_0"></a>Instructions</h1>
<pre>
Go to <a href="http://codecourt.org">codecourt.org</a> and login.
Select a problem from the navigation bar
Read the problem description
Select the language that you want to enter your solution in
Enter your solution in the provided space
Click the blue <code>test</code> button to test your solution against the sample input
You may enter your own input to test your own cases
Click the yellow <code>submit</code> button when you think you’ve solved the problem
Your solution will be checked against a secret test case which will differ from the sample
</pre>
<p>Sample solutions to 2 problems are provided below:</p>
<h2><a id="Hello_World_14"></a>Hello World</h2>
<p>Java:</p>
<pre><code class="language-Java"><span class="hljs-class"><span class="hljs-keyword">class</span> <span class="hljs-title">Main</span> </span>{
    <span class="hljs-function"><span class="hljs-keyword">public</span> <span class="hljs-keyword">static</span> <span class="hljs-keyword">void</span> <span class="hljs-title">main</span><span class="hljs-params">(String[] args)</span> </span>{
        System.out.println(<span class="hljs-string">"Hello, world!"</span>);
    }
}
</code></pre>
<p>Python3:</p>
<pre><code class="language-Python">print(<span class="hljs-string">"Hello, World!"</span>)
</code></pre>
<p>Python2:</p>
<pre><code class="language-Python"><span class="hljs-keyword">print</span> <span class="hljs-string">"Hello, world!"</span>
</code></pre>
<p>C:</p>
<pre><code class="language-C"><span class="hljs-preprocessor">#<span class="hljs-keyword">include</span><span class="hljs-string">&lt;stdio.h&gt;</span></span>

<span class="hljs-function"><span class="hljs-keyword">int</span> <span class="hljs-title">main</span><span class="hljs-params">()</span> </span>{
    <span class="hljs-built_in">printf</span>(<span class="hljs-string">"Hello, world!\n"</span>);
    <span class="hljs-keyword">return</span> <span class="hljs-number">0</span>;
}
</code></pre>
<p>Rust:</p>
<pre><code class="language-Rust"><span class="hljs-function"><span class="hljs-keyword">fn</span> <span class="hljs-title">main</span></span>() {
    <span class="hljs-built_in">println!</span>(<span class="hljs-string">"Hello, World!"</span>);
}
</code></pre>
<h2><a id="Sum_57"></a>Sum</h2>
<p>Java:</p>
<pre><code class="language-Java"><span class="hljs-keyword">import</span> java.util.Scanner;

<span class="hljs-class"><span class="hljs-keyword">class</span> <span class="hljs-title">Main</span> </span>{
    <span class="hljs-function"><span class="hljs-keyword">public</span> <span class="hljs-keyword">static</span> <span class="hljs-keyword">void</span> <span class="hljs-title">main</span><span class="hljs-params">(String[] args)</span> </span>{
        Scanner sc = <span class="hljs-keyword">new</span> Scanner(System.in);
        <span class="hljs-keyword">int</span> numCases = sc.nextInt();
        <span class="hljs-keyword">for</span> (<span class="hljs-keyword">int</span> i = <span class="hljs-number">0</span>; i &lt; numCases; ++i) {
            <span class="hljs-keyword">int</span> a = sc.nextInt();
            <span class="hljs-keyword">int</span> b = sc.nextInt();
            System.out.printf(<span class="hljs-string">"Case %d: %d\n"</span>, i+<span class="hljs-number">1</span>, a+b);
        }
    }
}
</code></pre>
<p>Python3:</p>
<pre><code class="language-Python"><span class="hljs-keyword">import</span> sys

num = int(sys.stdin.readline().strip())

<span class="hljs-keyword">for</span> n <span class="hljs-keyword">in</span> range(<span class="hljs-number">1</span>, num+<span class="hljs-number">1</span>):
    x, y = map(int, sys.stdin.readline().strip().split())
    print(<span class="hljs-string">"Case {}: {}"</span>.format(n, x+y))
</code></pre>
<p>Python2:</p>
<pre><code class="language-Python"><span class="hljs-keyword">for</span> i <span class="hljs-keyword">in</span> range(int(raw_input())):
    nums = raw_input().split(<span class="hljs-string">' '</span>)
    <span class="hljs-keyword">print</span> <span class="hljs-string">'Case '</span> + str(i+<span class="hljs-number">1</span>) + <span class="hljs-string">': '</span> + str(int(nums[<span class="hljs-number">1</span>]) + int(nums[<span class="hljs-number">0</span>]))
</code></pre>
<p>C:</p>
<pre><code class="language-C"><span class="hljs-preprocessor">#<span class="hljs-keyword">include</span><span class="hljs-string">&lt;stdio.h&gt;</span></span>

<span class="hljs-function"><span class="hljs-keyword">int</span> <span class="hljs-title">main</span><span class="hljs-params">()</span> </span>{
    <span class="hljs-keyword">int</span> numCases;
    <span class="hljs-built_in">scanf</span>(<span class="hljs-string">"%d"</span>, &amp;numCases);

    <span class="hljs-keyword">for</span> (<span class="hljs-keyword">int</span> i = <span class="hljs-number">0</span>; i &lt; numCases; ++i) {
        <span class="hljs-keyword">int</span> a, b;
        <span class="hljs-built_in">scanf</span>(<span class="hljs-string">"%d %d"</span>, &amp;a, &amp;b);

        <span class="hljs-built_in">printf</span>(<span class="hljs-string">"Case %d: %d\n"</span>, i+<span class="hljs-number">1</span>, a+b);
    }
    <span class="hljs-keyword">return</span> <span class="hljs-number">0</span>;
}
</code></pre>
<p>Rust:</p>
<pre><code class="language-Rust"><span class="hljs-keyword">use</span> std::io::stdin;

<span class="hljs-function"><span class="hljs-keyword">fn</span> <span class="hljs-title">main</span></span>() {
    <span class="hljs-keyword">let</span> num_cases: <span class="hljs-keyword">i32</span> = read_line().trim().parse().unwrap();

    <span class="hljs-keyword">for</span> i <span class="hljs-keyword">in</span> <span class="hljs-number">1</span>..num_cases+<span class="hljs-number">1</span> {
        <span class="hljs-keyword">let</span> line = read_line();
        <span class="hljs-keyword">let</span> nums: <span class="hljs-built_in">Vec</span>&lt;&amp;<span class="hljs-keyword">str</span>&gt; = line.trim().split(<span class="hljs-string">" "</span>).collect();
        <span class="hljs-keyword">let</span> a: <span class="hljs-keyword">i32</span> = nums[<span class="hljs-number">0</span>].parse().unwrap();
        <span class="hljs-keyword">let</span> b: <span class="hljs-keyword">i32</span> = nums[<span class="hljs-number">1</span>].parse().unwrap();

        <span class="hljs-built_in">println!</span>(<span class="hljs-string">"Case {}: {}"</span>, i, a+b);
    }
}

<span class="hljs-function"><span class="hljs-keyword">fn</span> <span class="hljs-title">read_line</span></span>() -&gt; <span class="hljs-built_in">String</span> {
    <span class="hljs-keyword">let</span> <span class="hljs-keyword">mut</span> line = String::new();
    stdin().read_line(&amp;<span class="hljs-keyword">mut</span> line).unwrap();

    line
}
</code></pre>

  </div>
</template>

<script>
import moment from 'moment'
import 'moment-timezone'
import tzdata from '!json-loader!moment-timezone/data/packed/latest.json'

moment.tz.load(tzdata)

export default {
  data () {
    return {
      contestEnd: null
    }
  },
  methods: {
    iso8601ToMoment (is8601Str) {
      return moment.tz(is8601Str, 'UTC').local()
    }
  },
  computed: {
    contest () {
      return this.$store.state.contest
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
