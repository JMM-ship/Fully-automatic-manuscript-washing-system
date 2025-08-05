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

```bash
pip install -r requirements.txt
```

### 2. 配置 API

编辑 `config/config.yaml`，添加您的 Gemini API 密钥：

```yaml
gemini:
  api_key: "YOUR_GEMINI_API_KEY"
```

### 3. 运行完整流程

有两种运行模式：

#### 自动流程（适合熟练用户）

##### 方式一：交互式输入
```bash
# 直接运行，按提示输入URL
python main.py process

# 或使用 -i 参数
python main.py process -i
```

##### 方式二：从文件读取
创建一个文本文件（如 `urls.txt`），每行一个公众号文章链接：
```
https://mp.weixin.qq.com/s/xxxxx
https://mp.weixin.qq.com/s/yyyyy
```

然后运行：
```bash
python main.py process urls.txt
```

#### 带审核流程（推荐新用户使用）

为确保每个阶段的质量，提供了带人工审核的版本：

```bash
# 交互式输入
python main.py process-with-review

# 从文件读取
python main.py process-with-review urls.txt
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
python main.py list-themes
```

### 创作新文章

```bash
# 默认创作一篇
python main.py create "主题名称"

# 交互式创作
python main.py create "主题名称" -i

# 批量创作3篇
python main.py create "主题名称" -b 3
```

### 准备发布

```bash
python main.py publish "主题名称" "草稿文件路径"
```

## 单独运行各模块

```bash
# 爬取文章（交互式输入）
python main.py crawl

# 爬取文章（从文件读取）
python main.py crawl urls.txt

# 转换格式
python main.py convert

# 文章分类
python main.py classify

# 提取素材
python main.py extract

# 图片标签
python main.py tag-images
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

## 注意事项

- 需要稳定的网络连接以访问 Gemini API
- 建议使用 Python 3.9 或更高版本
- 首次运行可能需要较长时间进行图片分析
- API 调用有速率限制，请合理使用

## 后续优化建议

- [ ] 添加更多公众号平台支持
- [ ] 实现自动发布功能
- [ ] 优化图片匹配算法
- [ ] 添加 Web 界面
- [ ] 支持更多 AI 模型