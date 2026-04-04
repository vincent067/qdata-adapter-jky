#!/usr/bin/env python3
"""
JkyAdapter 快速开始示例

运行前请确保：
1. 已安装适配器: pip install -e .
2. 已配置环境变量 (.env 文件已存在)

官方文档: https://open.jackyun.com/developer/document.html?alias=outsystem_openplat
"""

import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext


async def main():
    """主函数"""

    # 获取配置
    interface_type = os.getenv("JKY_DEFAULT_INTERFACE", "standard")

    if interface_type == "qimen":
        # 奇门接口配置
        base_url = os.getenv("JKY_QIMEN_HOST", "https://zci2vl4joy.api.taobao.com/router/qm")
        auth_config = {
            "app_key": os.getenv("JKY_QIMEN_APP_KEY", ""),
            "app_secret": os.getenv("JKY_QIMEN_APP_SECRET", ""),
            "target_app_key": os.getenv("JKY_QIMEN_TARGET_APP_KEY", ""),
            "jkyappkey": os.getenv("JKY_QIMEN_JKY_APP_KEY", ""),
            "jkyappsecret": os.getenv("JKY_QIMEN_JKY_APP_SECRET", ""),
            "jkycustomerid": os.getenv("JKY_QIMEN_CUSTOMER_ID", ""),
        }
    else:
        # 标准接口配置
        base_url = os.getenv("JKY_STANDARD_HOST", "https://open.jackyun.com/open/openapi/do")
        auth_config = {
            "AppKey": os.getenv("JKY_APP_KEY", ""),
            "AppSecret": os.getenv("JKY_APP_SECRET", ""),
            "token": os.getenv("JKY_TOKEN", ""),
            "version": os.getenv("JKY_VERSION", "1.0"),
        }

    print(f"🔗 接口类型: {interface_type}")
    print(f"🔗 连接到: {base_url}")

    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="jky-quickstart",
        app_software_code="jky",
        base_url=base_url,
        auth_config=auth_config,
        settings={"interface": interface_type},
        environment=os.getenv("JKY_ENVIRONMENT", "sandbox"),
    )

    # 初始化适配器
    adapter = JkyAdapter(context)

    try:
        # 初始化
        print("\n📡 初始化适配器...")
        await adapter.initialize()
        print("✅ 初始化成功!")

        # 1. 认证
        print("\n🔐 认证中...")
        token = await adapter.authenticate()
        print(f"✅ 认证成功!")
        print(f"   AppKey: {auth_config.get('AppKey', auth_config.get('app_key', ''))[:8]}...")

        # 2. 获取适配器信息
        print("\n📋 适配器信息:")
        info = adapter.get_info()
        for key, value in info.items():
            print(f"   {key}: {value}")

        # 3. 获取接口信息
        print("\n🔌 接口信息:")
        interface_info = adapter.get_interface_info()
        for key, value in interface_info.items():
            print(f"   {key}: {value}")

        # 4. 健康检查
        print("\n🏥 健康检查...")
        is_healthy = await adapter.health_check()
        print(f"   {'✅ 健康' if is_healthy else '❌ 不健康'}")

        # 5. 使用 invoke() 查询数据
        print("\n🎯 使用 invoke() 查询订单:")
        result = await adapter.invoke(
            method="query",
            object_type="oms.trade.fullinfoget",
            params={"pageNo": 1, "pageSize": 3}
        )
        total = result.get('total', 0)
        print(f"   查询到 {total} 条数据")

        # 6. 使用 list_objects() 查询
        print("\n📦 使用 list_objects() 查询订单:")
        count = 0
        async for trade in adapter.list_objects("oms.trade.fullinfoget", page_size=3):
            print(f"   - 订单: {trade.get('tradeNo', trade.get('id', 'N/A'))}")
            count += 1
            if count >= 3:
                break
        print(f"   共获取 {count} 条数据")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        print("\n💡 提示:")
        print("   1. 确保 .env 文件配置正确")
        print("   2. 检查网络连接")
        print("   3. 查看 api-docs/ 了解 API 详情")

    print("\n✨ 示例完成!")


if __name__ == "__main__":
    asyncio.run(main())
