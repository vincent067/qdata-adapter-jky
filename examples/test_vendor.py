#!/usr/bin/env python3
"""
供应商接口测试脚本

测试供应商的增删改查功能。
WARNING: 这是真实环境，请务必小心！

运行前请确保：
1. 已安装适配器: pip install -e .
2. 已配置环境变量 (.env 文件已存在)

接口文档: api-docs/Jky/details/
"""

import asyncio
import os
import time
import random
import string

from dotenv import load_dotenv

load_dotenv()

from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext


def generate_test_code(prefix: str = "TEST") -> str:
    """生成测试用的唯一编码"""
    timestamp = int(time.time())
    random_str = ''.join(random.choices(string.ascii_uppercase, k=4))
    return f"{prefix}_{timestamp}_{random_str}"


async def test_vendor_get(adapter: JkyAdapter, code: str):
    """测试查询供应商"""
    print(f"\n📋 测试 erp.vend.get 查询供应商...")
    print(f"   查询编码: {code}")

    try:
        result = await adapter.invoke(
            method="get",
            object_type="erp.vend.get",
            params={"code": code}  # 使用 code 参数查询
        )
        print(f"   ✅ 查询成功!")
        print(f"   返回数据: {result}")
        return result
    except Exception as e:
        print(f"   ❌ 查询失败: {e}")
        return None


async def test_vendor_create(adapter: JkyAdapter, code: str):
    """测试创建供应商"""
    print(f"\n📝 测试 erp.vend.create.v2 创建供应商...")
    print(f"   供应商编码: {code}")

    # 构造创建数据
    create_data = {
        "code": code,
        "name": f"测试供应商_{code}",
        "className": "默认分类",  # 必填
        "classId": 1,
        "countryName": "中国",
        "provinceName": "浙江省",
        "cityName": "杭州市",
        "address": "测试地址",
        "tel": "13800138000",
        "email": "test@example.com",
        "memo": f"这是自动化测试创建的供应商 {time.strftime('%Y-%m-%d %H:%M:%S')}",
    }

    print(f"   创建数据: {create_data}")

    try:
        result = await adapter.invoke(
            method="create",
            object_type="erp.vend.create.v2",
            data=create_data
        )
        print(f"   ✅ 创建成功!")
        print(f"   返回数据: {result}")
        return result
    except Exception as e:
        print(f"   ❌ 创建失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_vendor_update(adapter: JkyAdapter, code: str, vend_id: str):
    """测试更新供应商"""
    print(f"\n📝 测试 erp.vend.update 更新供应商...")
    print(f"   供应商编码: {code}")
    print(f"   供应商ID: {vend_id}")

    # 构造更新数据（注意：vendId 需要在 data 中）
    update_data = {
        "code": code,
        "vendId": vend_id,
        "name": f"测试供应商_{code}_已更新",
        "className": "默认分类",
        "memo": f"更新于 {time.strftime('%Y-%m-%d %H:%M:%S')}",
    }

    print(f"   更新数据: {update_data}")

    try:
        result = await adapter.invoke(
            method="update",
            object_type="erp.vend.update",
            data=update_data
        )
        print(f"   ✅ 更新成功!")
        print(f"   返回数据: {result}")
        return result
    except Exception as e:
        print(f"   ❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_vendor_blockup(adapter: JkyAdapter, code: str):
    """测试停用供应商"""
    print(f"\n🔴 测试 erp.vend.blockup 停用供应商...")
    print(f"   供应商编码: {code}")

    try:
        result = await adapter.invoke(
            method="create",  # blockup 使用 create 方法调用
            object_type="erp.vend.blockup",
            data={"code": code}
        )
        print(f"   ✅ 停用成功!")
        print(f"   返回数据: {result}")
        return result
    except Exception as e:
        print(f"   ❌ 停用失败: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""

    # 获取配置
    interface_type = os.getenv("JKY_DEFAULT_INTERFACE", "standard")
    environment = os.getenv("JKY_ENVIRONMENT", "sandbox")

    print(f"⚠️  警告：这是{'生产' if environment == 'production' else '沙盒'}环境测试!")
    print(f"🔗 接口类型: {interface_type}")

    if interface_type == "qimen":
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
        base_url = os.getenv("JKY_STANDARD_HOST", "https://open.jackyun.com/open/openapi/do")
        auth_config = {
            "AppKey": os.getenv("JKY_APP_KEY", ""),
            "AppSecret": os.getenv("JKY_APP_SECRET", ""),
            "token": os.getenv("JKY_TOKEN", ""),
            "version": os.getenv("JKY_VERSION", "1.0"),
        }

    print(f"🔗 连接到: {base_url}")

    # 创建连接器上下文
    context = ConnectorContext(
        connector_id="jky-vendor-test",
        app_software_code="jky",
        base_url=base_url,
        auth_config=auth_config,
        settings={"interface": interface_type},
        environment=environment,
    )

    # 初始化适配器
    adapter = JkyAdapter(context)

    try:
        # 初始化
        print("\n📡 初始化适配器...")
        await adapter.initialize()
        print("✅ 初始化成功!")

        # 认证
        print("\n🔐 认证中...")
        token = await adapter.authenticate()
        print(f"✅ 认证成功!")

        # 生成唯一的测试编码
        test_code = generate_test_code("VND")

        # =============================================
        # 步骤1: 查询供应商（测试 get 接口）
        # =============================================
        print("\n" + "="*50)
        print("步骤1: 测试 erp.vend.get 查询接口")
        print("="*50)

        # 先尝试查询一个已知编码的供应商
        existing_result = await test_vendor_get(adapter, "VENDOR_TEST_001")

        if existing_result and existing_result.get("data"):
            data = existing_result["data"]
            if isinstance(data, dict) and data.get("vendId"):
                print("   存在测试数据，可以使用")
                test_code = "VENDOR_TEST_001"
            else:
                print(f"   ⚠️ 查询结果无 vendId: {data}")
        else:
            print(f"   未找到现有测试数据，将创建新测试数据")

        # =============================================
        # 步骤2: 创建供应商（测试 create 接口）
        # =============================================
        print("\n" + "="*50)
        print("步骤2: 测试 erp.vend.create.v2 创建接口")
        print("="*50)

        create_result = await test_vendor_create(adapter, test_code)

        vend_id = None
        if create_result and create_result.get("data"):
            vend_data = create_result["data"]
            if isinstance(vend_data, dict):
                vend_id = vend_data.get("vendId")
            print(f"   创建的供应商ID: {vend_id}")

        # =============================================
        # 步骤3: 查询确认创建成功
        # =============================================
        if vend_id:
            print("\n" + "="*50)
            print("步骤3: 确认供应商创建成功")
            print("="*50)

            verify_result = await test_vendor_get(adapter, test_code)
            if verify_result and verify_result.get("data"):
                print("   ✅ 验证成功，供应商已创建!")
            else:
                print("   ⚠️ 验证失败，可能创建有问题")

            # =============================================
            # 步骤4: 更新供应商
            # =============================================
            print("\n" + "="*50)
            print("步骤4: 测试 erp.vend.update 更新接口")
            print("="*50)

            await test_vendor_update(adapter, test_code, vend_id)

            # =============================================
            # 步骤5: 停用供应商
            # =============================================
            print("\n" + "="*50)
            print("步骤5: 测试 erp.vend.blockup 停用接口")
            print("="*50)

            await test_vendor_blockup(adapter, test_code)
        else:
            print("\n⚠️ 无法获取供应商ID，跳过更新和停用测试")

        print("\n" + "="*50)
        print("✅ 测试完成!")
        print("="*50)

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()

    print("\n✨ 测试脚本完成!")


if __name__ == "__main__":
    asyncio.run(main())