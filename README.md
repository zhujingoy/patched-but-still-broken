# 📚 小说自动动漫化系统

一个完整的 Web 应用，可将小说文本自动转换为"图配文 + 语音讲述"的动漫式展示作品。

## ✨ 功能特性

### 核心功能
- 📝 **小说文本输入**：支持用户上传或粘贴小说文本
- 🎬 **自动分镜**：智能将小说分割为多个场景帧
- 🎨 **动漫风格插图**：AI 生成动漫风格的场景插图（需配置 API）
- 🔊 **语音朗读**：文本转语音 TTS 自动生成旁白（需配置 API）
- 👤 **角色一致性**：全篇保持角色风格连贯（发型、服装、表情）

### 界面功能
- 📱 **响应式设计**：完美支持移动端和桌面端
- 🎴 **卡片式展示**：美观的卡片轮播展示
- ▶️ **自动播放**：支持自动播放/暂停功能
- ⏭️ **帧控制**：上一帧/下一帧切换
- 🔊 **音量控制**：可调节语音播放音量
- 🎭 **流畅动画**：帧切换时的平滑过渡效果

## 🚀 快速开始

### 方式一：直接使用（演示模式）
1. 在浏览器中打开 `novel-anime.html`
2. 输入小说文本
3. 点击"开始生成动漫"
4. 使用播放控制按钮浏览作品

**注意**：演示模式下会使用彩色占位图片代替 AI 生成的插图，不包含真实语音。

### 方式二：完整功能（需配置 API）

#### 1. 获取 API Keys

**图片生成 API（选择其一）：**
- [OpenAI DALL-E](https://platform.openai.com/api-keys)
- [Stability AI](https://platform.stability.ai/)
- [Midjourney API](https://www.midjourney.com/)

**语音合成 API（选择其一）：**
- [OpenAI TTS](https://platform.openai.com/api-keys)
- [Azure Speech Services](https://azure.microsoft.com/zh-cn/services/cognitive-services/speech-services/)
- [百度语音合成](https://ai.baidu.com/tech/speech/tts)

#### 2. 配置 API Keys
1. 点击主页面右上角的"⚙️ 设置"按钮
2. 在设置页面输入您的 API Keys
3. 选择对应的 API 提供商
4. 点击"保存设置"按钮
5. 返回主页面开始使用

**注意**：所有 API Keys 仅保存在浏览器本地存储中，不会上传到任何服务器。

#### 3. 使用完整功能
配置完成后，系统将：
- 自动为每个场景生成动漫风格插图
- 自动为每帧文本生成语音朗读
- 保持角色在各帧之间的风格一致性

## 🎯 使用说明

### 输入小说文本
在"上传小说文本"区域输入或粘贴您的小说内容。系统会自动：
- 按段落分割场景
- 智能识别自然的分镜点
- 生成合适数量的动漫帧

### 生成动漫作品
点击"开始生成动漫"按钮，系统将：
1. 分析并分割小说文本
2. 为每个场景生成插图（需 API）
3. 为每帧生成语音朗读（需 API）
4. 展示进度条显示生成进度

### 播放控制
- **▶️ 播放**：自动按顺序播放所有帧
- **⏸️ 暂停**：暂停自动播放
- **⏮️ 上一帧**：回到上一个场景
- **⏭️ 下一帧**：跳到下一个场景
- **⏹️ 停止**：停止播放并返回第一帧
- **🔊 音量**：调节语音播放音量（0-100%）

## 🛠️ 技术架构

### 技术栈
- **前端**：纯 HTML5 + CSS3 + JavaScript（ES6+）
- **无依赖**：不需要 Node.js、npm 或任何构建工具
- **响应式**：Flexbox + CSS Grid 布局
- **动画**：CSS3 动画 + JavaScript 控制

### 文件结构
```
novel-anime.html    # 主页面（小说输入和动漫播放）
settings.html       # API 配置页面
README.md          # 本文档
```

### 核心模块
1. **分镜引擎**：`segmentNovel()` - 智能分割小说文本
2. **图片生成**：`generateImage()` - 调用 AI 图片生成 API
3. **语音合成**：`generateTTS()` - 调用 TTS API
4. **播放控制**：自动播放、帧切换、音量控制
5. **UI 渲染**：动态卡片展示、进度条、动画效果

## 🔧 API 集成指南

### 图片生成 API 集成（示例：OpenAI DALL-E）

在 `generateImage()` 函数中添加：

```javascript
async function generateImage(prompt, apiKey) {
    const response = await fetch('https://api.openai.com/v1/images/generations', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: "dall-e-3",
            prompt: `动漫风格插图：${prompt}。保持角色外观一致，日本动漫画风。`,
            n: 1,
            size: "1024x1024"
        })
    });
    
    const data = await response.json();
    return data.data[0].url;
}
```

### TTS API 集成（示例：OpenAI TTS）

在 `generateTTS()` 函数中添加：

```javascript
async function generateTTS(text, apiKey) {
    const response = await fetch('https://api.openai.com/v1/audio/speech', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
            model: "tts-1",
            voice: "alloy",
            input: text
        })
    });
    
    const audioBlob = await response.blob();
    return URL.createObjectURL(audioBlob);
}
```

## 📋 系统要求

- 现代浏览器（Chrome 90+、Firefox 88+、Safari 14+、Edge 90+）
- 支持 ES6+ JavaScript
- 启用 JavaScript
- 如使用完整功能，需要稳定的网络连接

## 🎨 自定义与扩展

### 修改样式
所有样式都在 `<style>` 标签中，您可以：
- 修改颜色主题（当前为紫色渐变）
- 调整卡片尺寸和布局
- 更改动画效果
- 自定义字体和排版

### 扩展功能
可以添加：
- 角色设定界面（发型、服装、表情库）
- 导出为视频功能
- 更多 AI 模型选择
- 批量处理多个小说
- 社交分享功能

## 📝 示例小说文本

```
夜幕降临，城市的霓虹灯开始闪烁。李明站在高楼的天台上，眺望着远方的天际线。

"这就是我梦想开始的地方。"他喃喃自语道。

突然，一阵刺耳的警报声打破了宁静。李明转身，看到远处升起一股浓烟。他的表情瞬间变得严肃起来。

"看来，那件事还是发生了..."

李明从口袋里掏出一个特殊的装置，上面闪烁着蓝色的光芒。他深吸一口气，按下了中央的按钮。

刹那间，一道耀眼的光芒从装置中射出，笼罩了李明的全身。当光芒散去，他已经换上了一身黑色的作战服，整个人散发出一种截然不同的气质。

"是时候行动了。"
```

## ⚠️ 注意事项

1. **API 费用**：使用 AI 图片生成和 TTS 服务会产生费用，请查看相应服务商的定价
2. **API 限制**：注意 API 的速率限制和配额限制
3. **隐私安全**：请勿在页面中硬编码 API Keys，使用环境变量或安全的配置方式
4. **版权问题**：生成的内容请遵守相关版权法律法规
5. **浏览器兼容**：部分旧版浏览器可能不支持某些功能

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🔗 相关资源

- [OpenAI API 文档](https://platform.openai.com/docs)
- [Stability AI 文档](https://platform.stability.ai/docs)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Canvas API](https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API)

---

**提示**：首次使用建议先在演示模式下测试功能，熟悉操作流程后再配置 API Keys 使用完整功能。
