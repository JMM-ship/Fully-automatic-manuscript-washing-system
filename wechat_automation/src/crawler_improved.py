import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from pathlib import Path
import json
import yaml
import re
import time
from urllib.parse import urlparse, parse_qs

class WechatCrawlerImproved:
    """改进版微信公众号文章爬虫"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        self.raw_articles_path = Path(self.config['paths']['raw_articles'])
        self.images_path = Path(self.config['paths']['images'])
        self.raw_articles_path.mkdir(parents=True, exist_ok=True)
        self.images_path.mkdir(parents=True, exist_ok=True)
        
        # 更完整的请求头
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x6309092b) XWEB/11253',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
    
    def normalize_url(self, url):
        """规范化URL"""
        # 处理短链接
        if 'mp.weixin.qq.com/s/' in url:
            # 移除多余参数
            if '?' in url:
                base_url = url.split('?')[0]
                params = parse_qs(urlparse(url).query)
                # 保留必要参数
                essential_params = ['__biz', 'mid', 'idx', 'sn']
                new_params = []
                for param in essential_params:
                    if param in params:
                        new_params.append(f"{param}={params[param][0]}")
                if new_params:
                    url = base_url + '?' + '&'.join(new_params)
            return url
        return url
    
    def extract_content_selenium_fallback(self, url):
        """使用selenium作为备用方案（需要单独安装）"""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            print("[INFO] 使用Selenium获取内容...")
            
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'user-agent={self.headers["User-Agent"]}')
            
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(url)
            
            # 等待内容加载
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "rich_media_content"))
            )
            
            # 获取页面源码
            page_source = driver.page_source
            driver.quit()
            
            return page_source
            
        except Exception as e:
            print(f"[ERROR] Selenium失败: {e}")
            return None
    
    def extract_content(self, url):
        """从URL提取文章内容（改进版）"""
        try:
            url = self.normalize_url(url)
            print(f"[DEBUG] 开始提取: {url}")
            
            # 使用session保持cookies
            session = requests.Session()
            session.headers.update(self.headers)
            
            # 第一次请求
            response = session.get(url, timeout=30, allow_redirects=True)
            
            # 检查是否需要重定向
            if response.history:
                print(f"[DEBUG] URL重定向: {response.url}")
            
            print(f"[DEBUG] 响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                # 检查响应内容
                if '请在微信客户端打开链接' in response.text:
                    print("[WARNING] 需要在微信客户端打开，尝试其他方法...")
                    # 尝试selenium
                    page_source = self.extract_content_selenium_fallback(url)
                    if page_source:
                        response_text = page_source
                    else:
                        return None
                else:
                    response_text = response.text
                
                soup = BeautifulSoup(response_text, 'html.parser')
                
                # 提取标题 - 改进的选择器
                title_text = "未知标题"
                
                # 方法1：从meta标签
                meta_title = soup.find('meta', attrs={'property': 'og:title'})
                if meta_title and meta_title.get('content'):
                    title_text = meta_title.get('content').strip()
                else:
                    # 方法2：从h1/h2标签
                    for tag in ['h1', 'h2']:
                        title_elem = soup.find(tag, class_=re.compile('rich_media_title'))
                        if title_elem:
                            title_text = title_elem.get_text(strip=True)
                            break
                    
                    # 方法3：从JavaScript变量
                    if title_text == "未知标题":
                        title_match = re.search(r'var\s+msg_title\s*=\s*["\']([^"\']+)["\']', response_text)
                        if title_match:
                            title_text = title_match.group(1).strip()
                
                print(f"[DEBUG] 提取到标题: {title_text}")
                
                # 提取内容 - 改进的选择器
                content_div = None
                
                # 尝试多种选择器
                selectors = [
                    {'tag': 'div', 'attrs': {'class': 'rich_media_content'}},
                    {'tag': 'div', 'attrs': {'id': 'js_content'}},
                    {'tag': 'div', 'attrs': {'class': re.compile('rich_media_area')}},
                    {'tag': 'div', 'attrs': {'id': 'img-content'}},
                    {'tag': 'article', 'attrs': {}},
                ]
                
                for selector in selectors:
                    content_div = soup.find(selector['tag'], **selector['attrs'])
                    if content_div:
                        print(f"[DEBUG] 使用选择器找到内容: {selector}")
                        break
                
                if content_div:
                    # 清理内容
                    # 移除脚本和样式
                    for script in content_div.find_all('script'):
                        script.decompose()
                    for style in content_div.find_all('style'):
                        style.decompose()
                    
                    print(f"[DEBUG] 找到内容区域，长度: {len(str(content_div))}")
                    
                    return {
                        'title': title_text,
                        'url': url,
                        'html': str(content_div),
                        'full_html': response_text
                    }
                else:
                    print(f"[DEBUG] 未找到内容区域，保存完整响应用于调试")
                    
                    # 保存调试文件
                    debug_path = self.raw_articles_path / f"debug_{int(time.time())}.html"
                    with open(debug_path, 'w', encoding='utf-8') as f:
                        f.write(response_text)
                    print(f"[DEBUG] 调试文件已保存到: {debug_path}")
                    
                    # 检查是否是特殊格式
                    if '<section' in response_text:
                        # 可能是新版格式，提取所有section
                        sections = soup.find_all('section')
                        if sections:
                            content = '\n'.join(str(s) for s in sections)
                            return {
                                'title': title_text,
                                'url': url,
                                'html': content,
                                'full_html': response_text
                            }
                    
                    return None
            else:
                print(f"[ERROR] 获取失败，状态码: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] 网络请求错误: {e}")
            return None
        except Exception as e:
            print(f"[ERROR] 提取内容时出错: {e}")
            import traceback
            print(f"[DEBUG] 错误详情:\n{traceback.format_exc()}")
            return None
    
    def download_images(self, html_content, article_id):
        """下载文章中的图片（改进版）"""
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
            for attr in ['data-src', 'src', 'data-original', 'data-croporisrc']:
                if img.get(attr):
                    img_url = img.get(attr)
                    break
            
            if img_url:
                # 处理相对URL
                if not img_url.startswith('http'):
                    if img_url.startswith('//'):
                        img_url = 'https:' + img_url
                    else:
                        # 可能是base64图片
                        if img_url.startswith('data:image'):
                            print(f"[DEBUG] 跳过base64图片")
                            continue
                        print(f"[DEBUG] 跳过相对URL: {img_url}")
                        continue
                
                # 处理微信图片URL参数
                if 'mmbiz.qpic.cn' in img_url or 'mmbiz.qlogo.cn' in img_url:
                    # 确保获取高质量图片
                    if 'wx_fmt=' not in img_url:
                        img_url = img_url + ('&' if '?' in img_url else '?') + 'wx_fmt=jpeg'
                
                try:
                    print(f"[DEBUG] 下载图片 {idx+1}: {img_url[:80]}...")
                    
                    headers = self.headers.copy()
                    headers['Referer'] = 'https://mp.weixin.qq.com/'
                    
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
                        elif 'webp' in content_type:
                            ext = '.webp'
                        else:
                            # 从URL推断
                            if 'wx_fmt=png' in img_url:
                                ext = '.png'
                            elif 'wx_fmt=gif' in img_url:
                                ext = '.gif'
                            else:
                                ext = '.jpg'
                        
                        filename = f"image_{idx+1}{ext}"
                        filepath = article_images_path / filename
                        
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                        
                        image_mapping[img_url] = str(filepath)
                        downloaded_count += 1
                        print(f"[SUCCESS] 下载图片: {filename} ({len(response.content)/1024:.1f}KB)")
                    else:
                        print(f"[ERROR] 图片下载失败，状态码: {response.status_code}")
                        
                except Exception as e:
                    print(f"[ERROR] 下载图片失败: {e}")
        
        print(f"[DEBUG] 共下载 {downloaded_count}/{len(images)} 张图片")
        return image_mapping
    
    async def crawl_articles(self, urls):
        """批量爬取文章"""
        results = []
        failed_urls = []
        
        print(f"[DEBUG] 开始爬取 {len(urls)} 篇文章")
        print(f"[DEBUG] 工作目录: {os.getcwd()}")
        print(f"[DEBUG] 保存路径: {self.raw_articles_path.absolute()}")
        
        for idx, url in enumerate(tqdm(urls, desc="爬取文章")):
            print(f"\n{'='*80}")
            print(f"[INFO] 处理第 {idx+1}/{len(urls)} 篇")
            
            try:
                # 提取内容
                content = self.extract_content(url)
                
                if content:
                    # 生成文章ID
                    article_id = f"article_{int(time.time())}_{idx+1}"
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
                        'html_path': str(html_path),
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')
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
            
            # 避免请求过快（微信有频率限制）
            wait_time = 2 + (idx % 3)  # 2-4秒随机延迟
            print(f"[INFO] 等待 {wait_time} 秒...")
            await asyncio.sleep(wait_time)
        
        # 保存总的索引文件
        if results:
            index_path = self.raw_articles_path / "index.json"
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"[SUCCESS] 索引文件已保存: {index_path}")
        
        print(f"\n{'='*80}")
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
    crawler = WechatCrawlerImproved()
    
    # 测试URL
    urls = [
        "https://mp.weixin.qq.com/s/0S12mSiFKluNYDhTRSjhjg",
        "https://mp.weixin.qq.com/s/_-yth1HoRINPSkRtgpmqnw",
    ]
    
    # 运行爬虫
    asyncio.run(crawler.crawl_articles(urls))