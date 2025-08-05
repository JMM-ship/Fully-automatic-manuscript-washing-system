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
            print(f"[DEBUG] 开始提取: {url}")
            
            # 添加请求头，模拟浏览器
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.encoding = 'utf-8'
            
            print(f"[DEBUG] 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 提取标题 - 尝试多种选择器
                title = soup.find('h1', class_='rich_media_title')
                if not title:
                    title = soup.find('h2', class_='rich_media_title')
                if not title:
                    title = soup.find('meta', attrs={'property': 'og:title'})
                    if title:
                        title_text = title.get('content', '未知标题')
                    else:
                        title_text = "未知标题"
                else:
                    title_text = title.get_text(strip=True)
                
                print(f"[DEBUG] 提取到标题: {title_text}")
                
                # 提取内容 - 尝试多种选择器
                content_div = soup.find('div', class_='rich_media_content')
                if not content_div:
                    content_div = soup.find('div', id='js_content')
                if not content_div:
                    content_div = soup.find('div', class_='rich_media_area_primary')
                
                if content_div:
                    print(f"[DEBUG] 找到内容区域，长度: {len(str(content_div))}")
                    return {
                        'title': title_text,
                        'url': url,
                        'html': str(content_div),
                        'full_html': response.text
                    }
                else:
                    print(f"[DEBUG] 未找到内容区域，尝试保存完整响应")
                    # 保存响应以便调试
                    debug_path = self.raw_articles_path / f"debug_{hash(url)}.html"
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    print(f"[DEBUG] 调试文件已保存到: {debug_path}")
                    
                    # 返回整个body作为后备方案
                    body = soup.find('body')
                    if body:
                        return {
                            'title': title_text,
                            'url': url,
                            'html': str(body),
                            'full_html': response.text
                        }
                    return None
            else:
                print(f"[ERROR] 获取失败，状态码: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"[ERROR] 提取内容时出错: {e}")
            import traceback
            print(f"[DEBUG] 错误详情:\n{traceback.format_exc()}")
            return None
    
    def download_images(self, html_content, article_id):
        """下载文章中的图片"""
        soup = BeautifulSoup(html_content, 'html.parser')
        images = soup.find_all('img')
        
        print(f"[DEBUG] 找到 {len(images)} 张图片")
        
        article_images_path = self.images_path / article_id
        article_images_path.mkdir(exist_ok=True)
        
        image_mapping = {}
        downloaded_count = 0
        
        for idx, img in enumerate(images):
            img_url = None
            
            # 尝试不同的属性获取图片URL
            for attr in ['data-src', 'src', 'data-original']:
                if img.get(attr):
                    img_url = img.get(attr)
                    break
            
            if img_url:
                # 处理相对URL
                if not img_url.startswith('http'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    else:
                        print(f"[DEBUG] 跳过相对URL: {img_url}")
                        continue
                
                try:
                    print(f"[DEBUG] 下载图片 {idx+1}: {img_url[:50]}...")
                    
                    headers = {
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Referer': 'https://mp.weixin.qq.com/'
                    }
                    
                    response = requests.get(img_url, headers=headers, timeout=30)
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
                        downloaded_count += 1
                        print(f"[SUCCESS] 下载图片: {filename}")
                    else:
                        print(f"[ERROR] 图片下载失败，状态码: {response.status_code}")
                        
                except Exception as e:
                    print(f"[ERROR] 下载图片失败: {e}")
        
        print(f"[DEBUG] 共下载 {downloaded_count} 张图片")
        return image_mapping
    
    async def crawl_articles(self, urls):
        """批量爬取文章"""
        results = []
        failed_urls = []
        
        print(f"[DEBUG] 开始爬取 {len(urls)} 篇文章")
        
        for idx, url in enumerate(tqdm(urls, desc="爬取文章")):
            print(f"\n{'='*60}")
            print(f"[INFO] 处理第 {idx+1}/{len(urls)} 篇: {url}")
            
            try:
                # 提取内容
                content = self.extract_content(url)
                
                if content:
                    # 生成文章ID
                    article_id = f"article_{idx+1}"
                    print(f"[DEBUG] 文章ID: {article_id}")
                    
                    # 下载图片
                    print(f"[INFO] 开始下载图片...")
                    image_mapping = self.download_images(content['html'], article_id)
                    
                    # 保存原始HTML
                    html_path = self.raw_articles_path / f"{article_id}.html"
                    with open(html_path, 'w', encoding='utf-8') as f:
                        f.write(content['full_html'])
                    print(f"[SUCCESS] HTML已保存: {html_path}")
                    
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
                    print(f"[SUCCESS] 元数据已保存: {metadata_path}")
                    
                    print(f"[SUCCESS] 文章处理完成: {content['title']}")
                else:
                    print(f"[ERROR] 无法提取内容: {url}")
                    failed_urls.append(url)
                
            except Exception as e:
                print(f"[ERROR] 处理文章时出错: {e}")
                import traceback
                print(f"[DEBUG] 错误详情:\n{traceback.format_exc()}")
                failed_urls.append(url)
            
            # 避免请求过快
            await asyncio.sleep(1)
        
        # 保存总的索引文件
        if results:
            index_path = self.raw_articles_path / "index.json"
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 索引文件已保存: {index_path}")
        
        print(f"\n{'='*60}")
        print(f"[SUMMARY] 爬取完成！")
        print(f"[SUMMARY] 成功: {len(results)} 篇")
        print(f"[SUMMARY] 失败: {len(failed_urls)} 篇")
        
        if failed_urls:
            print(f"[SUMMARY] 失败的URL:")
            for url in failed_urls:
                print(f"  - {url}")
        
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