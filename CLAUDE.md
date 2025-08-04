# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
总是用中文回答我

## 项目概述

此仓库主要包含 **wechat_automation** - 基于 Gemini 2.5 Pro 的公众号内容自动化系统。

旧版系统（wechat_spider-main 和 wechat_format-main）仅作为参考，不再维护。

## 核心命令

```bash
cd wechat_automation

# 安装依赖
pip install -r requirements.txt

# 配置Gemini API密钥
# 编辑 config/config.yaml 添加您的API密钥

# 一键处理流程
python main.py process urls.txt

# 查看所有主题
python main.py list-themes

# 创作文章
python main.py create "主题名称" -i  # 交互式创作
python main.py create "主题名称" -b 3  # 批量创作3篇

# 准备发布
python main.py publish "主题名称" "草稿路径"
```

## 系统架构

### 核心模块
1. **crawler.py**: 批量爬取公众号文章
   - 支持批量URL处理
   - 自动下载图片并建立映射关系
   - 生成文章元数据索引

2. **converter.py**: HTML转Markdown
   - 保留图片引用关系
   - 清理无关HTML标签
   - 生成干净的Markdown文档

3. **classifier.py**: 智能分类系统
   - 使用Gemini 2.5 Pro进行内容理解
   - 自动识别文章主题并分组
   - 创建主题文件夹结构

4. **extractor.py**: 12维度素材提取
   - 标题分析、开篇钩子、文章结构
   - 金句、核心观点、核心论证
   - 数据事实、案例故事、知识点
   - 实用方法、情绪共鸣点、行动号召

5. **image_tagger.py**: 图片智能标签
   - 使用Gemini视觉能力分析图片
   - 自动生成描述性标签
   - 建立图片搜索索引

6. **creator.py**: AI创作助手
   - 基于素材库智能创作
   - 支持交互式和批量创作模式
   - 自动语言优化功能

7. **publisher.py**: 发布准备
   - 智能图文匹配
   - 格式化输出
   - 与旧版format系统集成

### 工作流程
```
爬取URL -> HTML转Markdown -> 智能分类 -> 提取素材 -> AI创作 -> 优化润色 -> 智能配图 -> 发布准备
```

### 提示词系统
所有AI相关的提示词都存储在 `config/prompts/` 目录下：
- classify.txt: 文章分类提示词
- extract.txt: 素材提取提示词（12维度）
- create.txt: 内容创作提示词
- polish.txt: 文案优化提示词

## 数据流向

```
URLs文本文件
    ↓
批量爬取 (crawler.py)
    ↓
HTML + 图片 → data/raw_articles/
    ↓
转换Markdown (converter.py) → data/markdown/
    ↓
智能分类 (classifier.py) → data/themes/{主题名}/
    ↓
素材提取 (extractor.py) → data/themes/{主题名}/素材库/
    ↓
AI创作 (creator.py) → data/themes/{主题名}/草稿/
    ↓
发布准备 (publisher.py) → data/output/
```

## 关键配置

- **Gemini API**: 在 `config/config.yaml` 中配置
- **文件存储**: 基于文件夹系统，无需数据库
- **提示词**: 可在 `config/prompts/` 中自定义
- **阿里云OSS**: 可选，在 `config.yaml` 中配置

## 语言规范

创作和优化文章时遵循以下原则：
- 使用口语化、场景化的语言
- 提供极简、无歧义的指令
- 用具体数字量化收益
- 避免专业术语和英文缩写
- 少用比喻和四字成语
- 英文和中文之间加空格
- 使用简单句结构

## 注意事项

1. 首次使用需配置Gemini API密钥
2. 建议Python 3.9+版本
3. API调用有速率限制，合理使用
4. 图片分析可能耗时较长
5. 所有生成的数据存储在 `data/` 目录下

## 旧版系统说明

- **wechat_spider-main**: 使用GPT-3.5进行文章改写
- **wechat_format-main**: 基于HTML模板的格式化系统
- 这两个系统仅作为参考，不再维护