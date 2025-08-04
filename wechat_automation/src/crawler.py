import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from pathlib import Path
import json
import yaml

class WechatCrawler:
    """微信公众号文章爬虫"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_articles_path = Path(self.config['paths']['raw_articles'])
        self.images_path = Path(self.config['paths']['images'])
        self.raw_articles_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
    
    def extract_content(self, url):
        """从URL提取文章内容"""
        try:
            response = requests.get(url, timeout=30)
            response.encoding = 'utf-8'
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取标题
                title = soup.find('h1', class_='rich_media_title')
                title_text = title.get_text(strip=True) if title else "未知标题"
                
                # 提取内容
                content_div = soup.find('div', class_='rich_media_content')
                
                if content_div:
                    return {
                        'title': title_text,
                        'url': url,
                        'html': str(content_div),
                        'full_html': response.text
                    }
                else:
                    return None
            else:
                print(f"获取失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"提取内容时出错: {e}")
            return None
    
    def download_images(self, html_content, article_id):
        """下载文章中的图片"""
        soup = BeautifulSoup(html_content, 'html.parser')
        images = soup.find_all('img')
        
        article_images_path = self.images_path / article_id
        article_images_path.mkdir(exist_ok=True)
        
        image_mapping = {}
        
        for idx, img in enumerate(images):
            img_url = None
            
            # 尝试不同的属性获取图片URL
            for attr in ['data-src', 'src']:
                if img.get(attr):
                    img_url = img.get(attr)
                    break
            
            if img_url and ('http://' in img_url or 'https://' in img_url):
                try:
                    response = requests.get(img_url, timeout=30)
                    if response.status_code == 200:
                        # 确定图片格式
                        content_type = response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = '.jpg'
                        elif 'png' in content_type:
                            ext = '.png'
                        elif 'gif' in content_type:
                            ext = '.gif'
                        else:
                            ext = '.jpg'  # 默认
                        
                        filename = f"image_{idx+1}{ext}"
                        filepath = article_images_path / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        image_mapping[img_url] = str(filepath)
                        print(f"下载图片: {filename}")
                        
                except Exception as e:
                    print(f"下载图片失败: {e}")
        
        return image_mapping
    
    async def crawl_articles(self, urls):
        """批量爬取文章"""
        results = []
        
        for idx, url in enumerate(tqdm(urls, desc="爬取文章")):
            print(f"\n正在处理: {url}")
            
            # 提取内容
            content = self.extract_content(url)
            
            if content:
                # 生成文章ID
                article_id = f"article_{idx+1}"
                
                # 下载图片
                image_mapping = self.download_images(content['html'], article_id)
                
                # 保存原始HTML
                html_path = self.raw_articles_path / f"{article_id}.html"
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(content['full_html'])
                
                # 保存元数据
                metadata = {
                    'id': article_id,
                    'title': content['title'],
                    'url': content['url'],
                    'images': image_mapping,
                    'html_path': str(html_path)
                }
                
                results.append(metadata)
                
                # 保存元数据
                metadata_path = self.raw_articles_path / f"{article_id}_metadata.json"
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        # 保存总的索引文件
        index_path = self.raw_articles_path / "index.json"
        with open(index_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n爬取完成！共处理 {len(results)} 篇文章")
        return results

def read_urls_from_file(filepath):
    """从文件读取URL列表"""
    with open(filepath, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]
    return urls

if __name__ == "__main__":
    # 测试爬虫
    crawler = WechatCrawler()
    
    # 可以从文件读取URL列表
    # urls = read_urls_from_file("urls.txt")
    
    # 或者直接提供URL列表
    urls = [
        "https://mp.weixin.qq.com/s/OiGl2j9ACsUS3_ZGtwqMDw",
        # 添加更多URL
    ]
    
    # 运行爬虫
    asyncio.run(crawler.crawl_articles(urls))