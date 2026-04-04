# JkyAdapter 快速开始

> 5 分钟上手 jky 适配器

## 目录

1. [安装](#1-安装)
2. [配置](#2-配置)
3. [基础用法](#3-基础用法)
4. [测试](#4-测试)
5. [常见问题](#5-常见问题)

---

## 1. 安装

### 从 PyPI 安装（发布后）

```bash
pip install qdata-adapter-jky
```

### 从源码安装（开发）

```bash
git clone https://github.com/qeasy/qdata-adapter-jky.git
cd qdata-adapter-jky
pip install -e ".[dev]"
```

---

## 2. 配置

### 2.1 环境变量（推荐）

复制示例环境文件：

```bash
cp .env.example .env
```

编辑 `.env` 填入你的凭据：

```bash
# standard 接口认证
JKY_CLIENT_ID=your-client-id
JKY_CLIENT_SECRET=your-client-secret
JKY_BASE_URL=https://api.example.com
```

如需使用 qimen 接口：

```bash
# qimen 接口认证
JKY_APP_KEY=your-app-key
JKY_APP_SECRET=your-app-secret
JKY_CUSTOMER_ID=your-customer-id
```

### 2.2 代码中配置

```python
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

context = ConnectorContext(
    connector_id="my-connector",
    app_software_code="jky",
    base_url="https://api.example.com",
    auth_config={
        "client_id": "your-client-id",
        "client_secret": "your-client-secret",
    },
    settings={"interface": "standard"},  # 或 "qimen"
)
```

---

## 3. 基础用法

### 3.1 初始化适配器

```python
import asyncio
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

async def main():
    context = ConnectorContext(
        connector_id="demo",
        app_software_code="jky",
        base_url="https://api.example.com",
        auth_config={
            "client_id": "your-client-id",
            "client_secret": "your-client-secret",
        },
    )
    
    adapter = JkyAdapter(context)
    
    # 测试连接
    result = await adapter.test_connection()
    print(f"连接状态: {result.status}")

asyncio.run(main())
```

### 3.2 查询数据

```python
# 查询列表
async for item in adapter.list_objects("orders", filters={"status": "pending"}):
    print(f"订单: {item['id']}")

# 查询单条
order = await adapter.get_object("orders", "ORD001")
print(f"订单详情: {order}")
```

### 3.3 创建数据

```python
result = await adapter.create_object("orders", {
    "customer": "张三",
    "amount": 100.0,
    "items": [
        {"sku": "SKU001", "quantity": 2},
    ],
})
print(f"创建成功: {result['id']}")
```

### 3.4 使用 invoke() 灵活调用

对于平台特有 API 或复杂场景：

```python
# 查询列表（灵活方式）
result = await adapter.invoke(
    method="query",
    object_type="orders",
    params={"status": "pending", "page": 1}
)
print(f"共 {result['total']} 条记录")

# 获取单条
result = await adapter.invoke(
    method="get",
    object_type="orders",
    params={"id": "ORD001"}
)

# 创建对象
result = await adapter.invoke(
    method="create",
    object_type="orders",
    data={"customer": "张三", "amount": 100}
)

# 调用平台特有 API
result = await adapter.invoke(
    method="jky.goods.batchupdateflag",
    object_type="goods",
    data={"goods_ids": ["1", "2"], "flag": 1}
)
```

### 3.5 切换接口

```python
# 使用 qimen 接口
context = ConnectorContext(
    ...,
    settings={"interface": "qimen"},
    auth_config={
        "app_key": "your-app-key",
        "app_secret": "your-app-secret",
    },
)
adapter = JkyAdapter(context)
```

---

## 4. 测试

### 4.1 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_adapter.py::TestJkyAdapter::test_authenticate -v

# 使用真实 API 测试（需配置 .env）
USE_REAL_API=true pytest tests/ -v

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true pytest tests/ -v
```

### 4.2 配置真实 API 测试

1. 复制 `.env.example` 为 `.env`
2. 填入真实凭据
3. 运行测试：

```bash
USE_REAL_API=true pytest tests/test_adapter.py -v
```

⚠️ **注意**: 真实 API 测试会产生实际调用，请谨慎使用！

---

## 5. 常见问题

### Q: 如何获取 API 凭据？

A: 请访问 [官方开发者中心](https://docs.example.com) 申请应用，获取 client_id 和 client_secret。

### Q: 支持哪些 Python 版本？

A: Python 3.11, 3.12, 3.13

### Q: 如何处理分页？

A: `list_objects()` 方法自动处理分页，使用 AsyncIterator 逐条返回：

```python
async for item in adapter.list_objects("orders", page_size=100):
    # 自动处理翻页，无需关心 offset/page
    process(item)
```

### Q: 如何调试 API 调用？

A: 启用 HTTP 流量录制：

```bash
RECORD_HTTP_TRAFFIC=true pytest tests/ -v
# 记录保存在 tests/data/recordings/
```

### Q: 两个接口有什么区别？

| 特性 | standard | qimen |
|------|-------------------|---------------------|
| 认证方式 | OAuth2 / API Key | HMAC 签名 |
| 适用场景 | 标准 REST API | 专用网关/开放平台 |
| 性能 | 一般 | 针对大批量优化 |

---

## 下一步

- 查看完整 [API 文档](api-docs/README.md)
- 阅读 [开发指南](CONTRIBUTING.md)
- 了解 [架构设计](../docs/APP-INTEGRATION/adapter-development.md)

---

**遇到问题？** 请提交 [GitHub Issue](https://github.com/qeasy/qdata-adapter-jky/issues)