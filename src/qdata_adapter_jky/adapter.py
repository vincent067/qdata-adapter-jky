"""
JkyAdapter

适配器主类 - 组合器模式实现
根据 settings.interface 自动路由到对应的接口实现：
- "standard": 主接口（默认）
- "qimen": 备用接口
"""

from __future__ import annotations

import logging
from typing import Any, AsyncIterator

from qdata_adapter import BaseAppAdapter
from qdata_adapter.context import ConnectorContext
from qdata_adapter.results import TestConnectionResult

from qdata_adapter_jky.interfaces.base import BaseInterface
from qdata_adapter_jky.interfaces.standard import JkyAdapterStandardInterface
from qdata_adapter_jky.interfaces.qimen import JkyAdapterQimenInterface

logger = logging.getLogger(__name__)


class JkyAdapter(BaseAppAdapter):
    """
    jky 适配器
    组合器模式，支持多接口切换：

    - settings.interface = "standard"（默认）
      → 使用 JkyAdapterStandardInterface

    - settings.interface = "qimen"
      → 使用 JkyAdapterQimenInterface

    双接口设计说明：

    某些平台提供多种 API 体系（如标准 REST + 专用网关），本适配器通过组合器
    模式统一对外接口，内部根据 settings.interface 路由到对应实现。

    开发者可根据实际平台修改：
    - 接口名称（如 "standard"/"qimen", "openapi"/"custom"）
    - 接口实现类
    - 认证方式

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="my-connector",
        ...     app_software_code="jky",
        ...     base_url="https://open.jackyun.com/open/openapi/do",
        ...     auth_config={
        ...         "AppKey": "xxx",
        ...         "AppSecret": "xxx",
        ...         "token": "xxx",
        ...         "version": "1.0",
        ...     },
        ...     settings={"interface": "standard"},
        ... )
        >>> adapter = JkyAdapter(context)
        >>> await adapter.initialize()
        >>> token = await adapter.authenticate()
    """

    app_code = "jky"
    adapter_version = "0.1.0"

    def __init__(self, context: ConnectorContext, token_cache: Any = None) -> None:
        """
        初始化适配器

        Args:
            context: 连接器上下文
            token_cache: Token 缓存（可选）

        Note:
            context.settings.interface 控制接口路由：
            - "standard"（默认）
            - "qimen"（如启用双接口）
        """
        super().__init__(context, token_cache)
        self._interface = self._resolve_interface()
        logger.debug(
            "Initialized JkyAdapter with %s interface",
            self._interface.interface_name
        )

    def _resolve_interface(self) -> BaseInterface:
        """
        根据 settings 路由到对应的接口实现

        Returns:
            接口实现实例
        """
        interface_type = self.context.settings.get("interface", "standard")

        if interface_type == "qimen":
            logger.debug("Using qimen interface")
            return JkyAdapterQimenInterface(
                self.context, self.http_client
            )
        else:
            # 默认使用主接口
            if interface_type != "standard":
                logger.warning(
                    "Unknown interface '%s', falling back to 'standard'",
                    interface_type
                )
            logger.debug("Using standard interface")
            return JkyAdapterStandardInterface(
                self.context, self.http_client
            )

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        委托给当前接口实现
        """
        return await self._interface.authenticate()

    async def refresh_token(self) -> dict[str, Any]:
        """
        刷新认证凭证

        委托给当前接口实现
        """
        # 对于大多数接口，refresh 与 authenticate 相同
        return await self._interface.authenticate()

    async def list_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        列表查询

        委托给当前接口实现
        """
        async for item in self._interface.list_objects(object_type, filters, page_size):
            yield item

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """
        获取单个对象

        委托给当前接口实现
        """
        return await self._interface.get_object(object_type, object_id)

    async def invoke(
        self,
        method: str,
        object_type: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        统一的 API 调用方法

        对于拥有成百上千个 API 的平台，此方法提供灵活的统一调用入口。
        支持任意 API 方法（query/get/create/update/delete 等），
        而不局限于 list_objects/get_object/create_object 三种操作。

        Args:
            method: API 方法名，如 "query", "get", "create", "update", "delete"
            object_type: 对象类型，如 "orders", "products"
            data: 请求体数据（用于 create/update 等）
            params: 查询参数（用于 query/get 等）

        Returns:
            API 响应数据

        Raises:
            JkyAdapterAuthError: 认证失败
            JkyAdapterAPIError: API 调用失败
            NotImplementedError: 方法不支持

        Example:
            >>> # 查询列表
            >>> result = await adapter.invoke(
            ...     "query", "orders",
            ...     params={"status": "pending"}
            ... )
            >>>
            >>> # 获取单条
            >>> result = await adapter.invoke(
            ...     "get", "orders",
            ...     params={"id": "ORD001"}
            ... )
            >>>
            >>> # 调用平台特有 API
            >>> result = await adapter.invoke(
            ...     "jky.goods.batchupdateflag",
            ...     "goods",
            ...     data={"goods_ids": ["1", "2"], "flag": 1}
            ... )
        """
        # 委托给接口实现
        if hasattr(self._interface, 'invoke'):
            return await self._interface.invoke(method, object_type, data, params)

        # 默认路由到标准方法
        if method in ("list", "query"):
            results = []
            async for item in self._interface.list_objects(
                object_type, filters=params, page_size=100
            ):
                results.append(item)
            return {"data": results, "total": len(results)}

        elif method == "get":
            object_id = params.get("id") if params else None
            if not object_id:
                raise ValueError("'get' method requires params['id']")
            result = await self._interface.get_object(object_type, object_id)
            return {"data": result}

        elif method == "create":
            if not data:
                raise ValueError("'create' method requires data")
            result = await self._interface.create_object(object_type, data)
            return {"data": result}

        else:
            raise NotImplementedError(
                f"Method '{method}' not implemented in interface. "
                f"Please override invoke() in your interface class or "
                f"implement a custom method handler."
            )

    async def test_connection(self) -> TestConnectionResult:
        """
        测试连接

        检查与 jky 平台的连接是否正常

        Returns:
            连接测试结果
        """
        import time

        start_time = time.time()

        try:
            await self._interface.health_check()
            return TestConnectionResult.connected(
                message=f"jky 连接成功",
                duration_ms=int((time.time() - start_time) * 1000),
                metadata={
                    "interface": self._interface.interface_name,
                    "base_url": self.context.base_url,
                },
            )
        except Exception as e:
            logger.error("Connection test failed: %s", e)
            return TestConnectionResult.network_error(
                message=str(e),
                duration_ms=int((time.time() - start_time) * 1000),
                details={"error": str(e)},
            )

    def get_interface_info(self) -> dict[str, Any]:
        """
        获取当前接口信息

        Returns:
            接口信息字典
        """
        return {
            "interface_name": self._interface.interface_name,
            "available_interfaces": ["standard", "qimen"],
            "adapter_version": self.adapter_version,
            "app_code": self.app_code,
        }


__all__ = ["JkyAdapter"]
