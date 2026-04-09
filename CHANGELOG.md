# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-04-09

### Fixed
- 修复奇门接口签名算法，使 JSON 编码与 PHP `json_encode()` 保持一致
  - PHP 风格 JSON 在 `:` 和 `,` 后带空格，如 `{"pageNo": 1, "pageSize": 10}`
  - 移除 `orjson` 依赖，使用标准库 `json.dumps`
  - 修复 `None` 值处理，返回空字符串而非 `"null"`

### Added
- 新增奇门接口完整测试套件（12 个测试用例）
  - JSON 编码格式测试
  - jkysign 签名算法测试
  - 淘宝 sign 签名算法测试
  - 请求参数构建测试
  - PHP 兼容性测试
- 新增奇门接口完整文档
  - 配置参数说明
  - 使用示例代码
  - API 参数说明
  - 常见问题解答

### Changed
- 更新 `README.md`，添加奇门接口配置和示例
- 更新 `QUICKSTART.md`，添加奇门接口使用指南
- 更新 `tests/conftest.py`，完善 `qimen_auth_config` fixture

## [0.1.0] - 2026-04-04

### Initial Release
- Project scaffold generated
- Base adapter implementation
- CI/CD configuration
