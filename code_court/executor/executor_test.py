import re
import unittest

import responses

from executor import Executor, get_conf


def get_test_conf():
    conf = get_conf()
    conf['insecure'] = True
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


def setup_submit_writ_resp():
    responses.add(responses.POST, re.compile(r"http://.*?/api/submit-writ/.*?"),
                  json="Good", status=200)


def setup_return_writ_resp():
    responses.add(responses.POST, re.compile(r"http://.*?/api/return-without-run/.*?"),
                  json="Good", status=200)


class ExecutorTest(unittest.TestCase):
    @responses.activate
    def test_normal_run(self):
        setup_get_writ_resp(get_test_writ())
        setup_submit_writ_resp()
        Executor(get_test_conf())._run()

    @responses.activate
    def test_return_writ(self):
        setup_get_writ_resp(get_test_writ())
        setup_return_writ_resp()
        Executor(get_test_conf())._run()

    def test_run_timelimit(self):
        pass

    def test_run_outputlimit(self):
        pass

    def test_run_with_compile_error(self):
        pass


if __name__ == '__main__':
    unittest.main()
