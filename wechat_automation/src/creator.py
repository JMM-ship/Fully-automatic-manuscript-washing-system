import os
import json
from pathlib import Path
import google.generativeai as genai
import yaml
from typing import List, Dict
from datetime import datetime

class ContentCreator:
    """AI创作助手，基于素材库创作文章"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 配置Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        
        # 路径配置
        self.themes_path = Path(self.config['paths']['themes'])
        
        # 加载提示词
        with open('config/prompts/create.txt', 'r', encoding='utf-8') as f:
            self.create_prompt_template = f.read()
        
        with open('config/prompts/polish.txt', 'r', encoding='utf-8') as f:
            self.polish_prompt_template = f.read()
    
    def load_theme_materials(self, theme_name: str) -> Dict:
        """加载主题的素材库"""
        theme_path = self.themes_path / theme_name
        materials_path = theme_path / "素材库"
        
        if not materials_path.exists():
            print(f"主题 {theme_name} 的素材库不存在")
            return {}
        
        # 读取所有素材文档
        materials = {}
        
        for md_file in materials_path.glob("*.md"):
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                dimension_name = md_file.stem.replace("《", "").replace("》", "")
                materials[dimension_name] = content
        
        return materials
    
    def create_article(self, theme_name: str, custom_prompt: str = "") -> str:
        """基于素材创作文章"""
        # 加载素材
        materials = self.load_theme_materials(theme_name)
        
        if not materials:
            return ""
        
        print(f"正在为主题 {theme_name} 创作文章...")
        
        # 构建素材内容
        material_content = "\n\n".join([
            f"## {dimension}\n{content}"
            for dimension, content in materials.items()
        ])
        
        # 构建提示
        if custom_prompt:
            # 如果有自定义提示，添加到标准提示后
            full_prompt = self.create_prompt_template.format(
                theme_name=theme_name,
                material_content=material_content
            ) + f"\n\n额外要求：{custom_prompt}"
        else:
            full_prompt = self.create_prompt_template.format(
                theme_name=theme_name,
                material_content=material_content
            )
        
        # 调用Gemini创作
        try:
            response = self.model.generate_content(full_prompt)
            article_content = response.text
            
            return article_content
            
        except Exception as e:
            print(f"创作文章时出错: {e}")
            return ""
    
    def polish_article(self, article_content: str) -> str:
        """优化文章语言"""
        print("正在优化文章语言...")
        
        # 构建提示
        prompt = self.polish_prompt_template.format(
            article_content=article_content
        )
        
        try:
            response = self.model.generate_content(prompt)
            polished_content = response.text
            
            return polished_content
            
        except Exception as e:
            print(f"优化文章时出错: {e}")
            return article_content
    
    def save_draft(self, theme_name: str, article_content: str, draft_name: str = None):
        """保存草稿"""
        theme_path = self.themes_path / theme_name
        drafts_path = theme_path / "草稿"
        drafts_path.mkdir(exist_ok=True)
        
        # 生成文件名
        if not draft_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            draft_name = f"draft_{timestamp}"
        
        # 保存原始草稿
        draft_path = drafts_path / f"{draft_name}.md"
        with open(draft_path, 'w', encoding='utf-8') as f:
            f.write(article_content)
        
        print(f"草稿已保存: {draft_path}")
        
        return draft_path
    
    def interactive_create(self, theme_name: str):
        """交互式创作流程"""
        print(f"\n=== 为主题 {theme_name} 创作文章 ===")
        
        # 显示可用的素材
        materials = self.load_theme_materials(theme_name)
        if materials:
            print("\n可用素材维度：")
            for idx, dimension in enumerate(materials.keys(), 1):
                print(f"{idx}. {dimension}")
        
        # 获取额外要求
        print("\n请输入额外的创作要求（可选，直接回车跳过）：")
        custom_prompt = input("> ")
        
        # 创作文章
        article_content = self.create_article(theme_name, custom_prompt)
        
        if not article_content:
            print("创作失败")
            return
        
        # 显示初稿
        print("\n=== 初稿 ===")
        print(article_content[:500] + "...\n")
        
        # 询问是否优化
        optimize = input("是否需要优化语言？(y/n): ")
        
        if optimize.lower() == 'y':
            article_content = self.polish_article(article_content)
            print("\n=== 优化后 ===")
            print(article_content[:500] + "...\n")
        
        # 保存草稿
        save = input("是否保存草稿？(y/n): ")
        
        if save.lower() == 'y':
            draft_name = input("请输入草稿名称（可选，直接回车使用时间戳）: ")
            self.save_draft(theme_name, article_content, draft_name if draft_name else None)
    
    def batch_create(self, theme_name: str, count: int = 3):
        """批量创作多篇文章"""
        print(f"\n批量为主题 {theme_name} 创作 {count} 篇文章...")
        
        for i in range(count):
            print(f"\n创作第 {i+1} 篇...")
            
            # 创作文章
            article_content = self.create_article(theme_name)
            
            if article_content:
                # 自动优化
                article_content = self.polish_article(article_content)
                
                # 保存草稿
                draft_name = f"batch_draft_{i+1}"
                self.save_draft(theme_name, article_content, draft_name)
        
        print(f"\n批量创作完成！")

if __name__ == "__main__":
    # 测试创作助手
    creator = ContentCreator()
    
    # 示例：交互式创作
    # creator.interactive_create("AI工具")
    
    # 示例：批量创作
    # creator.batch_create("AI工具", count=3)