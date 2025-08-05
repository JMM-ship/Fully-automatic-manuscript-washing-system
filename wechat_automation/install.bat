@echo off
chcp 65001 >nul
echo ======================================
echo 公众号内容自动化系统 - 安装向导
echo ======================================
echo.

REM 检查Python版本
echo 检查Python版本...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python，请先安装Python 3.9或更高版本
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version

REM 询问是否使用虚拟环境
echo.
set /p use_venv="是否创建虚拟环境？(推荐) [Y/n]: "
if "%use_venv%"=="" set use_venv=Y

if /i "%use_venv%"=="Y" (
    echo.
    echo 创建虚拟环境...
    python -m venv venv
    
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
)

REM 升级pip
echo.
echo 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo.
echo 安装依赖包...
pip install -r requirements.txt

if %errorlevel% equ 0 (
    echo.
    echo ✅ 所有依赖安装成功！
) else (
    echo.
    echo ❌ 依赖安装失败，请检查错误信息
    pause
    exit /b 1
)

REM 检查配置文件
echo.
echo 检查配置文件...
if not exist "config\config.yaml" (
    if exist "config\config.example.yaml" (
        copy config\config.example.yaml config\config.yaml
        echo ✅ 已创建配置文件 config\config.yaml
    ) else (
        echo ⚠️  警告：未找到配置文件模板
    )
) else (
    echo ✅ 配置文件已存在
)

REM 创建必要的目录
echo.
echo 创建数据目录...
if not exist "data" mkdir data
if not exist "data\raw_articles" mkdir data\raw_articles
if not exist "data\markdown" mkdir data\markdown
if not exist "data\images" mkdir data\images
if not exist "data\themes" mkdir data\themes
if not exist "data\output" mkdir data\output
echo ✅ 数据目录创建完成

REM 完成提示
echo.
echo ======================================
echo 🎉 安装完成！
echo ======================================
echo.
echo 下一步：
echo 1. 编辑 config\config.yaml 添加您的 Gemini API 密钥
echo 2. 运行以下命令开始使用：
echo.
if /i "%use_venv%"=="Y" (
    echo    venv\Scripts\activate  # 激活虚拟环境
)
echo    python main.py process-with-review  # 带审核的处理流程
echo.
echo 详细使用说明请查看 README.md
echo.
pause