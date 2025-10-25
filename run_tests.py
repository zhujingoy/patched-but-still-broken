#!/usr/bin/env python3

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))

if __name__ == '__main__':
    loader = unittest.TestLoader()
    start_dir = 'tests'
    suite = loader.discover(start_dir, pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("测试总结 / Test Summary")
    print("="*70)
    print(f"运行测试数 / Tests run: {result.testsRun}")
    print(f"成功 / Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败 / Failures: {len(result.failures)}")
    print(f"错误 / Errors: {len(result.errors)}")
    
    sys.exit(0 if result.wasSuccessful() else 1)
