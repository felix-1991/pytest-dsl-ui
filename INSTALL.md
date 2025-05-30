# pytest-dsl-ui 安装指南

## 系统要求

- Python 3.9+
- pytest-dsl 0.7.0+
- 支持的操作系统：Windows、macOS、Linux

## 安装步骤

### 1. 安装pytest-dsl-ui

```bash
# 从PyPI安装（推荐）
pip install pytest-dsl-ui

# 或从源码安装
git clone https://github.com/felix-1991/pytest-dsl-ui.git
cd pytest-dsl-ui
pip install -e .
```

### 2. 安装Playwright浏览器

```bash
# 安装所有浏览器
playwright install

# 或只安装特定浏览器
playwright install chromium
playwright install firefox
playwright install webkit
```

### 3. 验证安装

创建一个简单的测试文件 `test_ui.dsl`：

```dsl
@name: "安装验证测试"

[启动浏览器], 浏览器: "chromium", 无头模式: true
[打开页面], 地址: "https://example.com"
[断言元素存在], 定位器: "h1"
[关闭浏览器]
```

运行测试：

```bash
pytest-dsl test_ui.dsl
```

如果测试通过，说明安装成功！

## 开发环境设置

### 1. 克隆仓库

```bash
git clone https://github.com/felix-1991/pytest-dsl-ui.git
cd pytest-dsl-ui
```

### 2. 创建虚拟环境

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. 安装开发依赖

```bash
pip install -e ".[dev]"
playwright install
```

### 4. 运行测试

```bash
# 运行单元测试
pytest tests/

# 运行示例测试
pytest-dsl examples/simple_test.dsl
pytest-dsl examples/advanced_test.dsl
```

## 配置选项

### 浏览器配置

可以通过配置文件或环境变量设置默认浏览器选项：

```yaml
# config.yaml
ui_config:
  default_browser: "chromium"
  default_headless: false
  default_timeout: 30
  screenshot_dir: "screenshots"
  video_dir: "videos"
  viewport:
    width: 1920
    height: 1080
```

### 环境变量

```bash
export PYTEST_DSL_UI_BROWSER=chromium
export PYTEST_DSL_UI_HEADLESS=false
export PYTEST_DSL_UI_TIMEOUT=30
```

## 故障排除

### 常见问题

1. **浏览器启动失败**
   ```
   Error: Browser not found
   ```
   解决方案：运行 `playwright install` 安装浏览器

2. **权限错误**
   ```
   Permission denied
   ```
   解决方案：确保有足够的权限，或使用 `--user` 参数安装

3. **依赖冲突**
   ```
   Dependency conflict
   ```
   解决方案：使用虚拟环境隔离依赖

4. **超时错误**
   ```
   Timeout waiting for element
   ```
   解决方案：增加超时时间或检查网络连接

### 调试模式

启用调试模式查看详细日志：

```bash
# 设置日志级别
export PYTEST_DSL_LOG_LEVEL=DEBUG

# 运行测试
pytest-dsl test_ui.dsl -v
```

### 无头模式问题

如果在无头模式下遇到问题，可以尝试：

1. 关闭无头模式进行调试：
   ```dsl
   [启动浏览器], 浏览器: "chromium", 无头模式: false
   ```

2. 使用慢动作模式：
   ```dsl
   [启动浏览器], 浏览器: "chromium", 慢动作: 1000
   ```

3. 增加等待时间：
   ```dsl
   [设置等待超时], 超时时间: 60
   ```

## 性能优化

### 1. 浏览器复用

在多个测试中复用浏览器实例：

```dsl
# 在第一个测试中启动
[启动浏览器], 浏览器: "chromium"

# 在后续测试中复用，不要关闭浏览器
# [关闭浏览器]  # 注释掉这行
```

### 2. 并行执行

使用pytest-xdist进行并行测试：

```bash
pip install pytest-xdist
pytest-dsl tests/ -n auto
```

### 3. 选择性测试

只运行特定标签的测试：

```bash
pytest-dsl tests/ -k "UI and not slow"
```

## 集成CI/CD

### GitHub Actions示例

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install pytest-dsl-ui
        playwright install --with-deps chromium
    
    - name: Run UI tests
      run: |
        pytest-dsl tests/ --alluredir=reports
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: reports/
```

### Docker支持

```dockerfile
FROM python:3.9-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install -r requirements.txt

# 安装Playwright浏览器
RUN playwright install --with-deps chromium

# 复制测试文件
COPY tests/ /tests/

# 运行测试
CMD ["pytest-dsl", "/tests/"]
```

## 获取帮助

- 查看文档：[README.md](README.md)
- 提交Issue：[GitHub Issues](https://github.com/felix-1991/pytest-dsl-ui/issues)
- 讨论交流：[GitHub Discussions](https://github.com/felix-1991/pytest-dsl-ui/discussions)
