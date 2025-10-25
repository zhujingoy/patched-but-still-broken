import os
from dotenv import load_dotenv
from novel_parser import NovelParser
from novel_analyzer import NovelAnalyzer
from character_manager import CharacterManager
from image_generator import ImageGenerator
from tts_generator import TTSGenerator
from storyboard_composer import StoryboardComposer
from video_generator import VideoGenerator
from typing import List, Dict
import json


class AnimeGenerator:
    def __init__(self, openai_api_key: str = None, provider: str = "qiniu", custom_prompt: str = None, enable_video: bool = False, use_ai_analysis: bool = True):
        load_dotenv()
        
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("需要提供 API Key")
        
        self.char_mgr = CharacterManager()
        self.image_gen = ImageGenerator(self.api_key, provider=provider, custom_prompt=custom_prompt)
        self.tts_gen = TTSGenerator()
        
        self.video_gen = None
        if enable_video:
            self.video_gen = VideoGenerator(self.api_key)
        
        self.novel_analyzer = None
        if use_ai_analysis:
            self.novel_analyzer = NovelAnalyzer(self.api_key)
        
        self.storyboard_composer = StoryboardComposer(self.image_gen, self.tts_gen, self.char_mgr, self.video_gen)
        
        self.output_dir = "anime_output"
        os.makedirs(self.output_dir, exist_ok=True)
        self.use_ai_analysis = use_ai_analysis
    
    def generate_from_novel(self, novel_path: str, 
                          max_scenes: int = None,
                          character_descriptions: Dict[str, str] = None,
                          generate_video: bool = False) -> Dict:
        with open(novel_path, 'r', encoding='utf-8') as f:
            novel_text = f.read()
        
        all_panels = []
        panel_index = 0
        
        if self.use_ai_analysis and self.novel_analyzer:
            print("=== 第一阶段：使用 DeepSeek AI 分析小说文本并提取角色 ===")
            
            analysis_result = self.novel_analyzer.analyze_novel_in_chunks(novel_text, max_chunks=None)
            
            analyzed_storyboards = analysis_result.get('storyboards', [])
            analyzed_characters = analysis_result.get('characters', [])
            
            print(f"AI分析完成，识别到 {len(analyzed_characters)} 个角色，{len(analyzed_storyboards)} 个分镜")
            
            print("\n=== 第二阶段：设计主要角色并生成角色立绘 ===")
            character_portraits = {}
            
            main_characters = [c for c in analyzed_characters if c.get('role') == '主要角色'][:10]
            if not main_characters:
                main_characters = analyzed_characters[:10]
            
            for char_info in main_characters:
                char_name = char_info.get('name', '')
                if not char_name:
                    continue
                
                self.char_mgr.register_character(
                    char_name,
                    description=char_info.get('personality', ''),
                    appearance={
                        'description': char_info.get('appearance', ''),
                        'background': char_info.get('background', '')
                    }
                )
                
                print(f"设计角色 '{char_name}' 并生成立绘...")
                appearance_prompt = self.novel_analyzer.generate_character_appearance_prompt(char_info)
                
                portrait_path = self.image_gen.generate_character_image(
                    char_name,
                    appearance_prompt,
                    style="anime"
                )
                
                if portrait_path:
                    character_portraits[char_name] = portrait_path
                    print(f"✓ 角色 '{char_name}' 设计完成")
                else:
                    print(f"✗ 角色 '{char_name}' 生成失败")
            
            print(f"\n角色设计完成，共设计 {len(character_portraits)} 个主要角色")
            
            print("\n=== 第三阶段：按照情节发展生成分镜漫画 ===")
            storyboards_to_process = analyzed_storyboards
            
            if max_scenes:
                storyboards_to_process = analyzed_storyboards[:max_scenes]
            
            all_panels = self.storyboard_composer.create_storyboards_from_analysis(
                storyboards_to_process,
                start_index=0,
                generate_video=generate_video
            )
        else:
            print("传统模式已移除，请启用 AI 分析模式 (use_ai_analysis=True)")
            return {
                'novel_path': novel_path,
                'total_panels': 0,
                'characters': [],
                'use_ai_analysis': self.use_ai_analysis,
                'character_portraits': {},
                'panels': [],
                'error': '传统模式已移除，请使用AI分析模式'
            }
        
        character_portraits_data = {}
        if self.use_ai_analysis and self.novel_analyzer and 'character_portraits' in locals():
            character_portraits_data = character_portraits
        
        metadata = {
            'novel_path': novel_path,
            'total_panels': len(all_panels),
            'characters': [char['name'] for char in self.char_mgr.get_all_characters()],
            'use_ai_analysis': self.use_ai_analysis,
            'character_portraits': character_portraits_data,
            'panels': [
                {
                    'panel_index': p['panel_index'],
                    'folder': p['folder'],
                    'characters': p['characters'],
                    'shot_type': p.get('shot_type', '')
                }
                for p in all_panels
            ]
        }
        
        self._save_project_metadata(metadata)
        
        print(f"\n分镜漫画生成完成！")
        print(f"总分镜数：{len(all_panels)}")
        print(f"输出目录：{self.output_dir}")
        
        return metadata
    
    def _save_project_metadata(self, metadata: Dict):
        metadata_path = os.path.join(self.output_dir, "project_metadata.json")
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"项目元数据已保存到：{metadata_path}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='从小说生成动漫（图配文+声音）')
    parser.add_argument('novel_path', help='小说文本文件路径')
    parser.add_argument('--max-scenes', type=int, default=None, 
                       help='最大生成场景数（默认：全部）')
    parser.add_argument('--api-key', default=None, 
                       help='OpenAI API Key（也可通过 .env 文件配置）')
    
    args = parser.parse_args()
    
    try:
        generator = AnimeGenerator(openai_api_key=args.api_key)
        generator.generate_from_novel(args.novel_path, max_scenes=args.max_scenes)
    except Exception as e:
        print(f"错误：{e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
