import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from character_manager import CharacterManager


class TestCharacterManager(unittest.TestCase):
    
    def setUp(self):
        self.manager = CharacterManager()
    
    def test_extract_characters_basic(self):
        text = "张三去找李四。李四说张三你好。张三回答李四。张三很高兴。"
        characters = self.manager.extract_characters(text, min_frequency=3)
        
        self.assertIn('张三', characters)
        self.assertEqual(self.manager.name_frequency['张三'], 4)
    
    def test_extract_characters_with_frequency_threshold(self):
        text = "张三说话。李四说话。王五出现了一次。张三又说话。李四也说话。张三李四。"
        characters = self.manager.extract_characters(text, min_frequency=3)
        
        self.assertIn('张三', characters)
        self.assertIn('李四', characters)
        self.assertNotIn('王五', characters)
    
    def test_extract_characters_filters_common_words(self):
        text = "这个人说什么。那个人说怎么。张三说可以。李四说不是。"
        characters = self.manager.extract_characters(text, min_frequency=1)
        
        self.assertNotIn('这个', characters)
        self.assertNotIn('什么', characters)
        self.assertNotIn('那个', characters)
    
    def test_extract_characters_sorted_by_frequency(self):
        text = "张三张三张三张三。李四李四李四。王五王五。"
        characters = self.manager.extract_characters(text, min_frequency=2)
        
        self.assertEqual(characters[0], '张三')
        self.assertEqual(characters[1], '李四')
        self.assertEqual(characters[2], '王五')
    
    def test_extract_characters_empty_text(self):
        text = ""
        characters = self.manager.extract_characters(text)
        
        self.assertEqual(len(characters), 0)
    
    def test_extract_characters_no_names(self):
        text = "这是一段没有人名的文本。只有一些普通的词语。"
        characters = self.manager.extract_characters(text, min_frequency=1)
        
        self.assertEqual(len(characters), 0)
    
    def test_extract_characters_min_length(self):
        text = "张张张张。李李李李。张三张三张三。"
        characters = self.manager.extract_characters(text, min_frequency=3)
        
        self.assertIn('张三', characters)
        self.assertEqual(len(characters), 1)
    
    def test_register_character_basic(self):
        self.manager.register_character("张三", "主角")
        
        char = self.manager.get_character("张三")
        self.assertIsNotNone(char)
        self.assertEqual(char['name'], '张三')
        self.assertEqual(char['description'], '主角')
    
    def test_register_character_with_appearance(self):
        appearance = {'hair': '黑色', 'eyes': '棕色'}
        self.manager.register_character("李四", "配角", appearance=appearance)
        
        char = self.manager.get_character("李四")
        self.assertEqual(char['appearance'], appearance)
    
    def test_register_character_with_custom_seed(self):
        self.manager.register_character("王五", image_seed=12345)
        
        char = self.manager.get_character("王五")
        self.assertEqual(char['image_seed'], 12345)
    
    def test_register_character_default_seed(self):
        self.manager.register_character("赵六")
        
        char = self.manager.get_character("赵六")
        self.assertIsNotNone(char['image_seed'])
        self.assertIsInstance(char['image_seed'], int)
    
    def test_register_character_duplicate(self):
        self.manager.register_character("张三", "描述1")
        self.manager.register_character("张三", "描述2")
        
        char = self.manager.get_character("张三")
        self.assertEqual(char['description'], '描述1')
    
    def test_get_character_not_exists(self):
        char = self.manager.get_character("不存在")
        
        self.assertIsNone(char)
    
    def test_get_all_characters_empty(self):
        characters = self.manager.get_all_characters()
        
        self.assertEqual(len(characters), 0)
    
    def test_get_all_characters_multiple(self):
        self.manager.register_character("张三")
        self.manager.register_character("李四")
        self.manager.register_character("王五")
        
        characters = self.manager.get_all_characters()
        
        self.assertEqual(len(characters), 3)
        names = [c['name'] for c in characters]
        self.assertIn('张三', names)
        self.assertIn('李四', names)
        self.assertIn('王五', names)
    
    def test_update_character_appearance(self):
        self.manager.register_character("张三")
        self.manager.update_character_appearance("张三", "穿着黑衣")
        self.manager.update_character_appearance("张三", "戴着帽子")
        
        char = self.manager.get_character("张三")
        self.assertIn('appearance_descriptions', char)
        self.assertEqual(len(char['appearance_descriptions']), 2)
        self.assertIn("穿着黑衣", char['appearance_descriptions'])
    
    def test_update_character_appearance_not_exists(self):
        self.manager.update_character_appearance("不存在", "描述")
        
        char = self.manager.get_character("不存在")
        self.assertIsNone(char)
    
    def test_get_character_prompt_basic(self):
        self.manager.register_character("张三", "主角")
        
        prompt = self.manager.get_character_prompt("张三")
        
        self.assertIn("张三", prompt)
        self.assertIn("主角", prompt)
    
    def test_get_character_prompt_with_appearance(self):
        appearance = {'hair': '黑色', 'eyes': '棕色'}
        self.manager.register_character("李四", "配角", appearance=appearance)
        
        prompt = self.manager.get_character_prompt("李四")
        
        self.assertIn("李四", prompt)
        self.assertIn("hair: 黑色", prompt)
        self.assertIn("eyes: 棕色", prompt)
    
    def test_get_character_prompt_not_exists(self):
        prompt = self.manager.get_character_prompt("不存在")
        
        self.assertEqual(prompt, "角色：不存在")
    
    def test_character_has_default_fields(self):
        self.manager.register_character("张三")
        
        char = self.manager.get_character("张三")
        
        self.assertIn('name', char)
        self.assertIn('description', char)
        self.assertIn('appearance', char)
        self.assertIn('image_seed', char)
        self.assertIn('appearances', char)
    
    def test_extract_characters_four_char_names(self):
        text = "欧阳锋说话。欧阳锋很厉害。欧阳锋出现了。欧阳锋最强。"
        characters = self.manager.extract_characters(text, min_frequency=3)
        
        self.assertIn('欧阳锋', characters)
    
    def test_filter_common_words_comprehensive(self):
        filtered = self.manager._filter_common_words(['张三', '这个', '李四', '什么', '王五'])
        
        self.assertIn('张三', filtered)
        self.assertIn('李四', filtered)
        self.assertIn('王五', filtered)
        self.assertNotIn('这个', filtered)
        self.assertNotIn('什么', filtered)


if __name__ == '__main__':
    unittest.main()
