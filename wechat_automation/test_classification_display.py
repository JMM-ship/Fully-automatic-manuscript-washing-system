#!/usr/bin/env python3
"""测试分类结果显示"""

import json
from pathlib import Path

# 读取分类结果
classification_file = Path("data/themes/classification.json")
if classification_file.exists():
    with open(classification_file, 'r', encoding='utf-8') as f:
        classification = json.load(f)
    
    print(f"\n✅ 分类完成！共识别出 {len(classification['themes'])} 个主题")
    print("\n主题分类结果：")
    
    for theme in classification['themes']:
        print(f"\n📁 {theme.get('theme_name', '未命名主题')}")
        print(f"   描述：{theme.get('description', '无描述')}")
        print(f"   文章数：{len(theme.get('articles', []))}")
        print(f"   文章列表：")
        articles = theme.get('articles', [])
        for article in articles[:3]:  # 只显示前3篇
            print(f"     - {article}")
        if len(articles) > 3:
            print(f"     ... 还有 {len(articles) - 3} 篇")
else:
    print("未找到分类结果文件")