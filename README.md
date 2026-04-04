# JkyAdapter

<p align="center">
  <strong>QDataV2 吉客云（Jky）数据集成适配器</strong>
</p>

<p align="center">
  由 <a href="https://www.qeasy.cloud">广东轻亿云软件科技有限公司</a> 开发<br>
  「轻易云数据集成平台」官方适配器
</p>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPL%20v3-blue.svg" alt="License: AGPL v3"></a>
  <a href="https://pypi.org/project/qdata-adapter-jky/"><img src="https://img.shields.io/pypi/v/qdata-adapter-jky.svg" alt="PyPI version"></a>
  <a href="https://github.com/qeasy/qdata-adapter-jky/actions/workflows/ci.yml"><img src="https://github.com/qeasy/qdata-adapter-jky/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
</p>

---

## 功能作用

本适配器用于集成 **吉客云开放平台**（https://open.jackyun.com/），通过 `invoke()` 方法可调用吉客云提供的全部 API 接口，包括但不限于：

- 供应商管理（查询、创建、更新、停用）
- 订单数据同步
- 商品信息管理
- 库存数据查询
- 客户管理
- 财务对账
- 更多 API...

## 多接口支持

本适配器支持多种接口模式，通过 `settings.interface` 参数切换：

| 接口 | 说明 | 适用场景 |
|------|------|---------|
| `standard`（默认） | 主接口 | 标准业务集成 |
| `qimen` | 奇门网关接口 | 特殊网关需求 |

## 统一调用方式

使用 `invoke()` 方法可调用吉客云平台的任意 API：

```python
# 查询列表
result = await adapter.invoke(
    method="query",
    object_type="oms.trade.fullinfoget",
    params={"pageNo": 1, "pageSize": 100}
)

# 获取单个对象
result = await adapter.invoke(
    method="get",
    object_type="erp.vend.get",
    params={"code": "VENDOR_001"}
)

# 创建对象
result = await adapter.invoke(
    method="create",
    object_type="erp.vend.create.v2",
    data={"code": "NEW_VENDOR", "name": "新供应商", ...}
)

# 更新对象
result = await adapter.invoke(
    method="update",
    object_type="erp.vend.update",
    data={"vendId": "123", "name": "更新后的名称", ...}
)
```

## 快速开始

查看 [QUICKSTART.md](QUICKSTART.md) 获取 5 分钟上手指南。

```bash
# 安装
pip install qdata-adapter-jky

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的 API 凭据

# 运行示例
python examples/quickstart.py
```

## API 文档

- 吉客云开放平台：https://open.jackyun.com/
- 轻易云官网：https://www.qeasy.cloud

## 认证配置

### Standard 接口

| 环境变量 | 说明 |
|----------|------|
| `JKY_APP_KEY` | 应用密钥 |
| `JKY_APP_SECRET` | 应用密码 |
| `JKY_TOKEN` | 访问令牌 |
| `JKY_VERSION` | API 版本（默认 1.0） |

### Qimen 接口

| 环境变量 | 说明 |
|----------|------|
| `JKY_QIMEN_APP_KEY` | 应用密钥 |
| `JKY_QIMEN_APP_SECRET` | 应用密码 |
| `JKY_QIMEN_JKY_APP_KEY` | 吉客云应用 Key |
| `JKY_QIMEN_JKY_APP_SECRET` | 吉客云应用密钥 |
| `JKY_QIMEN_CUSTOMER_ID` | 吉客云客户 ID |

## License

AGPL-3.0 © 广东轻亿云软件科技有限公司
