# jky API 文档

> 官方 API 文档和接口参考

## 文档来源

### 官方文档
- **官方文档地址**: https://open.jackyun.com/developer/document.html?alias=outsystem_openplat
- **API 参考**: https://open.jackyun.com/developer/apidocinfo.html?from=self&value=undefined&id=oms.trade.fullinfoget&name=true
- **开发者中心**: [请填写开发者中心 URL]

### 本目录文件说明

```
api-docs/
├── README.md                 # 本文件
├── openapi.yaml             # OpenAPI/Swagger 定义（如有）
├── postman-collection.json  # Postman 集合（如有）
├── scraped/                 # 爬取的网页文档
│   ├── official-api-reference.md
│   └── authentication-guide.md
└── examples/                # 官方示例
    └── sample-requests.md
```

## 接口概览

### 认证方式

| 方式 | 端点 | 说明 |
|------|------|------|
| OAuth2 | [请填写] | 客户端凭证模式 |
| API Key | [请填写] | Header 传参 |
| HMAC | [请填写] | 签名验证 |

### 主要接口

#### 1. [接口分类一]

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/xxx` | [说明] |
| POST | `/api/v1/xxx` | [说明] |

#### 2. [接口分类二]

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/api/v1/yyy` | [说明] |
| POST | `/api/v1/yyy` | [说明] |

## 爬取文档

### 命令参考

如需爬取官方文档：

```bash
# 使用 Firecrawl 爬取
cd api-docs/scraped
firecrawl scrape https://docs.example.com/api-reference

# 或使用 wget
wget --mirror --convert-links --adjust-extension --page-requisites --no-parent https://docs.example.com/api-reference
```

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| [日期] | [版本] | [内容] |