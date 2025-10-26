import unittest
import sys
import os
from unittest.mock import patch, MagicMock
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scene_composer import SceneComposer


class TestSceneComposer(unittest.TestCase):
    
    def setUp(self):
        self.mock_image_gen = MagicMock()
        self.mock_tts_gen = MagicMock()
        self.mock_char_mgr = MagicMock()
        self.mock_video_gen = MagicMock()
    
    @patch('scene_composer.os.makedirs')
    def test_init_without_session_id(self, mock_makedirs):
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        self.assertEqual(composer.output_dir, "output_scenes")
        mock_makedirs.assert_called_once_with("output_scenes", exist_ok=True)
    
    @patch('scene_composer.os.makedirs')
    def test_init_with_session_id(self, mock_makedirs):
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr,
            session_id="test_session"
        )
        
        self.assertEqual(composer.output_dir, "output_scenes/test_session")
        self.assertEqual(composer.session_id, "test_session")
    
    def test_extract_characters_from_text(self):
        self.mock_char_mgr.get_all_characters.return_value = [
            {'name': '张三'}, {'name': '李四'}
        ]
        
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        text = "张三见到了李四，李四很高兴。"
        characters = composer._extract_characters_from_text(text)
        
        self.assertIn('张三', characters)
        self.assertIn('李四', characters)
    
    def test_generate_scene_description(self):
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        text = "这是一段场景文字"
        characters = ['张三', '李四']
        description = composer._generate_scene_description(text, characters)
        
        self.assertIn('张三', description)
        self.assertIn('李四', description)
        self.assertIn(text, description)
    
    @patch('scene_composer.os.makedirs')
    @patch('scene_composer.json.dump')
    @patch('builtins.open', new_callable=unittest.mock.mock_open)
    def test_save_metadata(self, mock_file, mock_json_dump, mock_makedirs):
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        metadata = {
            'scene_index': 0,
            'text': '测试文字',
            'description': '测试描述',
            'characters': ['张三'],
            'image_path': '/path/image.png',
            'audio_path': '/path/audio.mp3',
            'video_path': None
        }
        
        composer._save_metadata("/test/folder", metadata)
        
        mock_file.assert_called_once()
        mock_json_dump.assert_called_once()
    
    @patch('scene_composer.os.makedirs')
    @patch('scene_composer.shutil.copy')
    def test_create_scene_success(self, mock_copy, mock_makedirs):
        self.mock_char_mgr.get_all_characters.return_value = [{'name': '张三'}]
        self.mock_char_mgr.get_character.return_value = {'name': '张三'}
        self.mock_char_mgr.get_character_prompt.return_value = "角色提示"
        self.mock_char_mgr.get_character_seed.return_value = 12345
        
        self.mock_image_gen.generate_scene_image.return_value = "/path/scene_image.png"
        self.mock_image_gen.create_text_overlay.return_value = True
        
        self.mock_tts_gen.generate_speech_for_scene.return_value = "/path/audio.mp3"
        
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        result = composer.create_scene(0, "张三在家里。")
        
        self.assertIsNotNone(result)
        self.assertEqual(result['scene_index'], 0)
        self.assertEqual(result['text'], "张三在家里。")
        self.assertIsNotNone(result['image_path'])
    
    @patch('scene_composer.os.makedirs')
    def test_create_scene_with_ai_analysis(self, mock_makedirs):
        scene_info = {
            'narration': '这是旁白',
            'description': '场景描述',
            'characters': ['张三', '李四']
        }
        
        self.mock_char_mgr.get_character.return_value = {'name': '张三'}
        self.mock_char_mgr.get_character_prompt.return_value = "角色提示"
        self.mock_char_mgr.get_character_seed.return_value = 12345
        
        self.mock_image_gen.generate_scene_image.return_value = "/path/scene.png"
        self.mock_image_gen.create_text_overlay.return_value = True
        self.mock_tts_gen.generate_speech_for_scene.return_value = "/path/audio.mp3"
        
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        result = composer.create_scene_with_ai_analysis(0, scene_info)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['text'], '这是旁白')
    
    @patch('scene_composer.os.makedirs')
    def test_create_scenes_from_paragraphs(self, mock_makedirs):
        paragraphs = ["段落1", "段落2", ""]
        
        self.mock_char_mgr.get_all_characters.return_value = []
        self.mock_image_gen.generate_scene_image.return_value = "/path/scene.png"
        self.mock_image_gen.create_text_overlay.return_value = True
        self.mock_tts_gen.generate_speech_for_scene.return_value = "/path/audio.mp3"
        
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        scenes = composer.create_scenes_from_paragraphs(paragraphs)
        
        self.assertEqual(len(scenes), 2)
    
    @patch('scene_composer.os.makedirs')
    def test_create_scene_from_storyboard(self, mock_makedirs):
        panel_info = {
            'shot_type': '特写',
            'visual_description': '角色表情',
            'dialogue': [{'character': '张三', 'text': '你好'}],
            'narration': '旁白文字',
            'characters': ['张三'],
            'location': '教室',
            'mood': 'happy'
        }
        
        character_designs = {'张三': '黑发男子'}
        
        self.mock_char_mgr.get_character.return_value = {'name': '张三'}
        self.mock_char_mgr.get_character_prompt.return_value = "角色提示"
        self.mock_char_mgr.get_character_seed.return_value = 12345
        
        self.mock_image_gen.generate_scene_image.return_value = "/path/scene.png"
        self.mock_image_gen.create_text_overlay.return_value = True
        self.mock_tts_gen.generate_speech_for_scene.return_value = "/path/audio.mp3"
        
        composer = SceneComposer(
            self.mock_image_gen,
            self.mock_tts_gen,
            self.mock_char_mgr
        )
        
        result = composer.create_scene_from_storyboard(0, panel_info, character_designs)
        
        self.assertIsNotNone(result)
        self.assertEqual(result['shot_type'], '特写')
        self.assertEqual(result['mood'], 'happy')


if __name__ == '__main__':
    unittest.main()
