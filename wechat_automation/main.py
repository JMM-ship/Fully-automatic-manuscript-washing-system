#!/usr/bin/env python3
"""
公众号内容自动化系统 - 主程序入口
"""

import click
import asyncio
from pathlib import Path
import sys

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
@click.argument('urls_file', type=click.Path(exists=True))
def crawl(urls_file):
    """批量爬取公众号文章
    
    URLS_FILE: 包含文章链接的文本文件，每行一个链接
    """
    click.echo(f"读取链接文件: {urls_file}")
    
    # 读取URL列表
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
@click.argument('urls_file', type=click.Path(exists=True))
def process(urls_file):
    """完整处理流程：爬取->转换->分类->提取素材
    
    URLS_FILE: 包含文章链接的文本文件
    """
    click.echo("开始完整处理流程...")
    
    # 1. 爬取
    click.echo("\n[1/5] 爬取文章...")
    urls = read_urls_from_file(urls_file)
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