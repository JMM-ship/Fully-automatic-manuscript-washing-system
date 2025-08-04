import os
import json
from pathlib import Path
from bs4 import BeautifulSoup
from markdownify import markdownify as md
import yaml
import re

class HtmlToMarkdownConverter:
    """HTML转Markdown转换器"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_articles_path = Path(self.config['paths']['raw_articles'])
        self.markdown_path = Path(self.config['paths']['markdown'])
        self.markdown_path.mkdir(parents=True, exist_ok=True)
    
    def clean_html(self, html_content):
        """清理HTML内容"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # 移除script和style标签
        for script in soup(["script", "style"]):
            script.decompose()
        
        # 获取rich_media_content内容
        content_div = soup.find('div', class_='rich_media_content')
        if content_div:
            return str(content_div)
        
        return str(soup)
    
    def process_images(self, html_content, image_mapping):
        """处理HTML中的图片链接"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        for img in soup.find_all('img'):
            # 获取原始URL
            img_url = None
            for attr in ['data-src', 'src']:
                if img.get(attr):
                    img_url = img.get(attr)
                    break
            
            # 如果在映射中找到本地路径，替换URL
            if img_url and img_url in image_mapping:
                local_path = image_mapping[img_url]
                # 转换为相对路径
                relative_path = os.path.relpath(local_path, self.markdown_path)
                img['src'] = relative_path
                
                # 添加alt文本
                if not img.get('alt'):
                    img['alt'] = f"图片"
        
        return str(soup)
    
    def html_to_markdown(self, html_content, title=""):
        """将HTML转换为Markdown"""
        # 使用markdownify进行转换
        markdown_content = md(
            html_content,
            heading_style="ATX",
            bullets="-",
            code_language="python",
            strip=['script', 'style']
        )
        
        # 清理多余的空行
        markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)
        
        # 添加标题
        if title:
            markdown_content = f"# {title}\n\n{markdown_content}"
        
        return markdown_content
    
    def convert_article(self, article_metadata):
        """转换单篇文章"""
        article_id = article_metadata['id']
        title = article_metadata['title']
        html_path = article_metadata['html_path']
        image_mapping = article_metadata.get('images', {})
        
        # 读取HTML内容
        with open(html_path, 'r', encoding='utf-8') as f:
            full_html = f.read()
        
        # 清理HTML
        cleaned_html = self.clean_html(full_html)
        
        # 处理图片链接
        processed_html = self.process_images(cleaned_html, image_mapping)
        
        # 转换为Markdown
        markdown_content = self.html_to_markdown(processed_html, title)
        
        # 保存Markdown文件
        markdown_filename = f"{article_id}.md"
        markdown_filepath = self.markdown_path / markdown_filename
        
        with open(markdown_filepath, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        print(f"已转换: {title} -> {markdown_filename}")
        
        return {
            'id': article_id,
            'title': title,
            'markdown_path': str(markdown_filepath),
            'image_mapping': image_mapping
        }
    
    def convert_all_articles(self):
        """转换所有文章"""
        # 读取索引文件
        index_path = self.raw_articles_path / "index.json"
        
        if not index_path.exists():
            print("未找到文章索引文件，请先运行爬虫")
            return []
        
        with open(index_path, 'r', encoding='utf-8') as f:
            articles = json.load(f)
        
        results = []
        
        print(f"开始转换 {len(articles)} 篇文章...")
        
        for article in articles:
            try:
                result = self.convert_article(article)
                results.append(result)
            except Exception as e:
                print(f"转换失败: {article['title']} - {e}")
        
        # 保存转换结果索引
        converted_index_path = self.markdown_path / "index.json"
        with open(converted_index_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n转换完成！共转换 {len(results)} 篇文章")
        return results

if __name__ == "__main__":
    # 测试转换器
    converter = HtmlToMarkdownConverter()
    converter.convert_all_articles()