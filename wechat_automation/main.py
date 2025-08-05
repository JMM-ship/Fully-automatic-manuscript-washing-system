#!/usr/bin/env python3
"""
公众号内容自动化系统 - 主程序入口
"""

import click
import asyncio
from pathlib import Path
import sys
import json
import os

# 添加src目录到Python路径
sys.path.append(str(Path(__file__).parent / "src"))

from crawler import WechatCrawler, read_urls_from_file
from converter import HtmlToMarkdownConverter
from classifier import ArticleClassifier
from extractor import MaterialExtractor
from image_tagger import ImageTagger
from creator import ContentCreator
from publisher import ContentPublisher

@click.group()
def cli():
    """公众号内容自动化系统 MVP"""
    pass

@cli.command()
@click.argument('urls_file', type=click.Path(exists=True), required=False)
@click.option('--interactive', '-i', is_flag=True, help='交互式输入URL')
def crawl(urls_file, interactive):
    """批量爬取公众号文章
    
    URLS_FILE: 包含文章链接的文本文件，每行一个链接（可选）
    """
    urls = []
    
    if interactive or not urls_file:
        # 交互式输入模式
        click.echo("请输入公众号文章链接（每行一个，输入空行结束）：")
        while True:
            url = click.prompt("URL", default="", show_default=False)
            if not url:
                break
            if url.startswith("http"):
                urls.append(url)
            else:
                click.echo("请输入有效的URL（以http开头）")
        
        if not urls:
            click.echo("未输入任何URL，退出")
            return
            
        click.echo(f"\n共输入 {len(urls)} 个链接")
    else:
        # 从文件读取
        click.echo(f"读取链接文件: {urls_file}")
        urls = read_urls_from_file(urls_file)
        click.echo(f"找到 {len(urls)} 个链接")
    
    # 创建爬虫并运行
    crawler = WechatCrawler()
    asyncio.run(crawler.crawl_articles(urls))
    
    click.echo("爬取完成！")

@cli.command()
def convert():
    """将HTML文章转换为Markdown格式"""
    click.echo("开始转换文章...")
    
    converter = HtmlToMarkdownConverter()
    converter.convert_all_articles()
    
    click.echo("转换完成！")

@cli.command()
def classify():
    """对文章进行智能分类"""
    click.echo("开始分类文章...")
    
    classifier = ArticleClassifier()
    result = classifier.run()
    
    if result:
        click.echo("分类完成！")
    else:
        click.echo("分类失败！")

@cli.command()
def extract():
    """提取文章的12维度素材"""
    click.echo("开始提取素材...")
    
    extractor = MaterialExtractor()
    extractor.extract_all_themes()
    
    click.echo("素材提取完成！")

@cli.command()
def tag_images():
    """为图片自动打标签"""
    click.echo("开始分析图片...")
    
    tagger = ImageTagger()
    tagger.tag_all_images()
    
    click.echo("图片标签完成！")

@cli.command()
@click.argument('theme_name')
@click.option('--interactive', '-i', is_flag=True, help='交互式创作模式')
@click.option('--batch', '-b', type=int, help='批量创作文章数量')
def create(theme_name, interactive, batch):
    """基于素材库创作文章
    
    THEME_NAME: 主题名称
    """
    creator = ContentCreator()
    
    if batch:
        # 批量创作模式
        creator.batch_create(theme_name, count=batch)
    elif interactive:
        # 交互式创作模式
        creator.interactive_create(theme_name)
    else:
        # 默认创作一篇
        click.echo(f"为主题 {theme_name} 创作文章...")
        article = creator.create_article(theme_name)
        
        if article:
            # 自动优化
            article = creator.polish_article(article)
            
            # 保存草稿
            draft_path = creator.save_draft(theme_name, article)
            click.echo(f"草稿已保存: {draft_path}")
        else:
            click.echo("创作失败！")

@cli.command()
@click.argument('theme_name')
@click.argument('draft_path', type=click.Path(exists=True))
def publish(theme_name, draft_path):
    """准备发布内容
    
    THEME_NAME: 主题名称
    DRAFT_PATH: 草稿文件路径
    """
    click.echo(f"准备发布: {draft_path}")
    
    publisher = ContentPublisher()
    output_path = publisher.prepare_for_publish(theme_name, draft_path)
    
    click.echo(f"发布内容已准备: {output_path}")

@cli.command()
@click.argument('urls_file', type=click.Path(exists=True), required=False)
@click.option('--interactive', '-i', is_flag=True, help='交互式输入URL')
def process(urls_file, interactive):
    """完整处理流程：爬取->转换->分类->提取素材
    
    URLS_FILE: 包含文章链接的文本文件（可选）
    """
    click.echo("开始完整处理流程...")
    
    # 1. 爬取
    click.echo("\n[1/5] 爬取文章...")
    urls = []
    
    if interactive or not urls_file:
        # 交互式输入模式
        click.echo("请输入公众号文章链接（每行一个，输入空行结束）：")
        while True:
            url = click.prompt("URL", default="", show_default=False)
            if not url:
                break
            if url.startswith("http"):
                urls.append(url)
            else:
                click.echo("请输入有效的URL（以http开头）")
        
        if not urls:
            click.echo("未输入任何URL，退出")
            return
            
        click.echo(f"\n共输入 {len(urls)} 个链接")
    else:
        # 从文件读取
        urls = read_urls_from_file(urls_file)
        click.echo(f"从文件读取 {len(urls)} 个链接")
    
    crawler = WechatCrawler()
    asyncio.run(crawler.crawl_articles(urls))
    
    # 2. 转换
    click.echo("\n[2/5] 转换为Markdown...")
    converter = HtmlToMarkdownConverter()
    converter.convert_all_articles()
    
    # 3. 分类
    click.echo("\n[3/5] 智能分类...")
    classifier = ArticleClassifier()
    classifier.run()
    
    # 4. 提取素材
    click.echo("\n[4/5] 提取素材...")
    extractor = MaterialExtractor()
    extractor.extract_all_themes()
    
    # 5. 图片标签
    click.echo("\n[5/5] 分析图片...")
    tagger = ImageTagger()
    tagger.tag_all_images()
    
    click.echo("\n✅ 完整处理流程完成！")
    click.echo("下一步：使用 'python main.py create <主题名>' 创作文章")

@cli.command()
@click.argument('urls_file', type=click.Path(exists=True), required=False)
@click.option('--interactive', '-i', is_flag=True, help='交互式输入URL')
def process_with_review(urls_file, interactive):
    """带人工审核的处理流程：每个阶段完成后人工确认
    
    URLS_FILE: 包含文章链接的文本文件（可选）
    """
    click.echo("开始带审核的处理流程...")
    click.echo("每个阶段完成后将展示结果，由您决定是否继续、重做或跳过")
    
    # 1. 爬取阶段
    click.echo("\n[1/5] 爬取文章...")
    urls = []
    
    if interactive or not urls_file:
        # 交互式输入模式
        click.echo("请输入公众号文章链接（每行一个，输入空行结束）：")
        while True:
            url = click.prompt("URL", default="", show_default=False)
            if not url:
                break
            if url.startswith("http"):
                urls.append(url)
            else:
                click.echo("请输入有效的URL（以http开头）")
        
        if not urls:
            click.echo("未输入任何URL，退出")
            return
            
        click.echo(f"\n共输入 {len(urls)} 个链接")
    else:
        # 从文件读取
        urls = read_urls_from_file(urls_file)
        click.echo(f"从文件读取 {len(urls)} 个链接")
    
    # 执行爬取
    crawler = WechatCrawler()
    results = asyncio.run(crawler.crawl_articles(urls))
    
    # 显示爬取结果
    raw_articles_path = Path("data/raw_articles")
    if results:
        click.echo(f"\n✅ 爬取成功！共获取 {len(results)} 篇文章")
        click.echo("文章列表：")
        for result in results[:5]:  # 只显示前5篇
            click.echo(f"  - {result['title']} ({result['id']})")
        if len(results) > 5:
            click.echo(f"  ... 还有 {len(results) - 5} 篇")
    else:
        click.echo("\n❌ 爬取失败！未获取到任何文章")
        click.echo("请检查：")
        click.echo("  1. 网络连接是否正常")
        click.echo("  2. URL是否有效")
        click.echo("  3. 查看上方的错误信息")
    
    # 审核爬取结果
    while True:
        action = click.prompt("\n请选择：[c]继续下一步 / [r]重新爬取 / [s]跳过后续步骤 / [q]退出", 
                             type=click.Choice(['c', 'r', 's', 'q']), 
                             default='c')
        
        if action == 'c':
            if not results:
                click.echo("警告：没有成功爬取的文章，后续步骤可能无法正常执行")
                if not click.confirm("确定要继续吗？"):
                    continue
            break
        elif action == 'r':
            click.echo("重新执行爬取...")
            results = asyncio.run(crawler.crawl_articles(urls))
            
            # 重新显示结果
            if results:
                click.echo(f"\n✅ 爬取成功！共获取 {len(results)} 篇文章")
                click.echo("文章列表：")
                for result in results[:5]:
                    click.echo(f"  - {result['title']} ({result['id']})")
                if len(results) > 5:
                    click.echo(f"  ... 还有 {len(results) - 5} 篇")
            else:
                click.echo("\n❌ 爬取失败！未获取到任何文章")
            continue
        elif action == 's':
            click.echo("跳过后续步骤")
            return
        elif action == 'q':
            click.echo("退出程序")
            return
    
    # 2. 转换阶段
    click.echo("\n[2/5] 转换为Markdown...")
    converter = HtmlToMarkdownConverter()
    converter.convert_all_articles()
    
    # 显示转换结果
    markdown_path = Path("data/markdown")
    if markdown_path.exists():
        md_files = list(markdown_path.glob("*.md"))
        click.echo(f"\n✅ 转换完成！共生成 {len(md_files)} 个Markdown文件")
        
        # 预览第一个文件的部分内容
        if md_files:
            sample_file = md_files[0]
            with open(sample_file, 'r', encoding='utf-8') as f:
                content = f.read()
                preview = content[:300] + "..." if len(content) > 300 else content
            click.echo(f"\n预览 {sample_file.name}:")
            click.echo("-" * 50)
            click.echo(preview)
            click.echo("-" * 50)
    
    # 审核转换结果
    while True:
        action = click.prompt("\n请选择：[c]继续下一步 / [r]重新转换 / [v]查看更多文件 / [s]跳过后续步骤 / [q]退出", 
                             type=click.Choice(['c', 'r', 'v', 's', 'q']), 
                             default='c')
        
        if action == 'c':
            break
        elif action == 'r':
            click.echo("重新执行转换...")
            converter.convert_all_articles()
            continue
        elif action == 'v':
            # 列出所有文件让用户选择查看
            for i, md_file in enumerate(md_files[:10]):
                click.echo(f"{i+1}. {md_file.name}")
            if len(md_files) > 10:
                click.echo("... (只显示前10个文件)")
            
            file_num = click.prompt("请输入要查看的文件编号", type=int)
            if 1 <= file_num <= min(len(md_files), 10):
                selected_file = md_files[file_num - 1]
                with open(selected_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    preview = content[:500] + "..." if len(content) > 500 else content
                click.echo(f"\n预览 {selected_file.name}:")
                click.echo("-" * 50)
                click.echo(preview)
                click.echo("-" * 50)
        elif action == 's':
            click.echo("跳过后续步骤")
            return
        elif action == 'q':
            click.echo("退出程序")
            return
    
    # 3. 分类阶段
    click.echo("\n[3/5] 智能分类...")
    classifier = ArticleClassifier()
    result = classifier.run()
    
    # 显示分类结果
    if result:
        themes_path = Path("data/themes")
        classification_file = themes_path / "classification.json"
        
        if classification_file.exists():
            with open(classification_file, 'r', encoding='utf-8') as f:
                classification = json.load(f)
            
            click.echo(f"\n✅ 分类完成！共识别出 {len(classification['themes'])} 个主题")
            click.echo("\n主题分类结果：")
            
            for theme in classification['themes']:
                click.echo(f"\n📁 {theme.get('theme_name', '未命名主题')}")
                click.echo(f"   描述：{theme.get('description', '无描述')}")
                click.echo(f"   文章数：{len(theme.get('articles', []))}")
                click.echo(f"   文章列表：")
                articles = theme.get('articles', [])
                for article in articles[:3]:  # 只显示前3篇
                    click.echo(f"     - {article}")
                if len(articles) > 3:
                    click.echo(f"     ... 还有 {len(articles) - 3} 篇")
    
    # 审核分类结果
    while True:
        action = click.prompt("\n请选择：[c]继续下一步 / [r]重新分类 / [e]编辑分类 / [s]跳过后续步骤 / [q]退出", 
                             type=click.Choice(['c', 'r', 'e', 's', 'q']), 
                             default='c')
        
        if action == 'c':
            break
        elif action == 'r':
            click.echo("重新执行分类...")
            result = classifier.run()
            continue
        elif action == 'e':
            click.echo("编辑分类功能暂未实现，请手动修改 data/themes/classification.json 文件")
        elif action == 's':
            click.echo("跳过后续步骤")
            return
        elif action == 'q':
            click.echo("退出程序")
            return
    
    # 4. 提取素材阶段
    click.echo("\n[4/5] 提取素材...")
    extractor = MaterialExtractor()
    extractor.extract_all_themes()
    
    # 显示提取结果
    themes_path = Path("data/themes")
    theme_dirs = [d for d in themes_path.iterdir() if d.is_dir() and d.name != "classification.json"]
    
    click.echo(f"\n✅ 素材提取完成！")
    for theme_dir in theme_dirs:
        material_path = theme_dir / "素材库"
        if material_path.exists():
            material_files = list(material_path.glob("*.json"))
            click.echo(f"\n📁 {theme_dir.name}: 提取了 {len(material_files)} 个素材文件")
            
            # 预览第一个素材文件
            if material_files:
                with open(material_files[0], 'r', encoding='utf-8') as f:
                    material = json.load(f)
                click.echo(f"   预览素材维度：")
                for key in list(material.keys())[:5]:  # 只显示前5个维度
                    click.echo(f"   - {key}")
    
    # 审核提取结果
    while True:
        action = click.prompt("\n请选择：[c]继续下一步 / [r]重新提取 / [v]查看素材详情 / [s]跳过后续步骤 / [q]退出", 
                             type=click.Choice(['c', 'r', 'v', 's', 'q']), 
                             default='c')
        
        if action == 'c':
            break
        elif action == 'r':
            click.echo("重新执行素材提取...")
            extractor.extract_all_themes()
            continue
        elif action == 'v':
            # 选择主题查看
            for i, theme_dir in enumerate(theme_dirs):
                click.echo(f"{i+1}. {theme_dir.name}")
            
            theme_num = click.prompt("请输入要查看的主题编号", type=int)
            if 1 <= theme_num <= len(theme_dirs):
                selected_theme = theme_dirs[theme_num - 1]
                material_path = selected_theme / "素材库"
                material_files = list(material_path.glob("*.json"))
                
                if material_files:
                    with open(material_files[0], 'r', encoding='utf-8') as f:
                        material = json.load(f)
                    click.echo(f"\n{selected_theme.name} 的素材示例：")
                    click.echo("-" * 50)
                    for key, value in list(material.items())[:3]:  # 只显示前3个维度
                        click.echo(f"{key}:")
                        if isinstance(value, list):
                            for item in value[:2]:  # 每个维度只显示前2项
                                click.echo(f"  - {item}")
                        else:
                            click.echo(f"  {value}")
                    click.echo("-" * 50)
        elif action == 's':
            click.echo("跳过后续步骤")
            return
        elif action == 'q':
            click.echo("退出程序")
            return
    
    # 5. 图片标签阶段
    click.echo("\n[5/5] 分析图片...")
    tagger = ImageTagger()
    tagger.tag_all_images()
    
    # 显示标签结果
    images_path = Path("data/images")
    if images_path.exists():
        image_files = list(images_path.glob("*.jpg")) + list(images_path.glob("*.png"))
        tagged_count = sum(1 for img in image_files if (img.parent / f"{img.stem}_tags.json").exists())
        
        click.echo(f"\n✅ 图片分析完成！")
        click.echo(f"共有 {len(image_files)} 张图片，已标记 {tagged_count} 张")
        
        # 预览一个标签文件
        for img in image_files:
            tag_file = img.parent / f"{img.stem}_tags.json"
            if tag_file.exists():
                with open(tag_file, 'r', encoding='utf-8') as f:
                    tags = json.load(f)
                click.echo(f"\n图片 {img.name} 的标签：")
                click.echo(f"  {tags}")
                break
    
    # 最终审核
    action = click.prompt("\n所有阶段已完成！是否查看最终统计？[y/n]", 
                         type=click.Choice(['y', 'n']), 
                         default='y')
    
    if action == 'y':
        click.echo("\n📊 处理统计：")
        click.echo(f"- 爬取文章数：{len(articles) if 'articles' in locals() else 0}")
        click.echo(f"- 转换文档数：{len(md_files) if 'md_files' in locals() else 0}")
        click.echo(f"- 识别主题数：{len(classification['themes']) if 'classification' in locals() else 0}")
        click.echo(f"- 提取素材数：{sum(len(list((t / '素材库').glob('*.json'))) for t in theme_dirs if (t / '素材库').exists()) if 'theme_dirs' in locals() else 0}")
        click.echo(f"- 标记图片数：{tagged_count if 'tagged_count' in locals() else 0}")
    
    click.echo("\n✅ 带审核的处理流程完成！")
    click.echo("下一步：使用 'python main.py create <主题名>' 创作文章")

@cli.command()
def list_themes():
    """列出所有可用的主题"""
    themes_path = Path("data/themes")
    
    if not themes_path.exists():
        click.echo("未找到任何主题，请先运行分类")
        return
    
    click.echo("可用主题：")
    
    for theme_dir in themes_path.iterdir():
        if theme_dir.is_dir() and theme_dir.name != "classification.json":
            # 读取主题元数据
            metadata_path = theme_dir / "metadata.json"
            if metadata_path.exists():
                import json
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                article_count = metadata.get('article_count', 0)
                description = metadata.get('description', '')
                
                click.echo(f"\n📁 {theme_dir.name}")
                click.echo(f"   文章数: {article_count}")
                if description:
                    click.echo(f"   描述: {description}")

if __name__ == "__main__":
    cli()