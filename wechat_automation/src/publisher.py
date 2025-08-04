import os
import json
from pathlib import Path
import yaml
from typing import List, Dict
import re

class ContentPublisher:
    """内容发布准备模块，包含智能配图和最终格式化"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 路径配置
        self.themes_path = Path(self.config['paths']['themes'])
        self.images_path = Path(self.config['paths']['images'])
        self.output_path = Path(self.config['paths']['output'])
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # 复用原有的模板系统
        self.template_path = Path("../wechat_format-main/templates/模板1")
    
    def smart_match_images(self, article_content: str, max_images: int = 5) -> List[Dict]:
        """智能匹配配图"""
        # 读取图片元数据
        metadata_path = self.images_path / "image_metadata.json"
        
        if not metadata_path.exists():
            print("未找到图片元数据")
            return []
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            image_metadata = json.load(f)
        
        # 提取文章关键词
        keywords = self.extract_keywords(article_content)
        
        # 匹配图片
        matched_images = []
        
        for article_id, images in image_metadata.items():
            for image_name, image_data in images.items():
                analysis = image_data.get('analysis', {})
                
                if 'error' not in analysis:
                    # 计算匹配度
                    score = self.calculate_match_score(keywords, analysis)
                    
                    if score > 0:
                        matched_images.append({
                            'path': image_data['path'],
                            'name': image_name,
                            'score': score,
                            'analysis': analysis
                        })
        
        # 按匹配度排序
        matched_images.sort(key=lambda x: x['score'], reverse=True)
        
        # 返回前N个
        return matched_images[:max_images]
    
    def extract_keywords(self, content: str) -> List[str]:
        """从文章内容提取关键词"""
        # 简单的关键词提取
        # 实际应用中可以使用更复杂的NLP方法
        
        # 移除标点符号
        content = re.sub(r'[^\w\s]', ' ', content)
        
        # 分词
        words = content.split()
        
        # 过滤停用词和短词
        keywords = [word for word in words if len(word) > 2]
        
        # 返回出现频率较高的词
        from collections import Counter
        word_freq = Counter(keywords)
        
        return [word for word, _ in word_freq.most_common(20)]
    
    def calculate_match_score(self, keywords: List[str], image_analysis: Dict) -> float:
        """计算图片与文章的匹配度"""
        score = 0
        
        # 检查标签
        image_tags = image_analysis.get('标签', [])
        for keyword in keywords:
            if any(keyword in tag for tag in image_tags):
                score += 2
        
        # 检查描述
        description = image_analysis.get('主要内容描述', '')
        for keyword in keywords:
            if keyword in description:
                score += 1
        
        # 检查适用场景
        scene = image_analysis.get('适用场景', '')
        for keyword in keywords:
            if keyword in scene:
                score += 1.5
        
        return score
    
    def format_article_with_images(self, article_content: str, images: List[Dict]) -> str:
        """将图片插入文章并格式化"""
        # 分段
        paragraphs = article_content.split('\n\n')
        
        # 计算图片插入位置
        if images:
            image_interval = max(1, len(paragraphs) // (len(images) + 1))
            
            # 插入图片
            formatted_content = []
            image_idx = 0
            
            for i, paragraph in enumerate(paragraphs):
                formatted_content.append(paragraph)
                
                # 在适当位置插入图片
                if image_idx < len(images) and (i + 1) % image_interval == 0:
                    formatted_content.append(f"\n[图片{image_idx + 1}]\n")
                    image_idx += 1
            
            return '\n\n'.join(formatted_content)
        else:
            return article_content
    
    def prepare_for_publish(self, theme_name: str, draft_path: str):
        """准备发布内容"""
        # 读取草稿
        with open(draft_path, 'r', encoding='utf-8') as f:
            article_content = f.read()
        
        # 智能配图
        print("正在智能匹配配图...")
        matched_images = self.smart_match_images(article_content)
        
        if matched_images:
            print(f"找到 {len(matched_images)} 张匹配的图片")
            
            # 显示匹配结果
            for idx, img in enumerate(matched_images, 1):
                print(f"{idx}. {img['name']} (匹配度: {img['score']:.2f})")
        
        # 格式化文章
        formatted_content = self.format_article_with_images(article_content, matched_images)
        
        # 添加头尾模板标记
        final_content = "[header]\n\n" + formatted_content + "\n\n[footer]"
        
        # 保存到输出目录
        output_filename = f"{theme_name}_{Path(draft_path).stem}_ready.txt"
        output_path = self.output_path / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(final_content)
        
        # 如果有图片，复制到格式化系统的图片目录
        if matched_images:
            format_img_path = Path("../wechat_format-main/img")
            format_img_path.mkdir(exist_ok=True)
            
            for idx, img in enumerate(matched_images, 1):
                src_path = Path(img['path'])
                dst_path = format_img_path / f"{idx}{src_path.suffix}"
                
                # 复制图片
                import shutil
                shutil.copy2(src_path, dst_path)
        
        print(f"\n发布内容已准备完成: {output_path}")
        print("图片已复制到格式化系统")
        print("\n下一步：")
        print("1. 将输出文件复制到 wechat_format-main/content.txt")
        print("2. 运行 python wechat_format-main/main.py 生成最终HTML")
        
        return output_path

if __name__ == "__main__":
    # 测试发布准备
    publisher = ContentPublisher()
    
    # 示例：准备发布
    # publisher.prepare_for_publish("AI工具", "path/to/draft.md")