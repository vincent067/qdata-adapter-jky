# JkyAdapter 快速开始

> 5 分钟上手 jky 适配器

## 目录

1. [安装](#1-安装)
2. [配置](#2-配置)
3. [基础用法](#3-基础用法)
4. [奇门接口使用指南](#4-奇门接口使用指南)
5. [测试](#5-测试)
6. [常见问题](#6-常见问题)

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

#### Standard 接口配置

```bash
# standard 接口认证
JKY_APP_KEY=your-app-key
JKY_APP_SECRET=your-app-secret
JKY_TOKEN=your-token
JKY_VERSION=1.0
```

#### Qimen 接口配置

```bash
# qimen 接口认证（用于淘系订单对接）
JKY_QIMEN_HOST=https://zci2vl4joy.api.taobao.com/router/qm
JKY_QIMEN_APP_KEY=your-qimen-app-key
JKY_QIMEN_APP_SECRET=your-qimen-app-secret
JKY_QIMEN_TARGET_APP_KEY=your-target-app-key
JKY_QIMEN_JKY_APP_KEY=your-jky-app-key
JKY_QIMEN_JKY_APP_SECRET=your-jky-app-secret
JKY_QIMEN_CUSTOMER_ID=your-customer-id
```

### 2.2 代码中配置

#### Standard 接口

```python
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

context = ConnectorContext(
    connector_id="my-connector",
    app_software_code="jky",
    base_url="https://open.jackyun.com/open/openapi/do",
    auth_config={
        "AppKey": "your-app-key",
        "AppSecret": "your-app-secret",
        "token": "your-token",
        "version": "1.0",
    },
    settings={"interface": "standard"},
)
```

#### Qimen 接口

```python
context = ConnectorContext(
    connector_id="my-qimen-connector",
    app_software_code="jky",
    base_url="https://zci2vl4joy.api.taobao.com/router/qm",
    auth_config={
        "app_key": "your-qimen-app-key",
        "app_secret": "your-qimen-app-secret",
        "target_app_key": "your-target-app-key",
        "jkyappkey": "your-jky-app-key",
        "jkyappsecret": "your-jky-app-secret",
        "jkycustomerid": "your-customer-id",
    },
    settings={"interface": "qimen"},
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

---

## 4. 奇门接口使用指南

### 4.1 什么是奇门接口

奇门接口是淘宝开放平台提供的企业级数据网关，用于 ERP 系统与淘系电商平台（淘宝、天猫等）的数据对接。吉客云通过奇门网关提供标准化的订单、商品、库存等数据接口。

### 4.2 奇门接口特点

- **双签名机制**：需要同时生成 `jkysign`（吉客云签名）和 `sign`（淘宝签名）
- **PHP 风格 JSON**：JSON 编码需要与 PHP `json_encode()` 保持一致（带空格）
- **专用网关**：使用独立的网关地址（`*.api.taobao.com`）

### 4.3 完整调用示例

```python
import asyncio
from datetime import datetime, timedelta
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

async def query_qimen_orders():
    """使用奇门接口查询订单"""
    
    # 1. 配置奇门接口
    context = ConnectorContext(
        connector_id="qimen-orders",
        app_software_code="jky",
        base_url="https://zci2vl4joy.api.taobao.com/router/qm",
        auth_config={
            "app_key": "your-qimen-app-key",
            "app_secret": "your-qimen-app-secret",
            "target_app_key": "your-target-app-key",
            "jkyappkey": "your-jky-app-key",
            "jkyappsecret": "your-jky-app-secret",
            "jkycustomerid": "your-customer-id",
        },
        settings={"interface": "qimen"},
    )
    
    # 2. 创建适配器
    adapter = JkyAdapter(context)
    
    # 3. 测试连接
    health = await adapter.test_connection()
    print(f"连接状态: {health.status}")
    
    # 4. 构建查询参数
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)
    
    query_params = {
        "tradeNo": "",
        "pageSize": "200",
        "pageIndex": 1,
        "hasTotal": "1",
        "startConsignTime": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "endConsignTime": end_time.strftime("%Y-%m-%d %H:%M:%S"),
        "tradeStatus": "",
        "tradeType": "1",
        "sourceTradeNos": "",
        "fields": "checkTotal,tradeNo,postFee,otherFee,chargeCurrency,accountName,payType,payNo,sellerMemo,buyerMemo,goodsDetail"
    }
    
    # 5. 调用 API
    result = await adapter.invoke(
        method="query",
        object_type="jackyun.tradenotsensitiveinfos.list.get",
        params=query_params
    )
    
    # 6. 处理结果
    if "data" in result:
        orders = result["data"]
        total = result.get("total", len(orders))
        print(f"查询到 {total} 条订单")
        
        for order in orders[:5]:  # 打印前5条
            print(f"订单号: {order.get('tradeNo')}, 状态: {order.get('tradeStatus')}")
    
    return result

# 运行
asyncio.run(query_qimen_orders())
```

### 4.4 常用奇门 API

| API 名称 | 说明 |
|----------|------|
| `jackyun.tradenotsensitiveinfos.list.get` | 查询订单列表（脱敏） |
| `jackyun.trade.fullinfo.get` | 查询订单详情 |
| `jackyun.goods.list.get` | 查询商品列表 |
| `jackyun.inventory.query` | 查询库存 |

> ⚠️ **注意**：具体的 API 名称需要从吉客云技术支持获取，不同账号的 API 前缀可能不同。

### 4.5 参数说明

#### 查询参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `pageSize` | string | 是 | 每页记录数，最大 200 |
| `pageIndex` | int | 是 | 页码，从 1 开始 |
| `startConsignTime` | string | 是 | 开始时间（格式：yyyy-MM-dd HH:mm:ss） |
| `endConsignTime` | string | 是 | 结束时间（格式：yyyy-MM-dd HH:mm:ss） |
| `tradeType` | string | 否 | 订单类型 |
| `fields` | string | 否 | 返回字段列表，逗号分隔 |

#### 返回字段示例

```
checkTotal,tradeNo,postFee,otherFee,chargeCurrency,accountName,payType,
payNo,sellerMemo,buyerMemo,goodsDetail,goodsDetail.goodsNo,
goodsDetail.goodsName,goodsDetail.specName,goodsDetail.barcode,
goodsDetail.sellCount,goodsDetail.sellPrice
```

---

## 5. 测试

### 5.1 运行测试

```bash
# 运行所有测试
make test

# 运行特定测试
pytest tests/test_adapter.py::TestJkyAdapter::test_authenticate -v

# 运行奇门接口签名测试
pytest tests/test_qimen_signature.py -v

# 使用真实 API 测试（需配置 .env）
USE_REAL_API=true pytest tests/ -v

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true pytest tests/ -v
```

### 5.2 配置真实 API 测试

1. 复制 `.env.example` 为 `.env`
2. 填入真实凭据
3. 运行测试：

```bash
USE_REAL_API=true pytest tests/test_adapter.py -v
```

⚠️ **注意**: 真实 API 测试会产生实际调用，请谨慎使用！

---

## 6. 常见问题

### Q: 如何获取 API 凭据？

A: 请访问 [吉客云开放平台](https://open.jackyun.com/) 申请应用，获取相应的 API 凭据。

### Q: Standard 和 Qimen 接口有什么区别？

A: 

| 特性 | Standard | Qimen |
|------|----------|-------|
| 认证方式 | Token + Sign | 双签名（jkysign + taobao sign） |
| 适用场景 | 标准业务接口 | 淘系订单、奇门网关 |
| 接入门槛 | 较低 | 需要淘宝开放平台资质 |
| 数据范围 | 吉客云内部数据 | 淘系电商数据 |

### Q: 奇门接口返回 "Invalid method" 怎么办？

A: 
1. 确认 API 方法名正确（联系吉客云技术支持获取）
2. 检查 `target_app_key` 配置是否正确
3. 确认账号有权限访问该 API

### Q: 奇门接口签名错误怎么办？

A:
1. 检查 `jkyappkey` 和 `jkyappsecret` 是否正确
2. 确认 JSON 编码格式（应该是 PHP 风格，带空格）
3. 检查时间戳格式（`yyyy-MM-dd HH:mm:ss`）

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

---

## 下一步

- 查看完整 [API 文档](api-docs/README.md)
- 阅读 [开发指南](CONTRIBUTING.md)
- 了解 [架构设计](../docs/APP-INTEGRATION/adapter-development.md)

---

**遇到问题？** 请提交 [GitHub Issue](https://github.com/qeasy/qdata-adapter-jky/issues)
