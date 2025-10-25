import re
import jieba
from typing import List, Dict, Set
from collections import Counter


class CharacterManager:
    def __init__(self):
        self.characters = {}
        self.name_frequency = Counter()
        
    def extract_characters(self, text: str, min_frequency: int = 3) -> List[str]:
        chinese_name_pattern = r'[\\u4e00-\\u9fa5]{2,4}'
        potential_names = re.findall(chinese_name_pattern, text)
        
        self.name_frequency.update(potential_names)
        
        main_characters = [name for name, count in self.name_frequency.items() 
                          if count >= min_frequency and len(name) >= 2]
        
        main_characters = self._filter_common_words(main_characters)
        
        return sorted(main_characters, key=lambda x: self.name_frequency[x], reverse=True)
    
    def _filter_common_words(self, names: List[str]) -> List[str]:
        common_words = {
            '这个', '那个', '什么', '怎么', '为什么', '可以', '不是', '是的',
            '但是', '然而', '因为', '所以', '如果', '虽然', '而且', '或者',
            '自己', '我们', '他们', '她们', '它们', '大家', '人们', '东西',
            '地方', '时候', '现在', '之前', '以后', '一直', '已经', '还是'
        }
        return [name for name in names if name not in common_words]
    
    def register_character(self, name: str, description: str = "", 
                          appearance: Dict = None, image_seed: int = None, 
                          character_tag: str = None):
        if name not in self.characters:
            tag = character_tag or f"<{name}>"
            self.characters[name] = {
                'name': name,
                'description': description,
                'appearance': appearance or {},
                'image_seed': image_seed or hash(name) % 1000000,
                'appearances': [],
                'character_tag': tag,
                'appearance_count': 0
            }
    
    def get_character(self, name: str) -> Dict:
        return self.characters.get(name, None)
    
    def get_all_characters(self) -> List[Dict]:
        return list(self.characters.values())
    
    def update_character_appearance(self, name: str, appearance_description: str):
        if name in self.characters:
            if 'appearance_descriptions' not in self.characters[name]:
                self.characters[name]['appearance_descriptions'] = []
            self.characters[name]['appearance_descriptions'].append(appearance_description)
    
    def get_character_prompt(self, name: str, include_consistency_hints: bool = True) -> str:
        char = self.get_character(name)
        if not char:
            return f"character: {name}"
        
        tag = char.get('character_tag', f"<{name}>")
        appearance_count = char.get('appearance_count', 0)
        
        prompt_parts = []
        
        prompt_parts.append(f"character: {tag}")
        
        if char.get('description'):
            prompt_parts.append(char['description'])
        
        if char.get('appearance'):
            appearance = char['appearance']
            appearance_desc = ', '.join(f"{v}" for k, v in appearance.items())
            prompt_parts.append(appearance_desc)
        
        if include_consistency_hints:
            if appearance_count > 0:
                prompt_parts.append(f"same character design as previous scenes")
                prompt_parts.append(f"identical face and outfit")
                prompt_parts.append(f"continuity maintained")
            
            prompt_parts.append("anime style")
            prompt_parts.append("consistent character design")
            prompt_parts.append("same outfit")
            prompt_parts.append("same hairstyle")
            prompt_parts.append("same proportions")
        
        return ', '.join(prompt_parts)
    
    def increment_appearance_count(self, name: str):
        if name in self.characters:
            self.characters[name]['appearance_count'] = self.characters[name].get('appearance_count', 0) + 1
    
    def get_character_seed(self, name: str) -> int:
        char = self.get_character(name)
        if char:
            return char.get('image_seed', hash(name) % 1000000)
        return hash(name) % 1000000
