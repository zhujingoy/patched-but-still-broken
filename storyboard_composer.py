import os
from typing import List, Dict, Optional
from image_generator import ImageGenerator
from tts_generator import TTSGenerator
from character_manager import CharacterManager
import re


class StoryboardComposer:
    def __init__(self, image_generator: ImageGenerator, 
                 tts_generator: TTSGenerator,
                 character_manager: CharacterManager,
                 video_generator = None):
        self.image_gen = image_generator
        self.tts_gen = tts_generator
        self.char_mgr = character_manager
        self.video_gen = video_generator
        self.output_dir = "output_storyboards"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def create_storyboard_panel(self, panel_index: int, 
                               storyboard_info: Dict,
                               generate_video: bool = False) -> Dict:
        panel_folder = os.path.join(self.output_dir, f"panel_{panel_index:04d}")
        os.makedirs(panel_folder, exist_ok=True)
        
        panel_description = storyboard_info.get('description', '')
        shot_type = storyboard_info.get('shot_type', '')
        characters_in_panel = storyboard_info.get('characters', [])
        dialogue = storyboard_info.get('dialogue', '')
        narration = storyboard_info.get('narration', '')
        emotion = storyboard_info.get('emotion', '')
        
        character_prompts = []
        for char in characters_in_panel:
            if self.char_mgr.get_character(char):
                character_prompts.append(self.char_mgr.get_character_prompt(char))
        
        character_seeds = {char: self.char_mgr.get_character_seed(char) 
                          for char in characters_in_panel 
                          if self.char_mgr.get_character(char)}
        
        for char in characters_in_panel:
            if self.char_mgr.get_character(char):
                self.char_mgr.increment_appearance_count(char)
        
        full_description = f"{panel_description}, {shot_type}, manga panel, comic style"
        if emotion:
            full_description += f", {emotion}"
        
        panel_image = self.image_gen.generate_scene_image(
            full_description,
            characters=character_prompts,
            character_seeds=character_seeds
        )
        
        output_image = None
        if panel_image:
            output_image = os.path.join(panel_folder, "panel.png")
            
            text_to_overlay = dialogue if dialogue else narration
            if text_to_overlay:
                self.image_gen.create_text_overlay(
                    panel_image,
                    text_to_overlay,
                    output_image
                )
            else:
                import shutil
                shutil.copy(panel_image, output_image)
        
        audio_file = None
        if narration:
            audio_file = self.tts_gen.generate_speech_for_scene(narration, panel_index)
        elif dialogue:
            audio_file = self.tts_gen.generate_speech_for_scene(dialogue, panel_index)
        
        output_audio = None
        if audio_file:
            output_audio = os.path.join(panel_folder, "audio.mp3")
            if audio_file != output_audio:
                import shutil
                shutil.copy(audio_file, output_audio)
        
        output_video = None
        if generate_video and self.video_gen and panel_image:
            video_file = self.video_gen.generate_video(
                prompt=full_description,
                image_path=panel_image
            )
            if video_file:
                output_video = os.path.join(panel_folder, "panel.mp4")
                if video_file != output_video:
                    import shutil
                    shutil.copy(video_file, output_video)
        
        metadata = {
            'panel_index': panel_index,
            'shot_type': shot_type,
            'description': panel_description,
            'characters': characters_in_panel,
            'dialogue': dialogue,
            'narration': narration,
            'emotion': emotion,
            'image_path': output_image,
            'audio_path': output_audio,
            'video_path': output_video,
            'folder': panel_folder
        }
        
        self._save_metadata(panel_folder, metadata)
        
        return metadata
    
    def _save_metadata(self, folder: str, metadata: Dict):
        import json
        metadata_path = os.path.join(folder, "metadata.json")
        
        serializable_metadata = {
            'panel_index': metadata.get('panel_index'),
            'shot_type': metadata.get('shot_type'),
            'description': metadata.get('description'),
            'characters': metadata.get('characters'),
            'dialogue': metadata.get('dialogue'),
            'narration': metadata.get('narration'),
            'emotion': metadata.get('emotion'),
            'image_path': metadata.get('image_path'),
            'audio_path': metadata.get('audio_path'),
            'video_path': metadata.get('video_path')
        }
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_metadata, f, ensure_ascii=False, indent=2)
    
    def create_storyboards_from_analysis(self, storyboards: List[Dict], 
                                        start_index: int = 0,
                                        generate_video: bool = False) -> List[Dict]:
        panels = []
        
        for i, storyboard_info in enumerate(storyboards):
            print(f"生成分镜 {start_index + i + 1}/{start_index + len(storyboards)}...")
            
            panel = self.create_storyboard_panel(
                start_index + i, 
                storyboard_info, 
                generate_video=generate_video
            )
            panels.append(panel)
        
        return panels
