import os
from typing import List, Dict, Optional
from openai import OpenAI
import json


class StoryboardGenerator:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openai.qiniu.com/v1"
        )
        self.model = "deepseek/deepseek-v3.1-terminus"
    
    def generate_storyboard_from_novel(self, novel_text: str, max_shots: int = None) -> Dict:
        system_prompt = """你是一个专业的漫画分镜设计师。请分析输入的小说文本，首先识别主要角色，然后按照情节发展生成分镜漫画。

请以JSON格式返回结果，格式如下：
{
  "characters": [
    {
      "name": "角色名",
      "appearance": "外貌描述（详细的视觉特征）",
      "personality": "性格特征",
      "role": "主要角色/次要角色"
    }
  ],
  "storyboard": [
    {
      "shot_number": 1,
      "shot_type": "特写/中景/全景/远景",
      "description": "分镜描述（包含环境、角色位置、动作等）",
      "focus": "焦点内容",
      "characters": ["出现的角色名"],
      "dialogues": [
        {"character": "角色名", "text": "对话内容", "emotion": "情绪"}
      ],
      "narration": "旁白文本（如果有）",
      "scene_type": "动作/对话/过渡"
    }
  ]
}

重要规则：
1. 先完整识别所有主要角色及其外貌特征
2. 分镜应该按照故事情节的自然发展顺序排列
3. 每个分镜应该是一个独立的画面单元
4. 分镜类型要多样化：特写、中景、全景、远景等
5. **确保所有文本（对话、旁白）使用简体中文**
6. 对话必须标注角色名称和情绪状态
7. 描述要详细，便于生成图像"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"请为以下小说生成角色设计和分镜：\n\n{novel_text}"}
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
            except json.JSONDecodeError:
                result = self._create_fallback_result(novel_text)
            
            if max_shots and 'storyboard' in result:
                result['storyboard'] = result['storyboard'][:max_shots]
            
            return result
            
        except Exception as e:
            print(f"生成分镜失败: {e}")
            return self._create_fallback_result(novel_text)
    
    def split_novel_into_chunks(self, text: str, max_chunk_size: int = 3000) -> List[str]:
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
    
    def generate_storyboard_in_chunks(self, novel_text: str, max_shots: int = None) -> Dict:
        chunks = self.split_novel_into_chunks(novel_text)
        
        all_shots = []
        all_characters = {}
        shot_counter = 0
        
        for i, chunk in enumerate(chunks):
            print(f"生成分镜片段 {i+1}/{len(chunks)}...")
            
            chunk_result = self.generate_storyboard_from_novel(chunk, max_shots=None)
            
            for shot in chunk_result.get('storyboard', []):
                shot['shot_number'] = shot_counter
                shot_counter += 1
                all_shots.append(shot)
                
                if max_shots and len(all_shots) >= max_shots:
                    break
            
            for char in chunk_result.get('characters', []):
                char_name = char.get('name', '')
                if char_name and char_name not in all_characters:
                    all_characters[char_name] = char
            
            if max_shots and len(all_shots) >= max_shots:
                break
        
        return {
            "characters": list(all_characters.values()),
            "storyboard": all_shots
        }
    
    def _create_fallback_result(self, text: str) -> Dict:
        return {
            "characters": [],
            "storyboard": [{
                "shot_number": 0,
                "shot_type": "全景",
                "description": text[:500] if len(text) > 500 else text,
                "focus": "场景全貌",
                "characters": [],
                "dialogues": [],
                "narration": text[:500] if len(text) > 500 else text,
                "scene_type": "过渡"
            }]
        }
