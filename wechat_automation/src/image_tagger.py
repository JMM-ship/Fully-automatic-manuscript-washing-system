import os
import json
from pathlib import Path
import google.generativeai as genai
import yaml
from PIL import Image
from typing import List, Dict

class ImageTagger:
    """图片标签系统，使用Gemini视觉能力分析图片"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 配置Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        
        # 路径配置
        self.images_path = Path(self.config['paths']['images'])
        
        # 图片标签提示词
        self.tag_prompt = """请分析这张图片，并提供以下信息：

1. 图片类型（如：截图、照片、图表、插画等）
2. 主要内容描述（一句话概括）
3. 关键元素（列出图片中的主要元素）
4. 适用场景（这张图片适合配在什么类型的文章中）
5. 情感色彩（正面、中性、负面）
6. 标签（提供5-10个描述性标签）

请以JSON格式返回结果。"""
    
    def analyze_image(self, image_path: Path) -> Dict:
        """分析单张图片"""
        try:
            # 打开图片
            img = Image.open(image_path)
            
            # 调用Gemini分析
            response = self.model.generate_content([self.tag_prompt, img])
            
            # 解析响应
            result_text = response.text
            
            # 提取JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                analysis = json.loads(json_match.group())
            else:
                # 如果解析失败，返回基本信息
                analysis = {
                    "error": "解析失败",
                    "raw_response": result_text
                }
            
            return analysis
            
        except Exception as e:
            print(f"分析图片 {image_path} 时出错: {e}")
            return {"error": str(e)}
    
    def tag_all_images(self):
        """为所有图片打标签"""
        image_metadata = {}
        
        # 遍历所有文章的图片文件夹
        for article_dir in self.images_path.iterdir():
            if article_dir.is_dir():
                print(f"\n处理文章 {article_dir.name} 的图片...")
                
                article_images = {}
                
                # 遍历该文章的所有图片
                for image_file in article_dir.iterdir():
                    if image_file.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        print(f"分析图片: {image_file.name}")
                        
                        # 分析图片
                        analysis = self.analyze_image(image_file)
                        
                        # 保存分析结果
                        article_images[image_file.name] = {
                            'path': str(image_file),
                            'analysis': analysis
                        }
                
                image_metadata[article_dir.name] = article_images
        
        # 保存所有图片的元数据
        metadata_path = self.images_path / "image_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(image_metadata, f, ensure_ascii=False, indent=2)
        
        print(f"\n图片标签完成！元数据已保存到: {metadata_path}")
        
        return image_metadata
    
    def search_images_by_tag(self, tags: List[str]) -> List[Dict]:
        """根据标签搜索图片"""
        # 读取图片元数据
        metadata_path = self.images_path / "image_metadata.json"
        
        if not metadata_path.exists():
            print("未找到图片元数据，请先运行标签分析")
            return []
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            image_metadata = json.load(f)
        
        matched_images = []
        
        # 搜索匹配的图片
        for article_id, images in image_metadata.items():
            for image_name, image_data in images.items():
                analysis = image_data.get('analysis', {})
                
                if 'error' not in analysis:
                    image_tags = analysis.get('标签', [])
                    description = analysis.get('主要内容描述', '')
                    
                    # 检查是否匹配
                    if any(tag in image_tags for tag in tags) or any(tag in description for tag in tags):
                        matched_images.append({
                            'article_id': article_id,
                            'image_name': image_name,
                            'path': image_data['path'],
                            'analysis': analysis
                        })
        
        return matched_images

if __name__ == "__main__":
    # 测试图片标签系统
    tagger = ImageTagger()
    tagger.tag_all_images()