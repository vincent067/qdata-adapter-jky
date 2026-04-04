# JkyAdapter

<p align="center">
  <strong>QDataV2 jky 适配器</strong>
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

## 🚀 快速开始

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

---

## 📖 简介

`qdata-adapter-jky` 是 QDataV2 数据集成平台的官方适配器，用于连接 **jky** 平台。
### 多接口支持

本适配器支持多种接口模式，通过 `settings.interface` 参数切换：

| 接口 | 说明 | 认证方式 |
|------|------|---------|
| `standard`（默认） | 主接口 | 根据实现 |
| `qimen` | 备用接口 | 根据实现 |

> **注意**: 具体的接口名称和认证方式需要根据实际平台 API 文档进行配置。
> 
> 例如：
> - 吉客云: `standard` (标准REST) + `qimen` (奇门)
> - 金蝶: `openapi` (开放API) + `custom` (自定义)

---

## 🚀 快速开始

### 安装

```bash
pip install qdata-adapter-jky
```

### 基础用法

```python
import asyncio
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

async def main():
    # 创建连接器上下文
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

    # 初始化适配器
    adapter = JkyAdapter(context)

    # 测试连接
    result = await adapter.test_connection()
    print(f"连接状态: {result.status}")

    # 查询数据
    async for item in adapter.list_objects("orders", page_size=50):
        print(item)

asyncio.run(main())
```

---

## ⚙️ 配置说明

### auth_config 格式

根据接口类型不同，`auth_config` 格式可能不同：

```python
# 示例：OAuth2 认证
{
    "client_id": "应用 Key",
    "client_secret": "应用 Secret",
    "token_url": "https://api.example.com/oauth/token",
}

# 示例：API Key 认证
{
    "api_key": "your-api-key",
    "api_secret": "your-api-secret",
}

# 示例：Session 认证
{
    "username": "用户名",
    "password": "密码",
    "account_id": "账套 ID",
}
```

### settings 配置

```python
{
    "interface": "standard",  # "standard" 或 "qimen"
}
```

---

## 📚 API 文档

### JkyAdapter

适配器主类，继承自 `BaseAppAdapter`。

#### 方法

| 方法 | 说明 |
|------|------|
| `authenticate()` | 获取认证 Token |
| `refresh_token()` | 刷新 Token |
| `list_objects(type, filters, page_size)` | 列表查询（自动翻页） |
| `get_object(type, id)` | 单条查询 |
| `create_object(type, data)` | 创建对象 |
| `test_connection()` | 连接测试 |

---

## 🧪 测试

```bash
# 安装开发依赖
pip install -e ".[dev]"

# 运行测试（Mock 模式）
make test

# 使用真实 API 测试（需配置 .env）
USE_REAL_API=true make test

# 录制 HTTP 流量（用于调试）
RECORD_HTTP_TRAFFIC=true make test

# 运行测试（带覆盖率）
make test-cov

# 代码检查
make check
```

### 测试配置

1. 复制 `.env.example` 为 `.env`
2. 填入真实 API 凭据
3. 运行 `USE_REAL_API=true pytest tests/ -v`

⚠️ **注意**: 真实 API 测试会产生实际调用！

测试数据保存在 `tests/data/recordings/`（已配置为 Git 忽略）

---

## 📄 许可与商业政策
### 🔓 开源协议

本项目采用 **GNU Affero General Public License v3.0 (AGPL-3.0)** 开源协议。

- ✅ **个人学习/研究**：完全免费，无需授权
- ✅ **开源项目**：可自由使用，需遵守 AGPL-3.0 条款
- ✅ **修改与分发**：允许修改和重新分发，但必须保持开源

**重要**：如果你修改本软件并提供网络服务（包括内部使用），根据 AGPL-3.0 条款，你必须公开你的修改源代码。

### 💼 商业用途

任何**商业用途**必须单独购买商业许可。

**商业许可咨询**：📧 vincent@qeasy.cloud

### ⚠️ 重要提示

**未经授权的商业使用将构成版权侵权，我们保留追究法律责任的权利。**

---

## 🏢 关于轻易云数据集成平台

**广东轻亿云软件科技有限公司**  
专注数据集成与处理，提供企业级 ETL/ELT 解决方案  
🌐 官网：[https://www.qeasy.cloud](https://www.qeasy.cloud)  
📧 开源项目：opensource@qeasy.cloud  
📧 商业咨询：vincent@qeasy.cloud

---

*Powered by [广东轻亿云软件科技有限公司](https://www.qeasy.cloud)*