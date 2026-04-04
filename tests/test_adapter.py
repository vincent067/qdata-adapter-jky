"""
适配器测试

测试 JkyAdapter 的核心功能
"""

from typing import Any

import pytest
from pytest_httpx import HTTPXMock

from qdata_adapter_jky import JkyAdapter
from qdata_adapter import ConnectorContext


class TestJkyAdapter:
    """JkyAdapter 测试类"""

    @pytest.mark.asyncio
    async def test_adapter_initialization(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
    ) -> None:
        """测试适配器初始化"""
        adapter = JkyAdapter(standard_context, mock_token_cache)

        assert adapter.app_code == "jky"
        assert adapter.adapter_version == "0.1.0"
        assert adapter.context == standard_context

    @pytest.mark.asyncio
    async def test_authenticate_standard(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 standard 接口认证"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={
                "access_token": "test-token-123",
                "token_type": "Bearer",
                "expires_in": 7200,
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.authenticate()

        assert result["access_token"] == "test-token-123"
        assert result["token_type"] == "Bearer"
        assert result["expires_in"] == 7200

    @pytest.mark.asyncio
    async def test_list_objects_standard(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 standard 接口列表查询"""
        # Mock 认证
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        # Mock 列表接口
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/v1/orders?page=1&page_size=50",
            json={
                "data": [
                    {"id": "ORD001", "status": "completed"},
                    {"id": "ORD002", "status": "pending"},
                ],
                "pagination": {"total": 2, "page": 1, "page_size": 50},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        records = []
        async for record in adapter.list_objects("orders", page_size=50):
            records.append(record)

        assert len(records) == 2
        assert records[0]["id"] == "ORD001"
        assert records[1]["status"] == "pending"

    @pytest.mark.asyncio
    async def test_get_object_standard(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 standard 接口单条查询"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/v1/orders/ORD001",
            json={
                "data": {"id": "ORD001", "status": "completed", "amount": 100.0},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.get_object("orders", "ORD001")

        assert result["id"] == "ORD001"
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_create_object_standard(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 standard 接口创建对象"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/api/v1/orders",
            json={
                "data": {"id": "ORD003", "status": "created", "customer": "Test"},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.create_object("orders", {"customer": "Test"})

        assert result["id"] == "ORD003"
        assert result["status"] == "created"

    @pytest.mark.asyncio
    async def test_test_connection_success(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试连接测试 - 成功场景"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.test_connection()

        assert result.success is True
        assert result.status == "connected"

    @pytest.mark.asyncio
    async def test_test_connection_failure(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试连接测试 - 失败场景"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            status_code=401,
            json={"error": "invalid_client"},
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.test_connection()

        assert result.success is False
        assert result.status == "network_error"

    @pytest.mark.asyncio
    async def test_query_objects_standard(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 query_objects 方法（工作流节点优先使用）"""
        # Mock 认证
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        # Mock 列表接口
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/v1/products",
            json={
                "data": [
                    {"id": "PROD001", "name": "Product 1"},
                    {"id": "PROD002", "name": "Product 2"},
                ],
                "pagination": {"total": 2, "page": 1, "page_size": 50},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        records = []
        async for record in adapter.query_objects("products", page_size=50):
            records.append(record)

        assert len(records) == 2
        assert records[0]["id"] == "PROD001"

    @pytest.mark.asyncio
    async def test_invoke_query(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 invoke 方法 - query 操作"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/v1/customers",
            json={
                "data": [
                    {"id": "C001", "name": "Customer 1"},
                    {"id": "C002", "name": "Customer 2"},
                ],
                "pagination": {"total": 2, "page": 1, "page_size": 50},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.invoke("query", "customers", params={"status": "active"})

        assert "data" in result
        assert result["total"] == 2
        assert len(result["data"]) == 2

    @pytest.mark.asyncio
    async def test_invoke_get(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 invoke 方法 - get 操作"""
        httpx_mock.add_response(
            method="POST",
            url="https://api.example.com/oauth/token",
            json={"access_token": "token", "expires_in": 7200},
        )
        httpx_mock.add_response(
            method="GET",
            url="https://api.example.com/api/v1/items/ITEM001",
            json={
                "data": {"id": "ITEM001", "name": "Test Item", "price": 99.9},
            },
        )

        adapter = JkyAdapter(standard_context, mock_token_cache)
        result = await adapter.invoke("get", "items", params={"id": "ITEM001"})

        assert "data" in result
        assert result["data"]["id"] == "ITEM001"

    @pytest.mark.asyncio
    async def test_get_interface_info(
        self,
        standard_context: ConnectorContext,
        mock_token_cache: Any,
    ) -> None:
        """测试获取接口信息"""
        adapter = JkyAdapter(standard_context, mock_token_cache)
        info = adapter.get_interface_info()

        assert "interface_name" in info
        assert "available_interfaces" in info
        assert info["adapter_version"] == "0.1.0"
        assert info["app_code"] == "jky"

    @pytest.mark.asyncio
    async def test_qimen_interface_routing(
        self,
        qimen_context: ConnectorContext,
        mock_token_cache: Any,
    ) -> None:
        """测试 qimen 接口路由"""
        adapter = JkyAdapter(qimen_context, mock_token_cache)
        info = adapter.get_interface_info()

        assert info["interface_name"] == "qimen"
        assert "qimen" in info["available_interfaces"]

    @pytest.mark.asyncio
    async def test_qimen_authenticate(
        self,
        qimen_context: ConnectorContext,
        mock_token_cache: Any,
        httpx_mock: HTTPXMock,
    ) -> None:
        """测试 qimen 接口认证"""
        # qimen 接口可能使用不同的认证方式
        httpx_mock.add_response(
            method="POST",
            url="https://api-alt.example.com/gateway",
            json={
                "response": {
                    "code": 0,
                    "data": {"authenticated": True},
                },
            },
        )

        adapter = JkyAdapter(qimen_context, mock_token_cache)
        result = await adapter.authenticate()

        assert result["authenticated"] is True