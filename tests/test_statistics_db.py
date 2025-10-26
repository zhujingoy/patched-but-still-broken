import unittest
import sys
import os
import pymysql
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import statistics_db

class TestStatisticsDB(unittest.TestCase):
    
    def setUp(self):
        self.test_db_config = {
            'host': os.getenv('TEST_DB_HOST', '127.0.0.1'),
            'port': int(os.getenv('TEST_DB_PORT', 3306)),
            'user': os.getenv('TEST_DB_USER', 'root'),
            'password': os.getenv('TEST_DB_PASSWORD', ''),
            'database': os.getenv('TEST_DB_NAME', 'test_appdb'),
            'charset': 'utf8mb4'
        }
        
        original_config = statistics_db.DB_CONFIG.copy()
        statistics_db.DB_CONFIG.update(self.test_db_config)
        
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
        except Exception as e:
            statistics_db.DB_CONFIG.update(original_config)
            self.skipTest(f"Cannot connect to test database: {e}")
        
        statistics_db.init_db()
        self._cleanup_test_data()
    
    def tearDown(self):
        self._cleanup_test_data()
    
    def _cleanup_test_data(self):
        try:
            with statistics_db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM generation_statistics")
                conn.commit()
        except:
            pass
    
    def test_init_db_creates_table(self):
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SHOW TABLES LIKE 'generation_statistics'")
            result = cursor.fetchone()
            
            self.assertIsNotNone(result)
    
    def test_init_db_table_structure(self):
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DESCRIBE generation_statistics")
            columns = cursor.fetchall()
            
            column_names = [col[0] for col in columns]
            
            self.assertIn('id', column_names)
            self.assertIn('session_id', column_names)
            self.assertIn('client_address', column_names)
            self.assertIn('upload_file_count', column_names)
            self.assertIn('upload_text_chars', column_names)
            self.assertIn('upload_content_size', column_names)
            self.assertIn('generated_scene_count', column_names)
            self.assertIn('generated_content_size', column_names)
            self.assertIn('created_at', column_names)
    
    def test_insert_statistics_basic(self):
        row_id = statistics_db.insert_statistics(
            session_id='test-session-1',
            client_address='127.0.0.1',
            upload_file_count=1,
            upload_text_chars=1000,
            upload_content_size=2048
        )
        
        self.assertIsNotNone(row_id)
        self.assertGreater(row_id, 0)
    
    def test_insert_statistics_multiple(self):
        row_id1 = statistics_db.insert_statistics('session-1', '127.0.0.1', 1, 100, 200)
        row_id2 = statistics_db.insert_statistics('session-2', '127.0.0.2', 2, 200, 400)
        
        self.assertNotEqual(row_id1, row_id2)
    
    def test_insert_statistics_zero_values(self):
        row_id = statistics_db.insert_statistics('session-0', '0.0.0.0', 0, 0, 0)
        
        self.assertIsNotNone(row_id)
    
    def test_insert_statistics_large_values(self):
        row_id = statistics_db.insert_statistics(
            'session-large',
            '192.168.1.1',
            1000,
            999999999,
            999999999
        )
        
        self.assertIsNotNone(row_id)
    
    def test_update_generation_stats(self):
        statistics_db.insert_statistics('session-update', '127.0.0.1', 1, 100, 200)
        
        statistics_db.update_generation_stats('session-update', 10, 5000)
        
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT generated_scene_count, generated_content_size FROM generation_statistics WHERE session_id = %s', 
                         ('session-update',))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 10)
            self.assertEqual(result[1], 5000)
    
    def test_update_generation_stats_non_existent(self):
        statistics_db.update_generation_stats('non-existent', 5, 1000)
        
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM generation_statistics WHERE session_id = %s', ('non-existent',))
            result = cursor.fetchone()
            
            self.assertIsNone(result)
    
    def test_update_generation_stats_zero_values(self):
        statistics_db.insert_statistics('session-zero', '127.0.0.1', 1, 100, 200)
        
        statistics_db.update_generation_stats('session-zero', 0, 0)
        
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT generated_scene_count FROM generation_statistics WHERE session_id = %s', 
                         ('session-zero',))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 0)
    
    def test_get_statistics_by_session_id(self):
        statistics_db.insert_statistics('session-get', '127.0.0.1', 2, 500, 1000)
        
        stats = statistics_db.get_statistics('session-get')
        
        self.assertIsNotNone(stats)
        self.assertEqual(stats['session_id'], 'session-get')
        self.assertEqual(stats['upload_file_count'], 2)
    
    def test_get_statistics_non_existent_session(self):
        stats = statistics_db.get_statistics('non-existent-session')
        
        self.assertIsNone(stats)
    
    def test_get_statistics_all_records(self):
        statistics_db.insert_statistics('session-1', '127.0.0.1', 1, 100, 200)
        statistics_db.insert_statistics('session-2', '127.0.0.2', 2, 200, 400)
        statistics_db.insert_statistics('session-3', '127.0.0.3', 3, 300, 600)
        
        stats = statistics_db.get_statistics()
        
        self.assertEqual(len(stats), 3)
    
    def test_get_statistics_empty_database(self):
        stats = statistics_db.get_statistics()
        
        self.assertEqual(len(stats), 0)
    
    def test_get_statistics_ordered_by_created_at(self):
        statistics_db.insert_statistics('session-1', '127.0.0.1', 1, 100, 200)
        statistics_db.insert_statistics('session-2', '127.0.0.2', 2, 200, 400)
        
        stats = statistics_db.get_statistics()
        
        self.assertEqual(stats[0]['session_id'], 'session-2')
        self.assertEqual(stats[1]['session_id'], 'session-1')
    
    def test_get_db_connection_context_manager(self):
        with statistics_db.get_db_connection() as conn:
            self.assertIsNotNone(conn)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            self.assertEqual(result[0], 1)
    
    def test_default_values_on_insert(self):
        statistics_db.insert_statistics('session-defaults', '127.0.0.1', 1, 100, 200)
        
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT generated_scene_count, generated_content_size FROM generation_statistics WHERE session_id = %s',
                         ('session-defaults',))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 0)
            self.assertEqual(result[1], 0)
    
    def test_insert_statistics_special_characters_in_session_id(self):
        special_id = "session-!@#$%^&*()"
        row_id = statistics_db.insert_statistics(special_id, '127.0.0.1', 1, 100, 200)
        
        self.assertIsNotNone(row_id)
    
    def test_insert_statistics_unicode_session_id(self):
        unicode_id = "会话-中文-123"
        row_id = statistics_db.insert_statistics(unicode_id, '127.0.0.1', 1, 100, 200)
        
        self.assertIsNotNone(row_id)
        stats = statistics_db.get_statistics(unicode_id)
        self.assertEqual(stats['session_id'], unicode_id)
    
    def test_multiple_updates_same_session(self):
        statistics_db.insert_statistics('session-multi', '127.0.0.1', 1, 100, 200)
        
        statistics_db.update_generation_stats('session-multi', 5, 1000)
        statistics_db.update_generation_stats('session-multi', 10, 2000)
        statistics_db.update_generation_stats('session-multi', 15, 3000)
        
        with statistics_db.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT generated_scene_count FROM generation_statistics WHERE session_id = %s',
                         ('session-multi',))
            result = cursor.fetchone()
            
            self.assertEqual(result[0], 15)


if __name__ == '__main__':
    unittest.main()
