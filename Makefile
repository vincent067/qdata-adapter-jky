.PHONY: help install install-dev test test-cov lint format type-check clean build publish docs version bump-patch bump-minor bump-major publish-test security check release git-init git-first-commit

# 颜色输出
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## 显示帮助信息
	@echo "$(BLUE)JkyAdapter - 开发工具$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "快速开始:"
	@echo "  1. make install-dev  # 安装开发依赖"
	@echo "  2. cp .env.example .env && 编辑 .env 填入凭据"
	@echo "  3. make example      # 运行示例"
	@echo "  4. make test         # 运行测试"

# Installation
install: ## 安装项目
	pip install -e .

install-dev: ## 安装开发依赖
	pip install -e ".[dev]"

# Testing
test: ## 运行测试（Mock 模式）
	pytest

test-real: ## 运行测试（使用真实 API，需配置 .env）
	USE_REAL_API=true pytest -v

test-record: ## 运行测试并录制 HTTP 流量
	RECORD_HTTP_TRAFFIC=true pytest -v

test-cov: ## 运行测试（带覆盖率）
	pytest --cov=qdata_adapter_jky --cov-report=term-missing --cov-report=html

test-verbose: ## 运行测试（详细模式）
	pytest -v

# Examples
example: ## 运行快速开始示例
	python examples/quickstart.py

example-real: ## 运行示例（使用真实 API）
	USE_REAL_API=true python examples/quickstart.py

# Code quality
lint: ## 运行代码检查
	ruff check src tests
	bandit -r src -ll

format: ## 格式化代码
	black src tests
	isort src tests

type-check: ## 类型检查
	mypy src/qdata_adapter_jky

# Cleaning
clean: ## 清理构建产物
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .coverage.*
	rm -rf coverage.xml
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf __pycache__/
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Building
build: clean ## 构建包
	python -m build

# Documentation
docs: ## 构建文档
	cd docs && make html

docs-serve: ## 启动文档服务器
	cd docs && make html && python -m http.server 8000 -d _build/html

# Development
dev-setup: install-dev ## 设置开发环境
	pre-commit install

# Security check
security: ## 运行安全检查
	@echo "$(BLUE)运行安全检查...$(NC)"
	bandit -r src -ll

# All-in-one quality check
check: lint type-check security ## 运行所有检查

quality: format lint type-check test ## 完整质量检查

# Version management
version: ## 显示当前版本
	@echo "0.1.0"

bump-patch: ## 递增 patch 版本号 (0.1.0 → 0.1.1)
	@echo "$(YELLOW)请手动修改 pyproject.toml 中的 version 字段$(NC)"

bump-minor: ## 递增 minor 版本号 (0.1.0 → 0.2.0)
	@echo "$(YELLOW)请手动修改 pyproject.toml 中的 version 字段$(NC)"

bump-major: ## 递增 major 版本号 (0.1.0 → 1.0.0)
	@echo "$(YELLOW)请手动修改 pyproject.toml 中的 version 字段$(NC)"

# Publishing
publish-test: build ## 发布到 Test PyPI
	@echo "$(BLUE)发布到 Test PyPI...$(NC)"
	python -m twine upload --repository testpypi dist/*

publish: build ## 发布到 PyPI (需要确认)
	@echo "$(YELLOW)准备发布到 PyPI...$(NC)"
	@echo "$(YELLOW)请确认版本号和 CHANGELOG 已更新！$(NC)"
	@read -p "确认发布? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		python -m twine upload dist/*; \
		echo "$(GREEN)✓ 发布成功！$(NC)"; \
	else \
		echo "$(YELLOW)✗ 取消发布$(NC)"; \
	fi

# Release preparation
release: clean quality build ## 准备发布（测试+构建）
	@echo "$(GREEN)Ready for release! Check dist/ for built packages.$(NC)"

# Git helpers
git-init: ## 初始化 Git 仓库
	git init
	git add .
	git commit -m "chore: initial commit"
	@echo "$(GREEN)✓ Git 仓库已初始化$(NC)"
	@echo "$(YELLOW)下一步: 在 GitHub 创建仓库并执行:$(NC)"
	@echo "  git remote add origin https://github.com/qeasy/qdata-adapter-jky.git"
	@echo "  git push -u origin main"

git-first-commit: ## 初次提交（初始化Git并提交）
	@if [ -d .git ]; then \
		echo "$(YELLOW)Git 仓库已存在，执行常规提交...$(NC)"; \
		git add .; \
		git commit -m "feat: initial adapter implementation"; \
	else \
		echo "$(BLUE)初始化 Git 仓库...$(NC)"; \
		git init; \
		git add .; \
		git commit -m "chore: initial commit"; \
		echo "$(GREEN)✓ 初次提交完成$(NC)"; \
	fi
	@echo "$(YELLOW)下一步:$(NC)"
	@echo "  1. 在 GitHub 创建仓库: https://github.com/new"
	@echo "  2. git remote add origin https://github.com/YOUR_USERNAME/qdata-adapter-jky.git"
	@echo "  3. git push -u origin main"

.DEFAULT_GOAL := help