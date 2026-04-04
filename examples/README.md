# 示例代码

此目录包含 jky 适配器的使用示例。

## 文件说明

| 文件 | 说明 |
|------|------|
| `quickstart.py` | 快速开始示例，展示基础用法 |

## 运行示例

### 1. 配置环境变量

```bash
cp ../.env.example .env
# 编辑 .env 填入你的 API 凭据
```

### 2. 运行示例

```bash
# 进入示例目录
cd examples

# 运行快速开始示例
python quickstart.py
```

### 3. 使用真实 API（可选）

如需使用真实 API 测试：

```bash
# 确保 .env 中配置了真实凭据
export USE_REAL_API=true
python quickstart.py
```

## 示例输出

```
🔗 连接到: https://api.example.com
🆔 Client ID: test-cli...

📡 测试连接...
✅ 连接成功! (125ms)
   接口: standard

📋 查询数据示例...
   获取订单列表（前 5 条）:
   - 订单 ORD001: pending
   - 订单 ORD002: completed
   - 订单 ORD003: processing

🎯 使用 invoke() 灵活调用:
   查询到 42 个产品

✨ 示例完成!
```

## 编写自己的代码

参考 `quickstart.py` 创建你的应用：

```python
import asyncio
from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext

async def my_app():
    context = ConnectorContext(...)
    adapter = JkyAdapter(context)
    
    # 你的业务逻辑
    async for item in adapter.list_objects("orders"):
        process(item)

asyncio.run(my_app())
```