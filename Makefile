# pytest-dsl-ui Makefile
# 提供常用的开发和测试命令

.PHONY: help install install-dev test test-unit test-examples clean build upload docs lint format check setup

# 默认目标
help:
	@echo "pytest-dsl-ui 开发工具"
	@echo ""
	@echo "可用命令:"
	@echo "  setup          - 设置开发环境"
	@echo "  install        - 安装项目依赖"
	@echo "  install-dev    - 安装开发依赖"
	@echo "  test           - 运行所有测试"
	@echo "  test-unit      - 运行单元测试"
	@echo "  test-examples  - 运行示例测试"
	@echo "  lint           - 代码检查"
	@echo "  format         - 代码格式化"
	@echo "  check          - 运行所有检查"
	@echo "  clean          - 清理临时文件"
	@echo "  build          - 构建包"
	@echo "  upload         - 上传到PyPI"
	@echo "  docs           - 生成文档"

# 设置开发环境
setup:
	@echo "设置开发环境..."
	python setup_dev.py

# 安装项目依赖
install:
	pip install -e .
	playwright install chromium

# 安装开发依赖
install-dev:
	pip install -e ".[dev]"
	playwright install

# 运行所有测试
test: test-unit test-examples

# 运行单元测试
test-unit:
	@echo "运行单元测试..."
	pytest tests/ -v

# 运行示例测试
test-examples:
	@echo "运行示例测试..."
	pytest-dsl examples/simple_test.dsl -v
	pytest-dsl examples/advanced_test.dsl -v

# 代码检查
lint:
	@echo "运行代码检查..."
	flake8 pytest_dsl_ui/ --max-line-length=120 --ignore=E203,W503
	@echo "代码检查完成"

# 代码格式化
format:
	@echo "格式化代码..."
	black pytest_dsl_ui/ tests/ --line-length=120
	@echo "代码格式化完成"

# 运行所有检查
check: lint test-unit
	@echo "所有检查完成"

# 清理临时文件
clean:
	@echo "清理临时文件..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf .pytest_cache/
	rm -rf screenshots/
	rm -rf videos/
	@echo "清理完成"

# 构建包
build: clean
	@echo "构建包..."
	python -m build
	@echo "构建完成"

# 上传到PyPI
upload: build
	@echo "上传到PyPI..."
	python -m twine upload dist/*

# 上传到测试PyPI
upload-test: build
	@echo "上传到测试PyPI..."
	python -m twine upload --repository testpypi dist/*

# 生成文档
docs:
	@echo "生成文档..."
	@echo "文档已在README.md中"

# 运行覆盖率测试
coverage:
	@echo "运行覆盖率测试..."
	pytest tests/ --cov=pytest_dsl_ui --cov-report=html --cov-report=term
	@echo "覆盖率报告生成在 htmlcov/ 目录"

# 安全检查
security:
	@echo "运行安全检查..."
	safety check
	bandit -r pytest_dsl_ui/

# 类型检查
typecheck:
	@echo "运行类型检查..."
	mypy pytest_dsl_ui/ --ignore-missing-imports

# 完整检查（用于CI）
ci-check: lint typecheck test-unit coverage
	@echo "CI检查完成"

# 发布准备
release-prep: clean check build
	@echo "发布准备完成"
	@echo "运行 'make upload' 来发布到PyPI"

# 开发模式安装
dev-install: install-dev
	@echo "开发模式安装完成"

# 快速测试（只运行基本测试）
quick-test:
	@echo "运行快速测试..."
	pytest tests/test_keywords.py -v

# 生成需求文件
requirements:
	@echo "生成需求文件..."
	pip freeze > requirements-dev.txt
	@echo "需求文件已生成: requirements-dev.txt"

# 更新依赖
update-deps:
	@echo "更新依赖..."
	pip install --upgrade pip
	pip install --upgrade -e ".[dev]"
	playwright install

# 验证安装
verify:
	@echo "验证安装..."
	python -c "import pytest_dsl_ui; print('pytest-dsl-ui 导入成功')"
	pytest-dsl --version
	playwright --version

# 创建示例项目
create-example:
	@echo "创建示例项目..."
	mkdir -p example_project/tests
	cp examples/simple_test.dsl example_project/tests/
	cp examples/advanced_test.dsl example_project/tests/
	echo "示例项目创建在 example_project/ 目录"

# 运行性能测试
perf-test:
	@echo "运行性能测试..."
	pytest tests/ --benchmark-only

# 生成变更日志
changelog:
	@echo "生成变更日志..."
	git log --oneline --decorate --graph > CHANGELOG.txt
	@echo "变更日志已生成: CHANGELOG.txt"
