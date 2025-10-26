import unittest
import sys
import os
from unittest.mock import patch
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import common


class TestCommon(unittest.TestCase):
    
    @patch('common.sys.platform', 'linux')
    @patch('common.getpass.getuser', return_value='testuser')
    def test_get_base_dir_linux(self, mock_getuser):
        base_dir = common.get_base_dir()
        
        self.assertEqual(base_dir, '/user_data')
    
    @patch('common.sys.platform', 'darwin')
    @patch('common.getpass.getuser', return_value='zhouting')
    def test_get_base_dir_darwin_zhouting(self, mock_getuser):
        base_dir = common.get_base_dir()
        
        self.assertEqual(base_dir, '/Users/zhouting/data_for_2025_1024_game')
    
    @patch('common.sys.platform', 'darwin')
    @patch('common.getpass.getuser', return_value='lyf')
    def test_get_base_dir_darwin_lyf(self, mock_getuser):
        base_dir = common.get_base_dir()
        
        self.assertEqual(base_dir, '/Users/lyf/data_for_2025_1024_game')
    
    @patch('common.sys.platform', 'win32')
    @patch('common.getpass.getuser', return_value='testuser')
    def test_get_base_dir_windows(self, mock_getuser):
        base_dir = common.get_base_dir()
        
        self.assertEqual(base_dir, 'C://data_for_2025_1024_game')
    
    @patch('common.os.makedirs')
    @patch('common.sys.platform', 'linux')
    @patch('common.getpass.getuser', return_value='testuser')
    def test_get_base_dir_creates_directory(self, mock_getuser, mock_makedirs):
        base_dir = common.get_base_dir()
        
        mock_makedirs.assert_called_once_with('/user_data', exist_ok=True)
    
    @patch('common.sys.platform', 'darwin')
    @patch('common.getpass.getuser', return_value='unknownuser')
    def test_get_base_dir_darwin_unknown_user(self, mock_getuser):
        with self.assertRaises(UnboundLocalError):
            common.get_base_dir()


if __name__ == '__main__':
    unittest.main()
