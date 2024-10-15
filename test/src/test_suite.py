# Copyright (C) 2023 Siemens AG
#
# SPDX-License-Identifier: MIT

import unittest
import sys
from HtmlTestRunner import HTMLTestRunner
from test.src.functions.log_function import test_logs


class CustomHTMLTestRunner(HTMLTestRunner):
    def run(self, test):
        result = super().run(test)
        if not result.wasSuccessful():
            sys.exit(1)
        return result


# load the test cases
loader = unittest.TestLoader()

suite1 = loader.loadTestsFromModule(test_logs)

# add them to a test suite
suite = unittest.TestSuite(
    [
        suite1,
    ]
)

# run the suite using the custom test runner
runner = CustomHTMLTestRunner(output="test_reports")
runner.run(suite)
