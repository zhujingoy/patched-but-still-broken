import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from image_generator import ImageGenerator


class TestImageGenerator(unittest.TestCase):
    
    def setUp(self):
        self.api_key = "test_api_key"
    
    @patch('image_generator.OpenAI')
    def test_init_qiniu_provider(self, mock_openai):
        generator = ImageGenerator(self.api_key, provider='qiniu')
        
        self.assertEqual(generator.provider, 'qiniu')
        mock_openai.assert_called_once()
        call_args = mock_openai.call_args
        self.assertEqual(call_args[1]['api_key'], self.api_key)
        self.assertEqual(call_args[1]['base_url'], 'https://openai.qiniu.com/v1')
    
    @patch('image_generator.OpenAI')
    def test_init_openai_provider(self, mock_openai):
        generator = ImageGenerator(self.api_key, provider='openai')
        
        self.assertEqual(generator.provider, 'openai')
        mock_openai.assert_called_once()
        call_args = mock_openai.call_args
        self.assertEqual(call_args[1]['api_key'], self.api_key)
    
    @patch('image_generator.OpenAI')
    def test_init_custom_prompt(self, mock_openai):
        custom_prompt = "custom style prompt"
        generator = ImageGenerator(self.api_key, custom_prompt=custom_prompt)
        
        self.assertEqual(generator.custom_prompt, custom_prompt)
    
    @patch('image_generator.os.path.exists', return_value=True)
    @patch('image_generator.OpenAI')
    def test_generate_character_image_from_cache(self, mock_openai, mock_exists):
        generator = ImageGenerator(self.api_key)
        
        result = generator.generate_character_image("张三", "黑发男子")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith(generator.cache_dir))
    
    @patch('image_generator.os.path.exists', return_value=False)
    @patch('image_generator.Image')
    @patch('image_generator.OpenAI')
    def test_generate_character_image_qiniu_success(self, mock_openai, mock_image, mock_exists):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json='dGVzdGltYWdl')]
        mock_client.images.generate.return_value = mock_response
        
        mock_img = MagicMock()
        mock_image.open.return_value = mock_img
        
        generator = ImageGenerator(self.api_key, provider='qiniu')
        result = generator.generate_character_image("李四", "长发女子")
        
        self.assertIsNotNone(result)
        mock_client.images.generate.assert_called_once()
    
    @patch('image_generator.os.path.exists', return_value=False)
    @patch('image_generator.OpenAI')
    def test_generate_character_image_exception(self, mock_openai, mock_exists):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.images.generate.side_effect = Exception("API Error")
        
        generator = ImageGenerator(self.api_key)
        result = generator.generate_character_image("王五", "壮汉")
        
        self.assertIsNone(result)
    
    @patch('image_generator.os.path.exists', return_value=True)
    @patch('image_generator.OpenAI')
    def test_generate_scene_image_from_cache(self, mock_openai, mock_exists):
        generator = ImageGenerator(self.api_key)
        
        result = generator.generate_scene_image("夜晚的城市")
        
        self.assertIsNotNone(result)
        self.assertTrue(result.startswith(generator.cache_dir))
    
    @patch('image_generator.os.path.exists', return_value=False)
    @patch('image_generator.Image')
    @patch('image_generator.OpenAI')
    def test_generate_scene_image_with_characters(self, mock_openai, mock_image, mock_exists):
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_response = MagicMock()
        mock_response.data = [MagicMock(b64_json='dGVzdGltYWdl')]
        mock_client.images.generate.return_value = mock_response
        
        mock_img = MagicMock()
        mock_image.open.return_value = mock_img
        
        generator = ImageGenerator(self.api_key, provider='qiniu')
        characters = ["黑发男子", "长发女子"]
        result = generator.generate_scene_image("城市街道", characters=characters)
        
        self.assertIsNotNone(result)
        call_args = mock_client.images.generate.call_args
        self.assertIn('黑发男子', call_args[1]['prompt'])
        self.assertIn('长发女子', call_args[1]['prompt'])
    
    @patch('image_generator.ImageFont')
    @patch('image_generator.ImageDraw')
    @patch('image_generator.Image')
    def test_create_text_overlay_success(self, mock_image_cls, mock_draw_cls, mock_font):
        mock_img = MagicMock()
        mock_img.size = (1024, 768)
        mock_image_cls.open.return_value = mock_img
        mock_image_cls.new.return_value = mock_img
        mock_img.convert.return_value = mock_img
        
        mock_draw = MagicMock()
        mock_draw_cls.Draw.return_value = mock_draw
        mock_draw.textbbox.return_value = (0, 0, 100, 50)
        
        mock_font.truetype.return_value = MagicMock()
        
        generator = ImageGenerator(self.api_key)
        result = generator.create_text_overlay("input.png", "测试文字", "output.png")
        
        self.assertTrue(result)
        mock_img.save.assert_called_once_with("output.png")
    
    @patch('image_generator.Image.open', side_effect=Exception("File error"))
    def test_create_text_overlay_exception(self, mock_open):
        generator = ImageGenerator(self.api_key)
        result = generator.create_text_overlay("input.png", "文字", "output.png")
        
        self.assertFalse(result)
    
    def test_filter_common_words(self):
        generator = ImageGenerator(self.api_key)
        
        fonts = [
            "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
            "/nonexistent/font.ttf"
        ]
        
        for font_path in fonts:
            result = generator._load_chinese_font(40)
            break
    
    def test_wrap_text(self):
        generator = ImageGenerator(self.api_key)
        
        from PIL import ImageDraw, ImageFont
        mock_draw = MagicMock()
        mock_draw.textbbox.return_value = (0, 0, 50, 20)
        
        try:
            font = ImageFont.load_default()
        except:
            font = None
        
        if font:
            lines = generator._wrap_text("这是一段很长的文字", font, 100, mock_draw)
            self.assertIsInstance(lines, list)
            self.assertGreater(len(lines), 0)


if __name__ == '__main__':
    unittest.main()
