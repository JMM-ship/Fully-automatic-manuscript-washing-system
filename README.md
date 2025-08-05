# 公众号内容自动化系统

基于 Gemini 2.5 Pro 的公众号内容自动化创作和发布系统。

## 项目结构

- **wechat_automation/**: 新版MVP系统（推荐使用）
- **wechat_spider-main/**: 旧版爬虫系统（仅供参考）
- **wechat_format-main/**: 旧版格式化系统（仅供参考）

## 快速开始

### 1. 安装依赖

```bash
cd wechat_automation

# 一键安装（推荐）
./install.sh    # macOS/Linux
install.bat     # Windows

# 或手动安装
pip install -r requirements.txt
```

### 2. 配置API密钥

编辑 `wechat_automation/config/config.yaml`，添加您的 Gemini API 密钥。

### 3. 运行系统

```bash
# 使用启动脚本（推荐，会自动激活虚拟环境）
./run.sh process-with-review    # macOS/Linux带审核流程
run.bat process-with-review     # Windows带审核流程

# 或者手动激活虚拟环境后运行
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows
python main.py process-with-review
```

详细使用说明请查看 [wechat_automation/README.md](wechat_automation/README.md)

## 系统特点

- 🕷️ 批量爬取公众号文章
- 📝 智能分类和素材提取
- ✍️ AI驱动的内容创作
- 🎨 智能配图系统
- 📤 一键发布准备

## 许可证

MIT License