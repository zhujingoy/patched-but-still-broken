import os
from gtts import gTTS
from typing import Optional, List, Dict
import hashlib
from pydub import AudioSegment


class TTSGenerator:
    def __init__(self, language: str = 'zh-cn'):
        self.language = language
        self.cache_dir = "audio_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.character_voice_map = {}
        self.available_tlds = ['com', 'co.uk', 'com.au', 'co.in', 'ca', 'co.za']
    
    def assign_voice_to_character(self, character_name: str):
        if character_name not in self.character_voice_map:
            voice_index = len(self.character_voice_map) % len(self.available_tlds)
            self.character_voice_map[character_name] = self.available_tlds[voice_index]
        return self.character_voice_map[character_name]
    
    def generate_speech(self, text: str, output_filename: Optional[str] = None, tld: str = 'com') -> Optional[str]:
        if not output_filename:
            cache_key = hashlib.md5(f"{text}_{tld}".encode()).hexdigest()
            output_filename = os.path.join(self.cache_dir, f"audio_{cache_key}.mp3")
        
        if os.path.exists(output_filename):
            return output_filename
        
        try:
            tts = gTTS(text=text, lang=self.language, slow=False, tld=tld)
            tts.save(output_filename)
            return output_filename
        except Exception as e:
            print(f"生成语音失败: {e}")
            return None
    
    def generate_speech_for_dialogue(self, dialogues: List[Dict], narration: str, output_filename: str) -> Optional[str]:
        if os.path.exists(output_filename):
            return output_filename
        
        audio_segments = []
        
        try:
            if narration and narration.strip():
                narration_file = os.path.join(self.cache_dir, f"temp_narration_{hashlib.md5(narration.encode()).hexdigest()}.mp3")
                narration_audio = self.generate_speech(narration, narration_file, tld='com')
                if narration_audio:
                    audio_segments.append(AudioSegment.from_mp3(narration_audio))
                    audio_segments.append(AudioSegment.silent(duration=300))
            
            for dialogue in dialogues:
                character = dialogue.get('character', '')
                text = dialogue.get('text', '')
                
                if not text.strip():
                    continue
                
                tld = self.assign_voice_to_character(character)
                
                dialogue_file = os.path.join(self.cache_dir, f"temp_dialogue_{hashlib.md5(f'{character}_{text}'.encode()).hexdigest()}.mp3")
                dialogue_audio = self.generate_speech(text, dialogue_file, tld=tld)
                
                if dialogue_audio:
                    audio_segments.append(AudioSegment.from_mp3(dialogue_audio))
                    audio_segments.append(AudioSegment.silent(duration=500))
            
            if audio_segments:
                combined = sum(audio_segments)
                combined.export(output_filename, format="mp3")
                return output_filename
            else:
                return None
                
        except Exception as e:
            print(f"生成对话语音失败: {e}")
            return None
    
    def generate_speech_for_scene(self, scene_text: str, scene_index: int) -> Optional[str]:
        # scene_text 是场景的剧情文字（narration），生成的语音将与前端显示的文字一致
        output_path = os.path.join(self.cache_dir, f"scene_{scene_index:04d}.mp3")
        return self.generate_speech(scene_text, output_path)
    
    def generate_speech_for_storyboard(self, shot_info: Dict, shot_index: int) -> Optional[str]:
        output_path = os.path.join(self.cache_dir, f"storyboard_{shot_index:04d}.mp3")
        
        dialogues = shot_info.get('dialogues', [])
        narration = shot_info.get('narration', '')
        
        if dialogues:
            return self.generate_speech_for_dialogue(dialogues, narration, output_path)
        elif narration:
            return self.generate_speech(narration, output_path)
        else:
            return None
