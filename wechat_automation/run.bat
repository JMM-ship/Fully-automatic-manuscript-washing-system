@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查虚拟环境是否存在
if exist "venv\Scripts\activate.bat" (
    echo 检测到虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
    
    REM 检查依赖是否已安装
    python -c "import click" 2>nul
    if errorlevel 1 (
        echo ⚠️  检测到依赖包未安装，正在安装...
        pip install -r requirements.txt
    )
) else (
    echo 未检测到虚拟环境
    
    REM 检查系统Python中是否安装了依赖
    python -c "import click" 2>nul
    if errorlevel 1 (
        echo ❌ 错误：依赖包未安装
        echo.
        echo 请先运行安装脚本：
        echo   install.bat
        echo.
        echo 或手动安装依赖：
        echo   pip install -r requirements.txt
        pause
        exit /b 1
    )
)

REM 运行主程序，传递所有参数
python main.py %*