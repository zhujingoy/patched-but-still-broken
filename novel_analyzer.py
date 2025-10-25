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
    
    def analyze_novel_text(self, text: str) -> Dict:
        system_prompt = """你是一个专业的小说分析助手。请分析输入的小说文本，提取以下信息：
1. 人物(Characters)：识别所有出现的人物，包括主要角色和次要角色，提取人物的外貌、性格特征、背景故事
2. 分镜(Storyboards)：根据情节发展将故事拆分为多个分镜，每个分镜包含画面描述、对话、叙述等

请以JSON格式返回结果，格式如下：
{
  "characters": [
    {
      "name": "角色名",
      "appearance": "外貌描述(详细，包括发型、脸型、体型、服饰等)",
      "personality": "性格特征",
      "role": "主要角色/次要角色",
      "background": "角色背景故事"
    }
  ],
  "storyboards": [
    {
      "panel_number": 1,
      "shot_type": "镜头类型(特写/中景/远景/全景等)",
      "description": "画面描述(详细描述画面内容、角色动作、表情、场景环境)",
      "characters": ["出现的角色"],
      "dialogue": "对话内容(如果有)",
      "narration": "旁白文本(如果有)",
      "emotion": "情绪氛围(如：紧张、欢快、悲伤等)"
    }
  ]
}

重要规则：
1. 角色设计要详细完整，确保外貌描述足够生成一致的角色立绘
2. 分镜描述应该像漫画分镜一样，详细说明每个画面的构图、角色位置、动作和表情
3. 每个分镜对应一个漫画格子(panel)，根据情节节奏合理拆分
4. 确保分镜描述包含统一的画风关键词(如：manga style, comic panel)
5. 分镜的shot_type要多样化，包括特写、中景、远景等不同镜头语言"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请分析以下小说文本：\n\n{text}"}
                ],
                temperature=0.7,
                max_tokens=8000
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
                if 'storyboards' not in result:
                    result['storyboards'] = result.get('scenes', [])
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
    
    def generate_storyboard_image_prompt(self, storyboard_info: Dict) -> str:
        description = storyboard_info.get('description', '')
        shot_type = storyboard_info.get('shot_type', '')
        characters = storyboard_info.get('characters', [])
        emotion = storyboard_info.get('emotion', '')
        
        prompt_parts = []
        
        if description:
            prompt_parts.append(description)
        
        if shot_type:
            prompt_parts.append(f"镜头类型：{shot_type}")
        
        if characters:
            char_list = "、".join(characters)
            prompt_parts.append(f"角色：{char_list}")
        
        if emotion:
            prompt_parts.append(f"氛围：{emotion}")
        
        full_prompt = ", ".join(prompt_parts)
        full_prompt += ", 漫画分镜风格, manga panel, comic style, 高质量, 细节丰富"
        
        return full_prompt
    
    def _parse_fallback(self, text: str) -> Dict:
        result = {
            "storyboards": [{
                "panel_number": 1,
                "shot_type": "中景",
                "description": text[:500] if len(text) > 500 else text,
                "characters": [],
                "dialogue": "",
                "narration": text,
                "emotion": "平静"
            }],
            "characters": []
        }
        return result
    
    def _create_empty_result(self) -> Dict:
        return {
            "storyboards": [],
            "characters": []
        }
    
    def split_text_into_chunks(self, text: str, max_chunk_size: int = 2000) -> List[str]:
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(para) > max_chunk_size:
                if current_chunk:
                    chunks.append(current_chunk)
                    current_chunk = ""
                
                for i in range(0, len(para), max_chunk_size):
                    chunks.append(para[i:i + max_chunk_size])
            elif len(current_chunk) + len(para) + 1 <= max_chunk_size:
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
        
        all_storyboards = []
        all_characters = {}
        panel_counter = 0
        
        for i, chunk in enumerate(chunks):
            print(f"分析文本块 {i+1}/{len(chunks)}...")
            
            chunk_result = self.analyze_novel_text(chunk)
            
            for storyboard in chunk_result.get('storyboards', []):
                storyboard['panel_number'] = panel_counter
                panel_counter += 1
                all_storyboards.append(storyboard)
            
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
                        if not existing.get('background') and char.get('background'):
                            existing['background'] = char['background']
        
        return {
            "storyboards": all_storyboards,
            "characters": list(all_characters.values())
        }
