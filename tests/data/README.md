# 测试数据目录

此目录用于存放测试相关的数据和记录。

## 目录结构

```
tests/data/
├── README.md           # 本文件
├── recordings/         # HTTP 请求/响应记录
│   ├── requests/       # 请求记录
│   └── responses/      # 响应记录
└── fixtures/           # 测试固件数据
    └── sample-data.json
```

## 说明

- **recordings/**: 测试运行时自动生成的 HTTP 流量记录
  - 用于调试和分析真实 API 交互
  - 不会被提交到 Git（已在 .gitignore 中排除）
  
- **fixtures/**: 手动维护的测试数据
  - 可被提交到 Git
  - 用于 Mock 测试

## 敏感信息警告

⚠️ **请勿将包含真实 API 密钥的请求/响应记录提交到 Git！**

该目录已配置为 Git 忽略，但请定期清理敏感数据。