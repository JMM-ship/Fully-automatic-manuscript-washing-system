#!/bin/bash
# 公众号内容自动化系统 - 智能启动脚本

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 检查虚拟环境是否存在
if [ -d "venv" ]; then
    echo "检测到虚拟环境，正在激活..."
    source venv/bin/activate
    echo "✅ 虚拟环境已激活"
    
    # 检查依赖是否已安装
    if ! python -c "import click" 2>/dev/null; then
        echo "⚠️  检测到依赖包未安装，正在安装..."
        pip install -r requirements.txt
    fi
else
    echo "未检测到虚拟环境"
    
    # 检查系统Python中是否安装了依赖
    if ! python3 -c "import click" 2>/dev/null; then
        echo "❌ 错误：依赖包未安装"
        echo ""
        echo "请先运行安装脚本："
        echo "  ./install.sh"
        echo ""
        echo "或手动安装依赖："
        echo "  pip3 install -r requirements.txt"
        exit 1
    fi
fi

# 运行主程序，传递所有参数
python main.py "$@"