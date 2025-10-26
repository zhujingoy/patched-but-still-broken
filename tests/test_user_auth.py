import unittest
import sys
import os
import pymysql
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import user_auth


class TestUserAuth(unittest.TestCase):
    
    def setUp(self):
        self.test_db_config = {
            'host': os.getenv('TEST_DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('TEST_DB_PORT', 3306)),
            'user': os.getenv('TEST_DB_USER', 'root'),
            'password': os.getenv('TEST_DB_PASSWORD', ''),
            'database': os.getenv('TEST_DB_NAME', 'test_appdb'),
            'charset': 'utf8mb4'
        }
        
        try:
            conn = pymysql.connect(
                host=self.test_db_config['host'],
                port=self.test_db_config['port'],
                user=self.test_db_config['user'],
                password=self.test_db_config['password'],
                charset=self.test_db_config['charset']
            )
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.test_db_config['database']}")
            conn.close()
            
            from db_config import DB_CONFIG
            DB_CONFIG.update(self.test_db_config)
            
            user_auth.init_user_db()
            self._cleanup_test_data()
        except Exception as e:
            self.skipTest(f"Cannot connect to test database: {e}")
    
    def tearDown(self):
        self._cleanup_test_data()
    
    def _cleanup_test_data(self):
        try:
            with user_auth.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users")
                conn.commit()
        except:
            pass
    
    def test_hash_password(self):
        password = "testpassword123"
        hashed = user_auth.hash_password(password)
        
        self.assertIsNotNone(hashed)
        self.assertIsInstance(hashed, str)
        self.assertEqual(len(hashed), 192)
    
    def test_hash_password_different_for_same_input(self):
        password = "samepassword"
        hash1 = user_auth.hash_password(password)
        hash2 = user_auth.hash_password(password)
        
        self.assertNotEqual(hash1, hash2)
    
    def test_verify_password_correct(self):
        password = "mypassword"
        hashed = user_auth.hash_password(password)
        
        result = user_auth.verify_password(hashed, password)
        
        self.assertTrue(result)
    
    def test_verify_password_incorrect(self):
        password = "correctpass"
        wrong_password = "wrongpass"
        hashed = user_auth.hash_password(password)
        
        result = user_auth.verify_password(hashed, wrong_password)
        
        self.assertFalse(result)
    
    def test_register_user_success(self):
        success, message = user_auth.register_user('testuser', 'password123')
        
        self.assertTrue(success)
        self.assertEqual(message, '注册成功')
    
    def test_register_user_empty_username(self):
        success, message = user_auth.register_user('', 'password123')
        
        self.assertFalse(success)
        self.assertEqual(message, '用户名和密码不能为空')
    
    def test_register_user_empty_password(self):
        success, message = user_auth.register_user('testuser', '')
        
        self.assertFalse(success)
        self.assertEqual(message, '用户名和密码不能为空')
    
    def test_register_user_short_username(self):
        success, message = user_auth.register_user('ab', 'password123')
        
        self.assertFalse(success)
        self.assertEqual(message, '用户名至少需要3个字符')
    
    def test_register_user_short_password(self):
        success, message = user_auth.register_user('testuser', '12345')
        
        self.assertFalse(success)
        self.assertEqual(message, '密码至少需要6个字符')
    
    def test_register_user_duplicate(self):
        user_auth.register_user('duplicateuser', 'password123')
        success, message = user_auth.register_user('duplicateuser', 'password456')
        
        self.assertFalse(success)
        self.assertEqual(message, '用户名已存在')
    
    def test_login_user_success(self):
        user_auth.register_user('loginuser', 'password123')
        
        success, user, message = user_auth.login_user('loginuser', 'password123')
        
        self.assertTrue(success)
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'loginuser')
        self.assertEqual(message, '登录成功')
    
    def test_login_user_wrong_password(self):
        user_auth.register_user('loginuser2', 'password123')
        
        success, user, message = user_auth.login_user('loginuser2', 'wrongpassword')
        
        self.assertFalse(success)
        self.assertIsNone(user)
        self.assertEqual(message, '用户名或密码错误')
    
    def test_login_user_nonexistent(self):
        success, user, message = user_auth.login_user('nonexistent', 'password123')
        
        self.assertFalse(success)
        self.assertIsNone(user)
        self.assertEqual(message, '用户名或密码错误')
    
    def test_login_user_empty_credentials(self):
        success, user, message = user_auth.login_user('', '')
        
        self.assertFalse(success)
        self.assertIsNone(user)
        self.assertEqual(message, '用户名和密码不能为空')
    
    def test_get_user_by_id(self):
        user_auth.register_user('getuser', 'password123')
        success, user_data, _ = user_auth.login_user('getuser', 'password123')
        
        user = user_auth.get_user_by_id(user_data['id'])
        
        self.assertIsNotNone(user)
        self.assertEqual(user['username'], 'getuser')
        self.assertIn('created_at', user)
    
    def test_get_user_by_id_nonexistent(self):
        user = user_auth.get_user_by_id(99999)
        
        self.assertIsNone(user)
    
    def test_get_user_video_count(self):
        user_auth.register_user('videouser', 'password123')
        success, user_data, _ = user_auth.login_user('videouser', 'password123')
        
        count = user_auth.get_user_video_count(user_data['id'])
        
        self.assertEqual(count, 0)
    
    def test_increment_user_video_count(self):
        user_auth.register_user('incrementuser', 'password123')
        success, user_data, _ = user_auth.login_user('incrementuser', 'password123')
        
        result = user_auth.increment_user_video_count(user_data['id'])
        
        self.assertTrue(result)
        
        count = user_auth.get_user_video_count(user_data['id'])
        self.assertEqual(count, 1)
    
    def test_increment_user_video_count_multiple(self):
        user_auth.register_user('multiuser', 'password123')
        success, user_data, _ = user_auth.login_user('multiuser', 'password123')
        
        for _ in range(3):
            user_auth.increment_user_video_count(user_data['id'])
        
        count = user_auth.get_user_video_count(user_data['id'])
        self.assertEqual(count, 3)


if __name__ == '__main__':
    unittest.main()
