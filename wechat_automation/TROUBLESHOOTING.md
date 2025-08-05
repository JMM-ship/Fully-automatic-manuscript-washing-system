# 故障排除指南

## 常见问题

### 1. ModuleNotFoundError: No module named 'click'

**问题原因**：依赖包未安装或虚拟环境未激活。

**解决方案**：

**方法1**：使用启动脚本（推荐）
```bash
# macOS/Linux
./run.sh process

# Windows
run.bat process
```

**方法2**：激活虚拟环境
```bash
# macOS/Linux
source venv/bin/activate
python main.py process

# Windows
venv\Scripts\activate
python main.py process
```

**方法3**：重新安装依赖
```bash
# 在虚拟环境中
pip install -r requirements.txt
```

### 2. 虚拟环境相关问题

**问题**：不确定是否在虚拟环境中

**检查方法**：
```bash
which python  # macOS/Linux
where python  # Windows
```

如果显示的是系统Python路径（如`/usr/bin/python`），说明虚拟环境未激活。

### 3. API调用错误

**问题**：Gemini API调用失败

**检查项**：
1. 确认已在`config/config.yaml`中配置API密钥
2. 检查网络连接
3. 确认API密钥有效

### 4. 权限问题

**问题**：`Permission denied`错误（macOS/Linux）

**解决方案**：
```bash
chmod +x install.sh
chmod +x run.sh
```

### 5. Windows特定问题

**问题**：脚本无法执行

**解决方案**：
1. 使用`run.bat`而不是`run.sh`
2. 确保使用`python`而不是`python3`命令

### 6. 依赖安装失败

**问题**：某些包安装失败

**可能原因**：
- Python版本过低（需要3.9+）
- 缺少编译工具（Windows需要Visual C++ 14.0）
- 网络问题

**解决方案**：
```bash
# 升级pip
python -m pip install --upgrade pip

# 单独安装失败的包
pip install 包名

# 使用国内镜像源
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

## 爬虫相关问题

### 7. 爬取失败（0篇文章）

**问题**：爬虫运行但显示"共处理 0 篇文章"

**可能原因**：
- 微信公众号反爬虫机制
- 网络连接问题
- URL格式不正确
- 页面结构变化

**解决方案**：

1. **检查URL格式**
   - 确保URL是完整的微信公众号文章链接
   - 格式应该是: `https://mp.weixin.qq.com/s/xxxxx`

2. **查看调试信息**
   - 运行后查看具体的错误信息
   - 检查 `data/raw_articles/debug_*.html` 文件
   - 查看控制台的 `[DEBUG]` 和 `[ERROR]` 信息

3. **尝试测试脚本**
   ```bash
   python test_crawler.py
   ```

4. **手动验证**
   - 在浏览器中打开URL，确认能正常访问
   - 检查是否需要登录或验证

5. **使用改进版爬虫**（如果默认爬虫失败）
   - 临时使用 `crawler_improved.py`
   - 或等待系统更新

### 8. SSL警告

**问题**：`NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+`

**说明**：这是警告信息，不影响功能，可以忽略。

**如果想消除警告**：
```python
import urllib3
urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
```

## 快速诊断命令

```bash
# 检查Python版本
python --version

# 检查已安装的包
pip list

# 检查虚拟环境
echo $VIRTUAL_ENV  # macOS/Linux
echo %VIRTUAL_ENV% # Windows

# 测试Gemini连接
python -c "import google.generativeai as genai; print('Gemini模块正常')"

# 测试爬虫模块
python -c "from src.crawler import WechatCrawler; print('爬虫模块正常')"
```

## 还需要帮助？

如果以上方法都无法解决问题：

1. 查看错误信息的完整内容
2. 检查`requirements.txt`中的所有包是否已安装
3. 尝试在新的虚拟环境中重新安装
4. 在GitHub仓库提交Issue：https://github.com/JMM-ship/Fully-automatic-manuscript-washing-system/issues