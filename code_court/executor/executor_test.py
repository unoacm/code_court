import json
import re
import unittest

import responses

from executor import Executor, get_conf


def get_test_conf():
    conf = get_conf()
    conf['insecure'] = True
    conf['timeout'] = 1
    conf['char_output_limit'] = 1000
    return conf


def get_test_writ():
    return {
        "status": "found",
        "source_code": "print('hello')",
        "language": "python",
        "run_script": "cat $input_file | python3 $program_file",
        "input": "",
        "run_id": 1,
        "return_url": "http://localhost:9191/api/submit-writ"
    }


def setup_get_writ_resp(writ):
    responses.add(responses.GET, re.compile(r"http://.*?/api/get-writ"),
                  json=writ, status=200)


def setup_submit_writ_resp(callback):
    responses.add_callback(
        responses.POST,
        re.compile(r"http://.*?/api/submit-writ/.*?"),
        callback=callback
    )


def setup_return_writ_resp():
    responses.add(responses.POST, re.compile(r"http://.*?/api/return-without-run/.*?"),
                  json="Good", status=200)


class ExecutorTest(unittest.TestCase):
    @responses.activate
    def test_normal_run(self):
        def submit_callback(request):
            resp = json.loads(request.body)
            self.assertEqual(resp['output'], "hello\n")
            self.assertEqual(resp['state'], "Executed")
            return (200, {}, "Good")

        setup_get_writ_resp(get_test_writ())
        setup_submit_writ_resp(submit_callback)
        Executor(get_test_conf())._run()

    @responses.activate
    def test_return_writ(self):
        setup_get_writ_resp(get_test_writ())
        setup_return_writ_resp()
        Executor(get_test_conf())._run()

    @responses.activate
    def test_run_timelimit(self):
        def submit_callback(request):
            resp = json.loads(request.body)
            self.assertEqual(resp['output'], "Error: Timed out")
            self.assertEqual(resp['state'], "TimedOut")
            return (200, {}, "Good")

        test_writ = get_test_writ()
        test_writ['source_code'] = 'import time\ntime.sleep(1000)'
        setup_get_writ_resp(test_writ)
        setup_submit_writ_resp(submit_callback)
        Executor(get_test_conf())._run()

    @responses.activate
    def test_run_outputlimit(self):
        def submit_callback(request):
            resp = json.loads(request.body)
            self.assertEqual(resp['output'], "Error: Output limit exceeded")
            self.assertEqual(resp['state'], "OutputLimitExceeded")
            return (200, {}, "Good")

        test_writ = get_test_writ()
        test_writ['source_code'] = 'print("a"*2000)'
        setup_get_writ_resp(test_writ)
        setup_submit_writ_resp(submit_callback)
        Executor(get_test_conf())._run()

    @responses.activate
    def test_run_with_compile_error(self):
        def submit_callback(request):
            resp = json.loads(request.body)
            self.assertIn("SyntaxError: unexpected EOF while parsing", resp['output'])
            self.assertEqual(resp['state'], "Executed")
            return (200, {}, "Good")

        test_writ = get_test_writ()
        test_writ['source_code'] = 'if test:'
        setup_get_writ_resp(test_writ)
        setup_submit_writ_resp(submit_callback)
        Executor(get_test_conf())._run()


if __name__ == '__main__':
    unittest.main()
