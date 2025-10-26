import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import web_app


class TestWebApp(unittest.TestCase):
    
    def setUp(self):
        web_app.app.config['TESTING'] = True
        self.client = web_app.app.test_client()
    
    def test_index_route(self):
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
    
    def test_login_page_route(self):
        response = self.client.get('/login')
        
        self.assertEqual(response.status_code, 200)
    
    def test_settings_route(self):
        response = self.client.get('/settings')
        
        self.assertEqual(response.status_code, 200)
    
    @patch('web_app.register_user')
    def test_register_api_success(self, mock_register):
        mock_register.return_value = (True, '注册成功')
        
        response = self.client.post('/api/register',
                                    json={'username': 'testuser', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '注册成功')
    
    @patch('web_app.register_user')
    def test_register_api_failure(self, mock_register):
        mock_register.return_value = (False, '用户名已存在')
        
        response = self.client.post('/api/register',
                                    json={'username': 'existing', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 400)
        data = response.get_json()
        self.assertEqual(data['error'], '用户名已存在')
    
    @patch('web_app.login_user')
    def test_login_api_success(self, mock_login):
        mock_login.return_value = (True, {'id': 1, 'username': 'testuser'}, '登录成功')
        
        response = self.client.post('/api/login',
                                    json={'username': 'testuser', 'password': 'password123'})
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '登录成功')
    
    @patch('web_app.login_user')
    def test_login_api_failure(self, mock_login):
        mock_login.return_value = (False, None, '用户名或密码错误')
        
        response = self.client.post('/api/login',
                                    json={'username': 'wronguser', 'password': 'wrongpass'})
        
        self.assertEqual(response.status_code, 401)
        data = response.get_json()
        self.assertEqual(data['error'], '用户名或密码错误')
    
    def test_logout_api(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
        
        response = self.client.post('/api/logout')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['message'], '已退出登录')
    
    def test_current_user_api_logged_in(self):
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
        
        with patch('web_app.get_user_by_id') as mock_get_user:
            mock_get_user.return_value = {'username': 'testuser'}
            
            response = self.client.get('/api/current_user')
            
            self.assertEqual(response.status_code, 200)
            data = response.get_json()
            self.assertIsNotNone(data['user'])
    
    def test_current_user_api_not_logged_in(self):
        response = self.client.get('/api/current_user')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsNone(data['user'])
    
    def test_allowed_file(self):
        self.assertTrue(web_app.allowed_file('test.txt'))
        self.assertFalse(web_app.allowed_file('test.pdf'))
        self.assertFalse(web_app.allowed_file('test'))
    
    def test_upload_novel_not_logged_in(self):
        response = self.client.post('/api/upload')
        
        self.assertEqual(response.status_code, 401)
    
    @patch('web_app.get_statistics')
    def test_get_history_api(self, mock_get_stats):
        mock_get_stats.return_value = [
            {'session_id': 'test1'},
            {'session_id': 'test2'}
        ]
        
        with self.client.session_transaction() as sess:
            sess['user_id'] = 1
            sess['username'] = 'testuser'
        
        response = self.client.get('/api/history')
        
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(len(data['history']), 2)
    
    def test_get_history_not_logged_in(self):
        response = self.client.get('/api/history')
        
        self.assertEqual(response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
