import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'scripts'))

suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
result = unittest.TextTestRunner(verbosity=0).run(suite)
os.environ['TEST_RC'] = '0' if result.wasSuccessful() else '1'
import w67
raise SystemExit(0 if result.wasSuccessful() else 1)
