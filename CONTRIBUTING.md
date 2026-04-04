# 贡献指南

感谢您对 qdata-adapter-jky 项目的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告问题

如果您发现了 bug 或有功能建议，请在 [GitHub Issues](https://github.com/qeasy/qdata-adapter-jky/issues) 中提交。

提交问题时，请包含：

- 问题的详细描述
- 复现步骤
- 期望行为与实际行为
- 您的环境信息（Python 版本、操作系统等）

### 提交代码

1. **Fork 仓库**

   ```bash
   git clone https://github.com/qeasy/qdata-adapter-jky.git
   cd qdata-adapter-jky
   ```

2. **创建分支**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **设置开发环境**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   pre-commit install
   ```

4. **编写代码**

   - 遵循项目代码风格
   - 添加必要的测试
   - 更新相关文档

5. **运行测试**

   ```bash
   pytest
   ```

6. **代码检查**

   ```bash
   make check
   ```

7. **提交更改**

   ```bash
   git add .
   git commit -m "feat: 添加新功能描述"
   ```

8. **推送并创建 Pull Request**

   ```bash
   git push origin feature/your-feature-name
   ```

## 代码规范

- 使用 [Black](https://github.com/psf/black) 进行代码格式化
- 使用 [isort](https://github.com/PyCQA/isort) 进行导入排序
- 遵循 [PEP 8](https://pep8.org/) 代码风格
- 添加类型提示
- 编写清晰的文档字符串

## Commit 规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复 bug
- `docs:` 文档更新
- `style:` 代码风格调整（不影响功能）
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

## 许可证

您的贡献将遵循项目的 AGPL-3.0 许可证。

## 联系我们

如有任何问题，欢迎通过以下方式联系：

- GitHub Issues: https://github.com/qeasy/qdata-adapter-jky/issues
- 邮箱: opensource@qeasy.cloud

感谢您的贡献！ 🎉