import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from storyboard_generator import StoryboardGenerator


class TestStoryboardGenerator(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
    
    @patch('storyboard_generator.OpenAI')
    def test_init(self, mock_openai):
        generator = StoryboardGenerator(self.api_key)
        
        self.assertEqual(generator.api_key, self.api_key)
        mock_openai.assert_called_once()
    
    @patch('storyboard_generator.OpenAI')
    def test_generate_storyboard_chunk_success(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = '{"storyboard": []}'
        mock_response.choices = [mock_choice]
        mock_client.chat.completions.create.return_value = mock_response
        
        generator = StoryboardGenerator(self.api_key)
        result = generator._generate_storyboard_chunk("测试文本", [])
        
        self.assertIsNotNone(result)
        self.assertIn('storyboard', result)
    
    @patch('storyboard_generator.OpenAI')
    def test_generate_storyboard_chunk_exception(self, mock_openai):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        
        generator = StoryboardGenerator(self.api_key)
        result = generator._generate_storyboard_chunk("测试文本", [])
        
        self.assertEqual(result, {'storyboard': []})
    
    @patch('storyboard_generator.OpenAI')
    def test_split_text_into_chunks(self, mock_openai):
        generator = StoryboardGenerator(self.api_key)
        
        text = "这是测试文本"
        chunks = generator._split_text_into_chunks(text, chunk_size=1000)
        
        self.assertEqual(len(chunks), 1)
    
    @patch.object(StoryboardGenerator, '_generate_storyboard_chunk')
    @patch('storyboard_generator.OpenAI')
    def test_generate_storyboard_in_chunks(self, mock_openai, mock_gen_chunk):
        mock_gen_chunk.return_value = {
            'storyboard': [
                {'panel_number': 1, 'shot_type': '特写'}
            ]
        }
        
        generator = StoryboardGenerator(self.api_key)
        result = generator.generate_storyboard_in_chunks("测试小说", [])
        
        self.assertIn('storyboard', result)
        self.assertIn('success_count', result)
        self.assertIn('failure_count', result)
    
    @patch.object(StoryboardGenerator, '_generate_storyboard_chunk')
    @patch('storyboard_generator.OpenAI')
    def test_generate_storyboard_with_retry(self, mock_openai, mock_gen_chunk):
        mock_gen_chunk.side_effect = [
            {'storyboard': []},
            {'storyboard': [{'panel_number': 1}]}
        ]
        
        generator = StoryboardGenerator(self.api_key)
        result = generator.generate_storyboard_in_chunks("测试文本", [], max_chunks=1)
        
        self.assertIn('storyboard', result)


if __name__ == '__main__':
    unittest.main()
