# 小说转动漫生成器

自动根据小说生成动漫，包含图片、文字和语音配音。

## 功能特点

- 🤖 **智能 AI 分析**：使用 DeepSeek AI 深度分析小说文本，提取场景、角色、对话和叙述
- ✨ 自动解析小说章节和段落
- 👥 智能提取小说角色并保持角色一致性
- 🎭 **角色立绘生成**：为每个主要角色生成稳定的外观设定和立绘
- 🎨 使用 AI 生成场景图片（支持七牛 Gemini 和 OpenAI DALL-E 3）
- 🗣️ 自动生成中文语音配音（Google TTS）
- 🎥 **视频生成**：支持将场景图片转换为视频（可选）
- 📝 图文结合，文字叠加在图片上
- 💾 自动缓存已生成的图片和音频

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置

1. 复制 `.env.example` 为 `.env`
2. 在 `.env` 中填入你的 OpenAI API Key：

```
OPENAI_API_KEY=your_openai_api_key_here
```

## 使用方法

### Web 界面（推荐）

启动 Web 服务器：

```bash
python web_app.py
```

然后在浏览器中打开 `http://localhost:5000`

Web 界面功能：
- 📤 上传小说文件
- ⚙️ 配置 API Key 和场景数量
- 📊 实时查看生成进度
- 🎬 在线播放动漫场景
- 🎵 支持音频自动播放和手动控制
- 🔊 音量调节
- ⏮⏭ 场景前后导航

### 命令行用法

#### 基本用法

```bash
python anime_generator.py 你的小说.txt
```

#### 限制场景数量

```bash
python anime_generator.py 你的小说.txt --max-scenes 10
```

#### 直接传入 API Key

```bash
python anime_generator.py 你的小说.txt --api-key sk-xxxxx
```

## 小说格式要求

小说文本应该是纯文本格式（.txt），支持以下章节标题格式：

- 第一章 XXX
- 第1章 XXX
- 第一回 XXX
- 第001节 XXX

如果没有章节标题，将把整个文本作为一个章节处理。

## 输出结构

### 传统模式输出

```
output_scenes/
  scene_0000/
    scene.png       # 带文字叠加的场景图片
    narration.mp3   # 语音配音
    metadata.json   # 场景元数据
  scene_0001/
    ...
anime_output/
  project_metadata.json  # 整个项目的元数据
```


## 工作原理（分镜模式）

### 第一阶段：主要角色设计
- 使用 **DeepSeek AI** 模型分析小说文本
- 识别所有主要角色及其外貌、性格特征
- 为每个主要角色生成角色设计稿和立绘
- 确保角色在所有分镜中保持一致的外观

### 第二阶段：分镜生成
- 根据小说情节发展，按时间顺序生成分镜（storyboard）
- 每个分镜包含：
  - **分镜类型**：特写/中景/全景/远景
  - **场景描述**：环境、角色位置、动作
  - **角色对话**：不同角色的对话内容和情绪
  - **旁白文本**：叙述性内容

### 第三阶段：分镜漫画生成
- 为每个分镜生成对应的图像
- 将对话和旁白以简体中文叠加到图片上
- 使用 gTTS 生成多角色语音配音
  - **不同角色使用不同的声音**
  - 自动合成对话和旁白音频

## 核心模块

- `storyboard_generator.py` - **分镜生成器（使用 DeepSeek AI）**
- `storyboard_composer.py` - **分镜组合器**
- `novel_analyzer.py` - AI 小说分析器（传统场景模式）
- `novel_parser.py` - 小说解析器（传统模式）
- `character_manager.py` - 角色管理器
- `image_generator.py` - 图片生成器（支持七牛 Gemini 和 OpenAI DALL-E 3）
- `tts_generator.py` - **多角色语音生成器（基于 Google TTS，支持不同角色不同声音）**
- `video_generator.py` - 视频生成器（可选）
- `scene_composer.py` - 场景组合器（传统模式）
- `anime_generator.py` - 主程序和命令行接口
- `web_app.py` - Flask Web 服务器
- `templates/` - HTML 模板文件
- `static/` - CSS 和 JavaScript 静态资源

## 注意事项

- 使用 OpenAI API 会产生费用，DALL-E 3 的价格为 $0.040 per image (1024×1024)
- 建议首次使用时设置 `--max-scenes` 限制场景数量，避免产生过多费用
- 生成的图片和音频会自动缓存，重复运行不会重复生成
- 角色一致性通过提示词工程和种子值实现，但 DALL-E 3 可能仍会产生一定变化

## 示例

假设你有一个小说文件 `三体.txt`：

```bash
python anime_generator.py 三体.txt --max-scenes 5
```

这将生成前 5 个场景的动漫内容。

## 系统要求

- Python 3.8+
- OpenAI API Key
- 网络连接（用于调用 API）

## 许可

MIT License
