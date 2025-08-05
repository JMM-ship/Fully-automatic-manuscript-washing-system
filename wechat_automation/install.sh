#!/bin/bash
# 公众号内容自动化系统 - 快速安装脚本

echo "======================================"
echo "公众号内容自动化系统 - 安装向导"
echo "======================================"
echo ""

# 检查Python版本
echo "检查Python版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ 错误：需要Python $required_version或更高版本，当前版本为 $python_version"
    exit 1
else
    echo "✅ Python版本检查通过: $python_version"
fi

# 询问是否使用虚拟环境
echo ""
read -p "是否创建虚拟环境？(推荐) [Y/n]: " use_venv
use_venv=${use_venv:-Y}

if [[ "$use_venv" =~ ^[Yy]$ ]]; then
    echo ""
    echo "创建虚拟环境..."
    python3 -m venv venv
    
    echo "激活虚拟环境..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
fi

# 升级pip
echo ""
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo ""
echo "安装依赖包..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 所有依赖安装成功！"
else
    echo ""
    echo "❌ 依赖安装失败，请检查错误信息"
    exit 1
fi

# 检查配置文件
echo ""
echo "检查配置文件..."
if [ ! -f "config/config.yaml" ]; then
    if [ -f "config/config.example.yaml" ]; then
        cp config/config.example.yaml config/config.yaml
        echo "✅ 已创建配置文件 config/config.yaml"
    else
        echo "⚠️  警告：未找到配置文件模板"
    fi
else
    echo "✅ 配置文件已存在"
fi

# 创建必要的目录
echo ""
echo "创建数据目录..."
mkdir -p data/{raw_articles,markdown,images,themes,output}
echo "✅ 数据目录创建完成"

# 完成提示
echo ""
echo "======================================"
echo "🎉 安装完成！"
echo "======================================"
echo ""
echo "下一步："
echo "1. 编辑 config/config.yaml 添加您的 Gemini API 密钥"
echo "2. 运行以下命令开始使用："
echo ""
if [[ "$use_venv" =~ ^[Yy]$ ]]; then
    echo "   source venv/bin/activate  # 激活虚拟环境"
fi
echo "   python main.py process-with-review  # 带审核的处理流程"
echo ""
echo "详细使用说明请查看 README.md"