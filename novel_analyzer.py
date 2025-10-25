import os
from openai import OpenAI
from typing import Dict, List
import json


class NovelAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openai.qiniu.com/v1"
        )
        self.model = "deepseek/deepseek-v3.1-terminus"
    
    def analyze_novel_text(self, text: str, max_chunk_size: int = 2000) -> Dict:
        chunks = self._split_text_into_chunks(text, max_chunk_size)
        
        all_scenes = []
        all_characters = {}
        
        for i, chunk in enumerate(chunks):
            print(f"分析文本块 {i + 1}/{len(chunks)}...")
            analysis = self._analyze_chunk(chunk)
            
            if analysis:
                if 'scenes' in analysis:
                    all_scenes.extend(analysis['scenes'])
                if 'characters' in analysis:
                    for char_name, char_info in analysis['characters'].items():
                        if char_name not in all_characters:
                            all_characters[char_name] = char_info
                        else:
                            if 'appearance' in char_info and char_info['appearance']:
                                all_characters[char_name]['appearance'] = char_info['appearance']
                            if 'personality' in char_info and char_info['personality']:
                                all_characters[char_name]['personality'] = char_info['personality']
        
        return {
            'scenes': all_scenes,
            'characters': all_characters
        }
    
    def _split_text_into_chunks(self, text: str, max_size: int) -> List[str]:
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            end_pos = min(current_pos + max_size, len(text))
            
            if end_pos < len(text):
                for delimiter in ['。', '\n', '，', ' ']:
                    last_delim = text.rfind(delimiter, current_pos, end_pos)
                    if last_delim > current_pos:
                        end_pos = last_delim + 1
                        break
            
            chunks.append(text[current_pos:end_pos])
            current_pos = end_pos
        
        return chunks
    
    def _analyze_chunk(self, text: str) -> Dict:
        prompt = f"""请分析以下小说文本，提取结构化信息：

小说文本：
{text}

请以 JSON 格式返回以下信息：
{{
  "scenes": [
    {{
      "description": "场景描述",
      "location": "地点",
      "time": "时间",
      "characters": ["角色1", "角色2"],
      "dialogues": [
        {{"character": "角色名", "content": "对话内容"}}
      ],
      "narration": "叙述描述",
      "storyboard_shots": [
        {{"shot_type": "镜头类型(如特写/全景/中景)", "description": "镜头描述", "focus": "焦点内容"}}
      ]
    }}
  ],
  "characters": {{
    "角色名": {{
      "appearance": "外貌描述",
      "personality": "性格特征"
    }}
  }}
}}

注意：
1. 提取所有明确的场景信息
2. 识别出现的角色及其外貌和性格
3. 记录角色之间的对话
4. 为每个场景生成 3-5 个不同的分镜镜头描述，用于后续生成多张场景图片
5. 分镜镜头应该包含不同的视角和焦点，如：特写、中景、全景、过肩镜头等

只返回 JSON，不要其他解释。"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的小说分析助手，擅长提取小说中的结构化信息并生成分镜脚本。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7
            )
            
            content = response.choices[0].message.content.strip()
            
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            return result
            
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"响应内容: {content[:200]}...")
            return None
        except Exception as e:
            print(f"AI 分析失败: {e}")
            return None
    
    def generate_character_prompt(self, character_name: str, character_info: Dict) -> str:
        prompt_parts = [f"角色名称：{character_name}"]
        
        if character_info.get('appearance'):
            prompt_parts.append(f"外貌：{character_info['appearance']}")
        
        if character_info.get('personality'):
            prompt_parts.append(f"性格：{character_info['personality']}")
        
        return "，".join(prompt_parts)
    
    def generate_scene_prompt(self, scene_info: Dict, shot_info: Dict = None) -> str:
        prompt_parts = []
        
        if scene_info.get('location'):
            prompt_parts.append(f"地点：{scene_info['location']}")
        
        if scene_info.get('time'):
            prompt_parts.append(f"时间：{scene_info['time']}")
        
        if shot_info:
            prompt_parts.append(f"镜头类型：{shot_info.get('shot_type', '中景')}")
            prompt_parts.append(f"镜头描述：{shot_info.get('description', '')}")
            if shot_info.get('focus'):
                prompt_parts.append(f"焦点：{shot_info['focus']}")
        else:
            prompt_parts.append(f"场景：{scene_info.get('description', '')}")
        
        if scene_info.get('characters'):
            char_list = "、".join(scene_info['characters'])
            prompt_parts.append(f"角色：{char_list}")
        
        return "，".join(prompt_parts)
