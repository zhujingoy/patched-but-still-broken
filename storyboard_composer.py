import os
from typing import List, Dict, Optional
from image_generator import ImageGenerator
from tts_generator import TTSGenerator
from character_manager import CharacterManager
import json


class StoryboardComposer:
    def __init__(self, image_generator: ImageGenerator, 
                 tts_generator: TTSGenerator,
                 character_manager: CharacterManager,
                 video_generator = None):
        self.image_gen = image_generator
        self.tts_gen = tts_generator
        self.char_mgr = character_manager
        self.video_gen = video_generator
        self.output_dir = "output_storyboard"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_storyboard_shot(self, shot_index: int, shot_info: Dict, 
                              generate_video: bool = False) -> Dict:
        shot_folder = os.path.join(self.output_dir, f"shot_{shot_index:04d}")
        os.makedirs(shot_folder, exist_ok=True)
        
        shot_description = shot_info.get('description', '')
        shot_type = shot_info.get('shot_type', '全景')
        characters_in_shot = shot_info.get('characters', [])
        dialogues = shot_info.get('dialogues', [])
        narration = shot_info.get('narration', '')
        
        text_for_overlay = self._build_text_for_overlay(dialogues, narration)
        
        character_prompts = []
        for char in characters_in_shot:
            if self.char_mgr.get_character(char):
                character_prompts.append(self.char_mgr.get_character_prompt(char))
        
        character_seeds = {char: self.char_mgr.get_character_seed(char) 
                          for char in characters_in_shot 
                          if self.char_mgr.get_character(char)}
        
        for char in characters_in_shot:
            if self.char_mgr.get_character(char):
                self.char_mgr.increment_appearance_count(char)
        
        full_description = f"{shot_type}镜头，{shot_description}"
        
        shot_image = self.image_gen.generate_scene_image(
            full_description,
            characters=character_prompts,
            character_seeds=character_seeds
        )
        
        output_image = None
        if shot_image:
            output_image = os.path.join(shot_folder, "shot.png")
            
            self.image_gen.create_text_overlay(
                shot_image,
                text_for_overlay,
                output_image
            )
        
        audio_file = self.tts_gen.generate_speech_for_storyboard(shot_info, shot_index)
        
        if audio_file:
            output_audio = os.path.join(shot_folder, "audio.mp3")
            if audio_file != output_audio:
                import shutil
                shutil.copy(audio_file, output_audio)
        else:
            output_audio = None
        
        output_video = None
        if generate_video and self.video_gen and shot_image:
            video_file = self.video_gen.generate_video(
                prompt=shot_description,
                image_path=shot_image
            )
            if video_file:
                output_video = os.path.join(shot_folder, "shot.mp4")
                if video_file != output_video:
                    import shutil
                    shutil.copy(video_file, output_video)
        
        metadata = {
            'shot_index': shot_index,
            'shot_type': shot_type,
            'description': shot_description,
            'characters': characters_in_shot,
            'dialogues': dialogues,
            'narration': narration,
            'text_overlay': text_for_overlay,
            'image_path': output_image,
            'audio_path': output_audio,
            'video_path': output_video,
            'folder': shot_folder
        }
        
        self._save_metadata(shot_folder, metadata)
        
        return metadata
    
    def _build_text_for_overlay(self, dialogues: List[Dict], narration: str) -> str:
        text_parts = []
        
        if narration and narration.strip():
            text_parts.append(f"[旁白] {narration}")
        
        for dialogue in dialogues:
            character = dialogue.get('character', '')
            text = dialogue.get('text', '')
            if text.strip():
                text_parts.append(f"{character}：{text}")
        
        return "\n".join(text_parts)
    
    def _save_metadata(self, folder: str, metadata: Dict):
        metadata_path = os.path.join(folder, "metadata.json")
        
        serializable_metadata = {
            'shot_index': metadata['shot_index'],
            'shot_type': metadata['shot_type'],
            'description': metadata['description'],
            'characters': metadata['characters'],
            'dialogues': metadata['dialogues'],
            'narration': metadata['narration'],
            'text_overlay': metadata['text_overlay'],
            'image_path': metadata.get('image_path'),
            'audio_path': metadata.get('audio_path'),
            'video_path': metadata.get('video_path')
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_metadata, f, ensure_ascii=False, indent=2)
    
    def create_storyboard_shots(self, shots: List[Dict], 
                               generate_video: bool = False) -> List[Dict]:
        shot_metadata_list = []
        
        for i, shot_info in enumerate(shots):
            print(f"生成分镜 {i + 1}/{len(shots)}...")
            
            shot_metadata = self.create_storyboard_shot(
                shot_index=i,
                shot_info=shot_info,
                generate_video=generate_video
            )
            
            shot_metadata_list.append(shot_metadata)
        
        return shot_metadata_list
