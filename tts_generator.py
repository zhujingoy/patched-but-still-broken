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
        
        self.character_voice_mapping = {}
    
    def generate_speech(self, text: str, output_filename: Optional[str] = None) -> Optional[str]:
        if not output_filename:
            cache_key = hashlib.md5(text.encode()).hexdigest()
            output_filename = os.path.join(self.cache_dir, f"audio_{cache_key}.mp3")
        
        if os.path.exists(output_filename):
            return output_filename
        
        try:
            tts = gTTS(text=text, lang=self.language, slow=False)
            tts.save(output_filename)
            return output_filename
        except Exception as e:
            print(f"生成语音失败: {e}")
            return None
    
    def generate_speech_for_scene(self, scene_text: str, scene_index: int) -> Optional[str]:
        output_path = os.path.join(self.cache_dir, f"scene_{scene_index:04d}.mp3")
        return self.generate_speech(scene_text, output_path)
    
    def _get_voice_pitch_for_character(self, character_name: str) -> float:
        if character_name not in self.character_voice_mapping:
            char_hash = hash(character_name) % 100
            pitch_shift = (char_hash / 100.0) * 4 - 2
            self.character_voice_mapping[character_name] = pitch_shift
        return self.character_voice_mapping[character_name]
    
    def generate_dialogue_audio(self, dialogues: List[Dict], panel_index: int) -> Optional[str]:
        if not dialogues:
            return None
        
        output_path = os.path.join(self.cache_dir, f"dialogue_{panel_index:04d}.mp3")
        
        if os.path.exists(output_path):
            return output_path
        
        try:
            audio_segments = []
            silence = AudioSegment.silent(duration=300)
            
            for dialogue in dialogues:
                character = dialogue.get('character', '')
                text = dialogue.get('text', '')
                
                if not text:
                    continue
                
                temp_file = os.path.join(self.cache_dir, f"temp_{hash(text)}_{character}.mp3")
                
                if not os.path.exists(temp_file):
                    tts = gTTS(text=text, lang=self.language, slow=False)
                    tts.save(temp_file)
                
                audio = AudioSegment.from_mp3(temp_file)
                
                pitch_shift = self._get_voice_pitch_for_character(character)
                if pitch_shift != 0:
                    new_sample_rate = int(audio.frame_rate * (2.0 ** (pitch_shift / 12.0)))
                    audio = audio._spawn(audio.raw_data, overrides={'frame_rate': new_sample_rate})
                    audio = audio.set_frame_rate(44100)
                
                audio_segments.append(audio)
                audio_segments.append(silence)
            
            if audio_segments:
                combined = sum(audio_segments)
                combined.export(output_path, format="mp3")
                return output_path
            
            return None
            
        except Exception as e:
            print(f"生成对话音频失败: {e}")
            return None
