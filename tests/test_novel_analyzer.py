import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from novel_analyzer import NovelAnalyzer


class TestNovelAnalyzer(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
    
    @patch('novel_analyzer.OpenAI')
    def test_init(self, mock_openai):
        analyzer = NovelAnalyzer(self.api_key)
        
        self.assertEqual(analyzer.api_key, self.api_key)
        mock_openai.assert_called_once()
    
    @patch('novel_analyzer.OpenAI')
    def test_analyze_text_chunk_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"scenes": [], "characters": []}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        analyzer = NovelAnalyzer(self.api_key)
        result = analyzer._analyze_text_chunk("测试文本")
        
        self.assertIsNotNone(result)
        self.assertIn('scenes', result)
        self.assertIn('characters', result)
    
    @patch('novel_analyzer.OpenAI')
    def test_analyze_text_chunk_exception(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        analyzer = NovelAnalyzer(self.api_key)
        result = analyzer._analyze_text_chunk("测试文本")
        
        self.assertEqual(result, {'scenes': [], 'characters': []})
    
    @patch('novel_analyzer.OpenAI')
    def test_split_text_into_chunks(self, mock_openai):
        analyzer = NovelAnalyzer(self.api_key)
        
        short_text = "这是短文本"
        chunks = analyzer._split_text_into_chunks(short_text, chunk_size=1000)
        
        self.assertEqual(len(chunks), 1)
        self.assertEqual(chunks[0], short_text)
    
    @patch('novel_analyzer.OpenAI')
    def test_split_text_into_chunks_long_text(self, mock_openai):
        analyzer = NovelAnalyzer(self.api_key)
        
        long_text = "测试" * 1000
        chunks = analyzer._split_text_into_chunks(long_text, chunk_size=100)
        
        self.assertGreater(len(chunks), 1)
    
    @patch.object(NovelAnalyzer, '_analyze_text_chunk')
    @patch('novel_analyzer.OpenAI')
    def test_analyze_novel_in_chunks(self, mock_openai, mock_analyze):
        mock_analyze.return_value = {
            'scenes': [{'description': '场景1'}],
            'characters': [{'name': '张三'}]
        }
        
        analyzer = NovelAnalyzer(self.api_key)
        result = analyzer.analyze_novel_in_chunks("测试小说文本")
        
        self.assertIn('scenes', result)
        self.assertIn('characters', result)
    
    @patch('novel_analyzer.OpenAI')
    def test_generate_character_design_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"visual_keywords": "黑发男子"}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        analyzer = NovelAnalyzer(self.api_key)
        char_info = {'name': '张三', 'personality': '勇敢', 'appearance': '高大'}
        result = analyzer.generate_character_design(char_info)
        
        self.assertIsNotNone(result)
        self.assertIn('visual_keywords', result)
    
    @patch('novel_analyzer.OpenAI')
    def test_generate_character_appearance_prompt(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "黑发蓝眼的年轻男子"
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        analyzer = NovelAnalyzer(self.api_key)
        char_info = {'name': '李四', 'appearance': '英俊'}
        result = analyzer.generate_character_appearance_prompt(char_info)
        
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
