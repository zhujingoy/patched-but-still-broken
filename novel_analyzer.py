from openai import OpenAI
from typing import Dict, List
import json


class NovelAnalyzer:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openai.qiniu.com/v1"
        )
        self.model = "deepseek-chat"
    
    def analyze_novel_text(self, text: str) -> Dict:
        system_prompt = """你是一个专业的小说分析助手。请分析输入的小说文本，提取以下信息：
1. 场景(Scene)：识别文本中的不同场景，包括场景描述、地点、时间等
2. 人物(Characters)：识别所有出现的人物，包括主要角色和次要角色，提取人物的外貌、性格特征
3. 对话(Dialogues)：提取人物之间的对话内容
4. 叙述(Narration)：提取旁白和描述性文本

请以JSON格式返回结果，格式如下：
{
  "scenes": [
    {
      "scene_number": 1,
      "description": "场景描述",
      "location": "地点",
      "time": "时间",
      "characters": ["出现的角色"],
      "narration": "场景叙述文本",
      "dialogues": [
        {"character": "角色名", "text": "对话内容"}
      ]
    }
  ],
  "characters": [
    {
      "name": "角色名",
      "appearance": "外貌描述",
      "personality": "性格特征",
      "role": "主要角色/次要角色"
    }
  ]
}"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下小说文本：\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            result_text = response.choices[0].message.content
            
            result_text = result_text.strip()
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.startswith("```"):
                result_text = result_text[3:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            try:
                result = json.loads(result_text)
            except json.JSONDecodeError:
                result = self._parse_fallback(result_text)
            
            return result
            
        except Exception as e:
            print(f"AI分析失败: {e}")
            return self._create_empty_result()
    
    def generate_character_appearance_prompt(self, character_info: Dict) -> str:
        name = character_info.get('name', '')
        appearance = character_info.get('appearance', '')
        personality = character_info.get('personality', '')
        
        prompt_parts = []
        if name:
            prompt_parts.append(f"角色名：{name}")
        if appearance:
            prompt_parts.append(f"外貌：{appearance}")
        if personality:
            prompt_parts.append(f"性格：{personality}")
        
        if not prompt_parts:
            return name
        
        full_prompt = ", ".join(prompt_parts)
        full_prompt += ", 动漫风格, 角色立绘, 全身像, 高质量, 细节丰富, 一致的角色设计"
        
        return full_prompt
    
    def generate_scene_image_prompt(self, scene_info: Dict) -> str:
        description = scene_info.get('description', '')
        location = scene_info.get('location', '')
        characters = scene_info.get('characters', [])
        narration = scene_info.get('narration', '')
        
        prompt_parts = []
        
        if description:
            prompt_parts.append(description)
        elif narration:
            prompt_parts.append(narration[:200])
        
        if location:
            prompt_parts.append(f"地点：{location}")
        
        if characters:
            char_list = "、".join(characters)
            prompt_parts.append(f"角色：{char_list}")
        
        full_prompt = ", ".join(prompt_parts)
        full_prompt += ", 动漫风格场景, 高质量, 细节丰富的背景"
        
        return full_prompt
    
    def _parse_fallback(self, text: str) -> Dict:
        result = {
            "scenes": [{
                "scene_number": 1,
                "description": text[:200],
                "location": "",
                "time": "",
                "characters": [],
                "narration": text,
                "dialogues": []
            }],
            "characters": []
        }
        return result
    
    def _create_empty_result(self) -> Dict:
        return {
            "scenes": [],
            "characters": []
        }
    
    def split_text_into_chunks(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) + 1 <= max_chunk_size:
                if current_chunk:
                    current_chunk += "\n" + para
                else:
                    current_chunk = para
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = para
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def analyze_novel_in_chunks(self, text: str, max_chunks: int = None) -> Dict:
        chunks = self.split_text_into_chunks(text)
        
        if max_chunks:
            chunks = chunks[:max_chunks]
        
        all_scenes = []
        all_characters = {}
        scene_counter = 0
        
        for i, chunk in enumerate(chunks):
            print(f"分析文本块 {i+1}/{len(chunks)}...")
            
            chunk_result = self.analyze_novel_text(chunk)
            
            for scene in chunk_result.get('scenes', []):
                scene['scene_number'] = scene_counter
                scene_counter += 1
                all_scenes.append(scene)
            
            for char in chunk_result.get('characters', []):
                char_name = char.get('name', '')
                if char_name:
                    if char_name not in all_characters:
                        all_characters[char_name] = char
                    else:
                        existing = all_characters[char_name]
                        if not existing.get('appearance') and char.get('appearance'):
                            existing['appearance'] = char['appearance']
                        if not existing.get('personality') and char.get('personality'):
                            existing['personality'] = char['personality']
        
        return {
            "scenes": all_scenes,
            "characters": list(all_characters.values())
        }
