import os
import json
from pathlib import Path
import google.generativeai as genai
import yaml
from typing import List, Dict

class ArticleClassifier:
    """文章分类器，使用Gemini进行智能分类"""
    
    def __init__(self, config_path="config/config.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        
        # 配置Gemini
        genai.configure(api_key=self.config['gemini']['api_key'])
        self.model = genai.GenerativeModel(self.config['gemini']['model'])
        
        # 路径配置
        self.markdown_path = Path(self.config['paths']['markdown'])
        self.themes_path = Path(self.config['paths']['themes'])
        self.themes_path.mkdir(parents=True, exist_ok=True)
        
        # 加载提示词
        with open('config/prompts/classify.txt', 'r', encoding='utf-8') as f:
            self.classify_prompt = f.read()
    
    def read_markdown_files(self) -> Dict[str, str]:
        """读取所有Markdown文件"""
        markdown_files = {}
        
        for file_path in self.markdown_path.glob("*.md"):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                markdown_files[file_path.name] = content
        
        return markdown_files
    
    def classify_articles(self) -> Dict:
        """对文章进行分类"""
        # 读取所有Markdown文件
        markdown_files = self.read_markdown_files()
        
        if not markdown_files:
            print("未找到Markdown文件，请先转换文章")
            return {}
        
        print(f"正在对 {len(markdown_files)} 篇文章进行分类...")
        
        # 构建提示内容
        articles_content = "\n\n---\n\n".join([
            f"文件名: {filename}\n{content[:1000]}..."  # 只传递前1000字符作为预览
            for filename, content in markdown_files.items()
        ])
        
        # 调用Gemini进行分类
        try:
            prompt = self.classify_prompt + "\n\n文章内容：\n" + articles_content
            response = self.model.generate_content(prompt)
            
            # 解析JSON响应
            result_text = response.text
            
            # 提取JSON部分
            import re
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                classification_result = json.loads(json_match.group())
            else:
                print("无法解析分类结果")
                return {}
            
        except Exception as e:
            print(f"分类时出错: {e}")
            return {}
        
        return classification_result
    
    def organize_by_themes(self, classification_result: Dict):
        """根据分类结果组织文件"""
        if 'themes' not in classification_result:
            print("分类结果格式错误")
            return
        
        # 读取Markdown索引
        markdown_index_path = self.markdown_path / "index.json"
        with open(markdown_index_path, 'r', encoding='utf-8') as f:
            markdown_index = json.load(f)
        
        # 创建标题到文件名的映射
        title_to_filename = {
            article['title']: article['id'] + '.md'
            for article in markdown_index
        }
        
        for theme in classification_result['themes']:
            theme_name = theme['theme_name']
            theme_desc = theme.get('description', '')
            articles = theme['articles']
            
            # 创建主题文件夹
            theme_path = self.themes_path / theme_name
            theme_path.mkdir(exist_ok=True)
            
            # 创建文章子文件夹
            articles_path = theme_path / "articles"
            articles_path.mkdir(exist_ok=True)
            
            # 复制文章到主题文件夹
            for article_title in articles:
                if article_title in title_to_filename:
                    filename = title_to_filename[article_title]
                    src_path = self.markdown_path / filename
                    dst_path = articles_path / filename
                    
                    if src_path.exists():
                        # 读取并复制文件
                        with open(src_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(dst_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        print(f"已归类: {article_title} -> {theme_name}")
            
            # 保存主题元数据
            theme_metadata = {
                'theme_name': theme_name,
                'description': theme_desc,
                'articles': articles,
                'article_count': len(articles)
            }
            
            metadata_path = theme_path / "metadata.json"
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(theme_metadata, f, ensure_ascii=False, indent=2)
        
        # 保存总的分类结果
        classification_path = self.themes_path / "classification.json"
        with open(classification_path, 'w', encoding='utf-8') as f:
            json.dump(classification_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n分类完成！共创建 {len(classification_result['themes'])} 个主题分组")
    
    def run(self):
        """运行分类流程"""
        # 执行分类
        classification_result = self.classify_articles()
        
        if classification_result:
            # 组织文件
            self.organize_by_themes(classification_result)
            return classification_result
        else:
            return None

if __name__ == "__main__":
    # 测试分类器
    classifier = ArticleClassifier()
    classifier.run()