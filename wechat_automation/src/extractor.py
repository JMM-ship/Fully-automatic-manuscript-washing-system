import os
import json
from pathlib import Path
import google.generativeai as genai
import yaml
from typing import List, Dict

class MaterialExtractor:
    """素材提取器，提取文章的12个维度信息"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 配置Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        
        # 路径配置
        self.themes_path = Path(self.config['paths']['themes'])
        
        # 加载提示词
        with open('config/prompts/extract.txt', 'r', encoding='utf-8') as f:
            self.extract_prompt_template = f.read()
        
        # 12个维度
        self.dimensions = [
            "标题分析",
            "开篇钩子",
            "文章结构",
            "金句",
            "核心观点",
            "核心论证",
            "数据与事实",
            "案例与故事",
            "知识点与信息增量",
            "实用方法与模型",
            "情绪共鸣点",
            "行动号召"
        ]
    
    def extract_materials_for_theme(self, theme_name: str) -> Dict:
        """为特定主题提取素材"""
        theme_path = self.themes_path / theme_name
        articles_path = theme_path / "articles"
        
        if not articles_path.exists():
            print(f"主题 {theme_name} 不存在")
            return {}
        
        # 读取该主题下的所有文章
        articles_content = []
        for md_file in articles_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                articles_content.append({
                    'filename': md_file.name,
                    'content': content
                })
        
        if not articles_content:
            print(f"主题 {theme_name} 下没有文章")
            return {}
        
        print(f"正在为主题 {theme_name} 提取素材（共{len(articles_content)}篇文章）...")
        
        # 构建提示内容
        articles_text = "\n\n---\n\n".join([
            f"文件名: {article['filename']}\n{article['content']}"
            for article in articles_content
        ])
        
        # 调用Gemini进行提取
        try:
            prompt = self.extract_prompt_template.format(
                theme_name=theme_name
            ) + "\n\n文章内容：\n" + articles_text
            
            response = self.model.generate_content(prompt)
            
            # 解析响应
            result_text = response.text
            
            # 尝试解析JSON
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                extracted_materials = json.loads(json_match.group())
            else:
                # 如果不是JSON格式，尝试手动解析
                extracted_materials = self.parse_text_response(result_text)
            
        except Exception as e:
            print(f"提取素材时出错: {e}")
            return {}
        
        return extracted_materials
    
    def parse_text_response(self, text: str) -> Dict:
        """解析文本格式的响应"""
        materials = {}
        
        for dimension in self.dimensions:
            # 尝试找到每个维度的内容
            pattern = rf"{dimension}[：:](.*?)(?={self.dimensions[self.dimensions.index(dimension)+1] if self.dimensions.index(dimension)+1 < len(self.dimensions) else '$'})"
            match = re.search(pattern, text, re.DOTALL)
            
            if match:
                content = match.group(1).strip()
                materials[dimension] = content.split('\n')
        
        return materials
    
    def save_materials(self, theme_name: str, materials: Dict):
        """保存提取的素材"""
        theme_path = self.themes_path / theme_name
        materials_path = theme_path / "素材库"
        materials_path.mkdir(exist_ok=True)
        
        # 保存每个维度的文档
        for dimension, content in materials.items():
            filename = f"《{dimension}汇总》.md"
            filepath = materials_path / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {dimension}汇总\n\n")
                
                if isinstance(content, list):
                    for idx, item in enumerate(content, 1):
                        f.write(f"{idx}. {item}\n\n")
                else:
                    f.write(str(content))
            
            print(f"已保存: {filename}")
        
        # 保存完整的素材JSON
        json_path = materials_path / "all_materials.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(materials, f, ensure_ascii=False, indent=2)
    
    def extract_all_themes(self):
        """为所有主题提取素材"""
        # 读取分类结果
        classification_path = self.themes_path / "classification.json"
        
        if not classification_path.exists():
            print("未找到分类结果，请先运行分类")
            return
        
        with open(classification_path, 'r', encoding='utf-8') as f:
            classification = json.load(f)
        
        for theme in classification['themes']:
            theme_name = theme['theme_name']
            print(f"\n处理主题: {theme_name}")
            
            # 提取素材
            materials = self.extract_materials_for_theme(theme_name)
            
            if materials:
                # 保存素材
                self.save_materials(theme_name, materials)
        
        print("\n所有主题的素材提取完成！")

if __name__ == "__main__":
    # 测试提取器
    extractor = MaterialExtractor()
    extractor.extract_all_themes()