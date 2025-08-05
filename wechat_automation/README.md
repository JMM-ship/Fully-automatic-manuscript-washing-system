# 公众号内容自动化系统 MVP

一个基于 AI 的公众号内容自动化创作和发布系统，使用 Gemini 2.5 Pro 模型进行智能处理。

## 功能特点

- 🕷️ **批量爬取**：从微信公众号批量下载文章和图片
- 📝 **格式转换**：HTML 自动转换为 Markdown，保留图片引用
- 🏷️ **智能分类**：基于内容自动分类文章，归组相同主题
- 📊 **素材提取**：从文章中提取12个维度的创作素材
- 🖼️ **图片标签**：使用 AI 分析图片内容并自动打标签
- ✍️ **AI创作**：基于素材库智能创作新文章
- 🎨 **智能配图**：根据内容自动匹配合适的图片
- 📤 **发布准备**：格式化输出，准备发布到公众号

## 快速开始

### 1. 安装依赖

#### 方法一：一键安装脚本（最简单）

**macOS/Linux:**
```bash
./install.sh
```

**Windows:**
```bash
install.bat
```

脚本将自动：
- 检查Python版本
- 创建虚拟环境（可选）
- 安装所有依赖
- 创建必要的目录结构
- 复制配置文件模板

#### 方法二：手动安装
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

#### 依赖包说明
- **requests & aiohttp**: 网络请求和异步爬虫
- **beautifulsoup4 & lxml**: HTML解析和内容提取
- **markdownify**: HTML转Markdown
- **google-generativeai**: Google Gemini AI接口
- **pillow**: 图片处理和分析
- **pyyaml**: 配置文件读取
- **click**: 命令行界面
- **tqdm**: 进度条显示
- **colorama**: 跨平台彩色输出

### 2. 配置 API

编辑 `config/config.yaml`，添加您的 Gemini API 密钥：

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY"
```

### 3. 运行系统

#### 使用启动脚本（推荐）

启动脚本会自动检测并激活虚拟环境：

**macOS/Linux:**
```bash
./run.sh process
./run.sh process-with-review
./run.sh list-themes
```

**Windows:**
```bash
run.bat process
run.bat process-with-review
run.bat list-themes
```

#### 手动运行（如果已激活虚拟环境）

如果已经激活了虚拟环境，可以直接使用python命令：

```bash
# 激活虚拟环境后
python main.py process
python main.py process -i
```

### 4. 运行模式

有两种运行模式：

#### 自动流程（适合熟练用户）

##### 方式一：交互式输入
```bash
# macOS/Linux
./run.sh process

# Windows
run.bat process
```

##### 方式二：从文件读取
创建一个文本文件（如 `urls.txt`），每行一个公众号文章链接：
```
https://mp.weixin.qq.com/s/xxxxx
https://mp.weixin.qq.com/s/yyyyy
```

然后运行：
```bash
# macOS/Linux
./run.sh process urls.txt

# Windows
run.bat process urls.txt
```

#### 带审核流程（推荐新用户使用）

为确保每个阶段的质量，提供了带人工审核的版本：

```bash
# 交互式输入（macOS/Linux）
./run.sh process-with-review

# 交互式输入（Windows）
run.bat process-with-review

# 从文件读取
./run.sh process-with-review urls.txt  # macOS/Linux
run.bat process-with-review urls.txt   # Windows
```

在带审核模式下，每个阶段完成后会：
- 显示处理结果的预览
- 提供以下选项：
  - [c] 继续下一步
  - [r] 重新执行当前步骤
  - [v] 查看更多详情（部分阶段）
  - [e] 编辑结果（部分阶段）
  - [s] 跳过后续步骤
  - [q] 退出程序

## 使用指南

### 查看可用主题

```bash
# macOS/Linux
./run.sh list-themes

# Windows
run.bat list-themes
```

### 创作新文章

```bash
# 默认创作一篇
./run.sh create "主题名称"         # macOS/Linux
run.bat create "主题名称"          # Windows

# 交互式创作
./run.sh create "主题名称" -i      # macOS/Linux
run.bat create "主题名称" -i       # Windows

# 批量创作3篇
./run.sh create "主题名称" -b 3    # macOS/Linux
run.bat create "主题名称" -b 3     # Windows
```

### 准备发布

```bash
# macOS/Linux
./run.sh publish "主题名称" "草稿文件路径"

# Windows
run.bat publish "主题名称" "草稿文件路径"
```

## 单独运行各模块

```bash
# 爬取文章（交互式输入）
./run.sh crawl              # macOS/Linux
run.bat crawl               # Windows

# 爬取文章（从文件读取）
./run.sh crawl urls.txt     # macOS/Linux
run.bat crawl urls.txt      # Windows

# 转换格式
./run.sh convert            # macOS/Linux
run.bat convert             # Windows

# 文章分类
./run.sh classify           # macOS/Linux
run.bat classify            # Windows

# 提取素材
./run.sh extract            # macOS/Linux
run.bat extract             # Windows

# 图片标签
./run.sh tag-images         # macOS/Linux
run.bat tag-images          # Windows
```

## 项目结构

```
wechat_automation/
├── config/
│   ├── config.yaml      # 配置文件
│   └── prompts/         # AI提示词模板
├── data/
│   ├── raw_articles/    # 原始HTML文章
│   ├── markdown/        # Markdown格式文章
│   ├── images/          # 下载的图片（含标签）
│   ├── themes/          # 主题分类
│   │   └── {主题名}/
│   │       ├── articles/   # 该主题的文章
│   │       ├── 素材库/     # 12维度素材文档
│   │       └── 草稿/       # AI生成的草稿
│   └── output/          # 最终输出
├── src/                 # 源代码模块
└── main.py             # 主程序入口
```

## 工作流程

1. **爬取阶段**：下载公众号文章HTML和图片
2. **处理阶段**：转换格式、智能分类、提取素材
3. **创作阶段**：基于素材库AI创作、优化语言
4. **发布阶段**：智能配图、格式化输出

## 系统要求

- Python 3.9 或更高版本
- 稳定的网络连接（访问 Gemini API）
- 至少 2GB 可用磁盘空间（存储文章和图片）

## 注意事项

- 首次运行可能需要较长时间进行图片分析
- API 调用有速率限制，请合理使用
- 建议在虚拟环境中运行，避免依赖冲突
- Windows 用户可能需要安装 Microsoft Visual C++ 14.0

## 遇到问题？

请查看 [故障排除指南](TROUBLESHOOTING.md)

## 后续优化建议

- [ ] 添加更多公众号平台支持
- [ ] 实现自动发布功能
- [ ] 优化图片匹配算法
- [ ] 添加 Web 界面
- [ ] 支持更多 AI 模型