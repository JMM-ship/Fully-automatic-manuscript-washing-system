#!/usr/bin/env python3
"""测试爬虫功能"""

import asyncio
from src.crawler import WechatCrawler

async def test_single_url():
    """测试单个URL爬取"""
    crawler = WechatCrawler()
    
    # 测试URL
    test_url = "https://mp.weixin.qq.com/s/0S12mSiFKluNYDhTRSjhjg"
    
    print("测试单个URL爬取...")
    print(f"URL: {test_url}")
    
    # 直接测试extract_content
    print("\n1. 测试内容提取...")
    content = crawler.extract_content(test_url)
    
    if content:
        print(f"✅ 提取成功")
        print(f"   标题: {content['title']}")
        print(f"   HTML长度: {len(content['html'])}")
        print(f"   完整HTML长度: {len(content['full_html'])}")
    else:
        print("❌ 提取失败")
    
    # 测试完整爬取流程
    print("\n2. 测试完整爬取流程...")
    results = await crawler.crawl_articles([test_url])
    
    if results:
        print(f"✅ 爬取成功，共 {len(results)} 篇文章")
        for result in results:
            print(f"   - {result['title']}")
            print(f"     ID: {result['id']}")
            print(f"     图片数: {len(result['images'])}")
    else:
        print("❌ 爬取失败")

if __name__ == "__main__":
    asyncio.run(test_single_url())