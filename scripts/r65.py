import os
import sys
import unittest

suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=0).run(suite)
os.environ['TEST_RC'] = '0' if result.wasSuccessful() else '1'
import w65
raise SystemExit(0 if result.wasSuccessful() else 1)
