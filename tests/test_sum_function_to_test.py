import os, tempfile, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from cmdline.core import sum_function_to_test


def test_sum_function_to_test():

    assert 3 == sum_function_to_test(1,2)
