<!-- 
    title: Voice-Pro: 终极 AI 语音转换与多语言翻译工具
    description: 强大的 AI 驱动 Web 应用程序，集 YouTube 视频处理、语音识别、翻译及多语言文本转语音于一体
    keywords: AI 语音转换, YouTube 翻译, 字幕生成, 语音转文本, 文本转语音, 语音克隆, 多语言翻译, ElevenLabs 替代品
    author: ABUS
    version: 3.2.0
    last-updated: 2026-01-28
    product-type: AI 多媒体处理软件
    platforms: macOS, Windows, Linux
    technology-stack: Whisper, Edge-TTS, Gradio, CUDA, Faster-Whisper, Whisper-Timestamped, WhisperX, E2-TTS, F5-TTS, YouTube Downloader, Demucs, MDX-Net, RVC, CosyVoice, kokoro
    license: LGPL
-->

<h1 align="center">
Voice-Pro
</h1>

<p align="center">
  <i align="center">最顶级的 AI 语音识别、翻译及多语言配音解决方案 🚀</i>
</p>

<h4 align="center">
  <a href="https://deepwiki.com/abus-aikorea/voice-pro">
    <img alt="Ask DeepWiki.com" src="https://deepwiki.com/badge.svg" style="height: 20px;">
  </a>
  <a href="https://www.youtube.com/channel/UCbCBWXuVbk-OBp9T4H5JjAA">
    <img src="https://img.shields.io/badge/youtube-d95652.svg?style=flat-square&logo=youtube" alt="youtube" style="height: 20px;">
  </a>
  <a href="https://www.buymeacoffee.com/abus">
    <img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me a Coffee" style="height: 20px;">
  </a>
  <a href="https://github.com/abus-aikorea/voice-pro/releases">
    <img src="https://img.shields.io/github/v/release/abus-aikorea/voice-pro" alt="release" style="height: 20px;">
  </a>
  <a href="https://github.com/abus-aikorea/voice-pro/stargazers">
    <img alt="GitHub Repo stars" src="https://img.shields.io/github/stars/abus-aikorea/voice-pro">
  </a>  
</h4>

<p align="center">
    <img src="docs/images/main_page_crop.zh.jpg?raw=true" alt="Dubbing Studio"/>
</p>
<br />

## 🎙️ AI 驱动的语音识别、翻译与配音 Web 应用

<p>  
  <a href="docs/README.kor.md">
    <img src="https://flagcdn.com/16x12/kr.png" alt="South Korea Flag" style="vertical-align: middle;"> 한국어
  </a> ∙ 
  <a href="docs/README.eng.md">
    <img src="https://flagcdn.com/16x12/us.png" alt="United Kingdom Flag" style="vertical-align: middle;"> English
  </a> ∙ 
  <a href="docs/README.zh.md">
    <img src="https://flagcdn.com/16x12/cn.png" alt="China Flag" style="vertical-align: middle;"> 中文简体
  </a> ∙ 
  <a href="docs/README.tw.md">
    <img src="https://flagcdn.com/16x12/tw.png" alt="Taiwan Flag" style="vertical-align: middle;"> 中文繁體
  </a> ∙ 
  <a href="docs/README.jpn.md">
    <img src="https://flagcdn.com/16x12/jp.png" alt="Japan Flag" style="vertical-align: middle;"> 日本語
  </a> ∙ 
  <a href="docs/README.deu.md">
    <img src="https://flagcdn.com/16x12/de.png" alt="Germany Flag" style="vertical-align: middle;"> Deutsch
  </a> ∙ 
  <a href="docs/README.spa.md">
    <img src="https://flagcdn.com/16x12/es.png" alt="Spain Flag" style="vertical-align: middle;"> Español
  </a> ∙ 
  <a href="docs/README.por.md">
    <img src="https://flagcdn.com/16x12/pt.png" alt="Portugal Flag" style="vertical-align: middle;"> Português
  </a>
</p>

Voice-Pro 是一款代表业界先进水平的 Web 应用程序，彻底改变了多媒体内容创作。它将 YouTube 视频下载、人声分离、语音识别、翻译和文本转语音集成到一个强大的工具中，专为创作者、研究人员和多语言专家设计。

- 🔊 **顶尖语音识别**：支持 **Whisper**, **Faster-Whisper**, **Whisper-Timestamped**, **WhisperX**
- 🎤 **零样本语音克隆**：集成 **F5-TTS**, **E2-TTS**, **CosyVoice**
- 📢 **多语言文本转语音**：支持 **Edge-TTS**, **kokoro** (完全免费)
- 🎥 **YouTube 处理与音频提取**：使用 **yt-dlp**
- 🌍 **100+ 语言即时翻译**：集成 **Deep-Translator**

作为 **ElevenLabs** 的强力开源替代品，Voice-Pro 为播客主播、开发者和创作者提供进阶语音解决方案。

## ⚠️ 注意事项
- 本项目现已全面支持 **macOS**、Windows 和 Linux。
- 我们已将 Voice-Pro 的所有代码开源，并完全免费供大众使用。任何人都可以自由分发和修改。
- **故障排除**：大多数问题可以通过删除 `installer_files` 文件夹，然后依次运行 `configure.sh` (macOS/Linux) 或 `configure.bat` (Windows)，最后运行 `start.sh` 或 `start.bat` 来解决。

## 📰 新闻与历史

<details open>
<summary>版本 3.2 (当前版本)</summary>

- **全面支持 macOS 版本**（包括 Apple Silicon M1/M2/M3 优化）。
- 决定开源所有 Voice-Pro 代码，完全免费。
- 支持 Windows、Mac 和 Linux 跨平台运行。
- 优化了 macOS 下的安装脚本 `configure.sh` 和启动脚本 `start.sh`。

</details>

<details>
<summary>版本 3.1</summary>

- 🪄 支持 **F5-TTS** 的微调模型。
- 🌍 扩展了对英语、中文、日语、韩语、法语、德语、西班牙语、俄语等多国语言的支持。
  
</details>

<details>
<summary>版本 3.0</summary>

- 🔥 移出了 **AI Cover** 功能。  
- 🚀 增加了对 **m-bain/whisperX** 的支持。
  
</details>

## 🎥 视频展示

<table style="border-collapse: collapse; width: 100%;">
  <tr>
    <td style="padding: 10px; border: none;" align="center">
      <a href="https://youtu.be/scC5CicZ6G0" style="text-decoration: none; color: inherit;">
        <img src="https://img.youtube.com/vi/scC5CicZ6G0/hqdefault.jpg" alt="Demo Video 1" width="240" height="135" style="border-radius: 4px;">
        <br>
        <span style="font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.2;">Voice-Pro (v2.0) 演示</span>
      </a>
    </td>
    <td style="padding: 10px; border: none;" align="center">
      <a href="https://youtu.be/Wfo7vQCD4no" style="text-decoration: none; color: inherit;">
        <img src="https://img.youtube.com/vi/Wfo7vQCD4no/hqdefault.jpg" alt="Demo Video 2" width="240" height="135" style="border-radius: 4px;">
        <br>
        <span style="font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.2;">F5-TTS: 语音克隆</span>
      </a>
    </td>
    <td style="padding: 10px; border: none;" align="center">
      <a href="https://youtu.be/GOzCDj4MCpo" style="text-decoration: none; color: inherit;">
        <img src="https://img.youtube.com/vi/GOzCDj4MCpo/hqdefault.jpg" alt="Demo Video 3" width="240" height="135" style="border-radius: 4px;">
        <br>
        <span style="font-size: 16px; font-weight: 600; color: #0f0f0f; line-height: 1.2;">实时转录与翻译</span>
      </a>
    </td>
  </tr>
</table>

## ⭐ 核心功能

### 1. 配音工作室 (Dubbing Studio)
- YouTube 视频下载与音频提取。
- 使用 **Demucs** 进行人声分离。
- 支持 100 多种语言的语音识别与翻译。

### 2. 语音技术
- **语音转文本 (STT)**：集成 Whisper 全系列模型，支持高精度字幕生成。
- **文本转语音 (TTS)**：
  - **Edge-TTS**：100+ 语言，400+ 声音。
  - **F5-TTS / CosyVoice**：实现惊人的零样本语音克隆。
  - **kokoro**：高性能轻量级 TTS 系统。

### 3. 实时翻译
- 即时语音识别与翻译。
- 支持自定义音频输入来源。

## 🤖 WebUI 界面

### `配音工作室` 标签
- 功能中心：视频下载、降噪、字幕制作、翻译及 TTS。
- 支持所有 ffmpeg 兼容格式，输出格式包括 WAV, FLAC, MP3。
- 精确控制 TTS 的语速、音量和音调。
  
<p align="center">
  <img style="width: 90%; height: 90%" src="docs/images/main_page.zh.jpg?raw=true" alt="多语言语音转换与字幕生成 Web UI 界面"/>
</p>  

### `Whisper 字幕` 标签
- 专注于字幕生成：支持 90 多种语言。
- 视频集成预览，支持词级高亮和降噪处理。

### `翻译` 标签
- 支持 ASS, SSA, SRT 等多种字幕文件格式。
- 实现低延迟的实时语音识别转换。

## 🎤✨ 参考声音
如果您有想要添加的特定声音，请在 Issues 页面提交请求：[Issues](https://github.com/abus-aikorea/voice-pro/issues)。

## 💻 系统要求
- **操作系统**：macOS (Intel/M系列), Windows 10/11, Linux
- **硬件加速 (可选)**：NVIDIA GPU (CUDA 12.4) 或 Apple Silicon (MPS)
- **显存**：建议 8GB+ 以获得更佳体验
- **存储空间**：至少 20GB 空闲空间
- **网络连接**：安装过程及模型下载需联网

## 📀 安装步骤

### 1. 下载项目
```bash
git clone https://github.com/abus-aikorea/voice-pro.git
cd voice-pro
```

### 2. 环境配置与启动 (macOS/Linux)
1. 🚀 **./configure.sh**
   - 自动配置 Homebrew (macOS), ffmpeg 和 Git。
2. 🚀 **./start.sh**
   - 自动创建 Conda 环境并安装所有依赖。
   - 第一次运行会下载必要模型，耗时取决于网速。

### 3. 环境配置与启动 (Windows)
1. 🚀 **configure.bat**
2. 🚀 **start.bat**

## ❓ 常见问题

#### 浏览器未自动运行？
- 确认终端内显示的地址（通常为 **http://127.0.0.1:7870**），手动拷贝至浏览器访问。

#### 出现显存不足 (OOM) 错误？
- 将 `Denoise` 级别设置为 0 或 1。
- 尝试使用 `int` 类型计算以减少显存占用。

## ☕ 贡献与支持
大家好，我是来自 Voice-Pro 团队的 David。我们是一家致力于将顶尖 AI 技术带给每一位创作者的团队。如果您觉得这个项目对你有帮助，请考虑给我们点一个 ⭐ **Star**，这不仅是对我们的鼓励，也能帮助项目更好地成长。

- 提交问题请至：[Issues](https://github.com/abus-aikorea/voice-pro/issues) 
- 提交改进请至：[Pull requests](https://github.com/abus-aikorea/voice-pro/pulls)

## 📬 联系我们
- 邮件：<abus.aikorea@gmail.com>
- 官方主页：<https://www.wctokyoseoul.com>

## ©️ 版权信息
<img src="docs/images/ABUS-logo.jpg" width="100" height="100"> by [ABUS](https://www.wctokyoseoul.com)
