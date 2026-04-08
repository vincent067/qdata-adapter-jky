# MIT License
#
# Copyright (c) 2024-2026 广东轻亿云软件科技有限公司
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
jky standard 接口实现

主接口实现，基于平台的标准 API。
参考旧PHP实现: JkySDKV2.php
"""

from __future__ import annotations

import hashlib
import json as _json
import logging
import time
from typing import TYPE_CHECKING, Any, AsyncIterator

from qdata_adapter.exceptions import AuthenticationError, NotFoundError, ValidationError

from qdata_adapter_jky.exceptions import JkyAdapterAPIError, JkyAdapterAuthError
from qdata_adapter_jky.interfaces.base import BaseInterface

if TYPE_CHECKING:
    from qdata_adapter.client import HttpClient
    from qdata_adapter.context import ConnectorContext

logger = logging.getLogger(__name__)


class JkyAdapterStandardInterface(BaseInterface):
    """
    jky standard 接口实现

    主要 API 接口，提供标准的数据访问能力。
    API文档: https://open.jackyun.com/developer/document.html?alias=outsystem_openplat

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="test",
        ...     app_software_code="jky",
        ...     base_url="https://open.jackyun.com/open/openapi/do",
        ...     auth_config={
        ...         "AppKey": "xxx",
        ...         "AppSecret": "xxx",
        ...         "token": "xxx",
        ...         "version": "1.0",
        ...     },
        ... )
        >>> interface = JkyAdapterStandardInterface(context, http_client)
    """

    interface_name = "standard"

    # 默认 API 基础地址
    DEFAULT_HOST = "https://open.jackyun.com/open/openapi/do"

    # 吉客云的数据键映射（从响应中提取列表数据）
    DATA_KEYS = [
        "stockTake",
        "returnChangeList",
        "stockAllocate",
        "goods",
        "salesChannelInfo",
        "warehouseInfo",
        "trades",
        "purchOrderReturn",
        "vendInfo",
        "goodsStockQuantity",
    ]

    def __init__(self, context: "ConnectorContext", http_client: "HttpClient") -> None:
        super().__init__(context, http_client)
        # 确定 API 端点
        self._host = self.context.base_url or self.DEFAULT_HOST

    def _generate_sign(self, api: str, bizcontent: str, timestamp: str) -> str:
        """
        生成请求签名

        签名算法：
        str = 'appkey' + AppKey + 'bizcontent' + bizcontent + 'contenttypeJSON'
              + 'method' + api + 'timestamp' + timestamp + 'version' + version
        sign = md5(lowercase(AppSecret + str + AppSecret))

        Args:
            api: API方法名
            bizcontent: JSON格式的请求参数
            timestamp: 时间戳

        Returns:
            签名字符串
        """
        auth_config = self.get_auth_config()
        app_key = auth_config.get("AppKey", "")
        app_secret = auth_config.get("AppSecret", "")
        version = auth_config.get("version", "1.0")

        sign_str = (
            f"appkey{app_key}"
            f"bizcontent{bizcontent}"
            f"contenttypeJSON"
            f"method{api}"
            f"timestamp{timestamp}"
            f"version{version}"
        )
        sign_str = app_secret + sign_str + app_secret
        return hashlib.md5(sign_str.lower().encode()).hexdigest()

    def _build_request_params(
        self, api: str, bizcontent: dict[str, Any] | None = None
    ) -> dict[str, str]:
        """
        构建请求参数

        Args:
            api: API方法名
            bizcontent: 业务参数

        Returns:
            请求参数字典
        """
        auth_config = self.get_auth_config()
        bizcontent_json = "" if bizcontent is None else json_dumps(bizcontent)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

        params = {
            "method": api,
            "appkey": auth_config.get("AppKey", ""),
            "version": auth_config.get("version", "1.0"),
            "contenttype": "json",
            "timestamp": timestamp,
            "bizcontent": bizcontent_json,
            "sign": self._generate_sign(api, bizcontent_json, timestamp),
        }

        # 添加 token（如果存在）
        token = auth_config.get("token")
        if token:
            params["token"] = token

        return params

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        Standard 接口使用预先分配的 token，无需额外认证请求。
        此方法仅验证配置是否完整。

        Returns:
            Token 信息

        Raises:
            JkyAdapterAuthError: 认证配置缺失
        """
        auth_config = self.get_auth_config()

        app_key = auth_config.get("AppKey")
        app_secret = auth_config.get("AppSecret")
        token = auth_config.get("token")

        missing = []
        if not app_key:
            missing.append("AppKey")
        if not app_secret:
            missing.append("AppSecret")
        if not token:
            missing.append("token")

        if missing:
            raise JkyAdapterAuthError(
                f"Missing required credentials: {', '.join(missing)}",
                details={"missing": missing},
            )

        logger.debug("Authentication configured for AppKey: %s", app_key[:8] + "...")
        return {
            "app_key": app_key,
            "token": token,
            "authenticated": True,
        }

    def _extract_list_data(self, response: dict[str, Any]) -> tuple[list[Any], int]:
        """
        从响应中提取列表数据

        Args:
            response: API 响应

        Returns:
            (数据列表, 总数)

        Raises:
            JkyAdapterAPIError: API 调用失败
        """
        # 检查错误码 - code=200 表示成功
        code = response.get("code") or response.get("jackyunCode")
        message = response.get("msg") or response.get("message", "")

        # 如果有明确的错误码且不为 200，认为是错误
        if code is not None and code != 200:
            # 如果 result.data 有数据，可能只是空结果，不算错误
            result = response.get("result") or response.get("jackyunData") or {}
            data = result.get("data") if isinstance(result, dict) else None

            if data is None or data == []:
                # 真正没有数据
                if code != 0:  # code=0 通常表示成功但无数据
                    raise JkyAdapterAPIError(
                        f"API error: {message}",
                        api_code=str(code),
                        details=response,
                    )
            else:
                # 有数据但 code 不是 200，可能需要处理
                pass

        # 尝试从 result.data 获取数据
        result = response.get("result") or response.get("jackyunData") or {}
        if result is None:
            return [], 0

        if not isinstance(result, dict):
            logger.warning("Unexpected response: result is not a dict: %s", type(result))
            return [], 0

        data = result.get("data")
        if data is None:
            return [], 0

        # 尝试从已知的数据键中提取列表
        for key in self.DATA_KEYS:
            if key in data:
                items = data[key]
                total = len(items) if isinstance(items, list) else 0
                return items, total

        # 如果 data 是列表，直接返回
        if isinstance(data, list):
            return data, len(data)

        # 如果是字典且没有匹配到已知键，返回空列表
        logger.warning("Unexpected response data format: %s", list(data.keys()) if isinstance(data, dict) else type(data))
        return [], 0

    def _extract_single_data(self, response: dict[str, Any]) -> dict[str, Any]:
        """
        从响应中提取单条数据

        Args:
            response: API 响应

        Returns:
            单条数据

        Raises:
            JkyAdapterAPIError: API 调用失败
        """
        # 检查错误码 - code=200 表示成功
        code = response.get("code") or response.get("jackyunCode")
        message = response.get("msg") or response.get("message", "")

        # 如果有明确的错误码且不为 200，认为是错误
        if code is not None and code != 200:
            result = response.get("result") or response.get("jackyunData") or {}
            data = result.get("data") if isinstance(result, dict) else None

            if data is None or data == {}:
                if code != 0:
                    raise JkyAdapterAPIError(
                        f"API error: {message}",
                        api_code=str(code),
                        details=response,
                    )

        # 尝试从 result.data 获取数据
        result = response.get("result") or response.get("jackyunData") or {}
        if result is None:
            return {}

        if not isinstance(result, dict):
            return {}

        data = result.get("data")
        if data is None:
            return {}

        # 如果是字典，直接返回
        if isinstance(data, dict):
            return data

        # 如果是列表，返回第一个元素或空字典
        if isinstance(data, list):
            return data[0] if data else {}

        return data

    async def list_objects(
        self,
        object_type: str,
        filters: dict[str, Any] | None = None,
        page_size: int = 100,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        列表查询（自动翻页）

        Args:
            object_type: 对象类型，如 "orders", "products"，对应 API method
            filters: 过滤条件
            page_size: 每页大小

        Yields:
            单条记录
        """
        filters = filters or {}
        page = 1
        has_more = True

        while has_more:
            # 构建分页参数
            params = {
                "pageNo": page,
                "pageSize": page_size,
                **filters,
            }

            try:
                request_params = self._build_request_params(object_type, params)

                response = await self.http_client.post(
                    self._host,
                    data=request_params,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                logger.debug("API Response for %s: %s", object_type, response)
                items, total = self._extract_list_data(response)

                for item in items:
                    yield item

                # 判断是否还有更多数据
                has_more = len(items) == page_size and (page * page_size) < total
                page += 1

            except Exception as e:
                logger.error("Failed to fetch %s list: %s", object_type, e)
                raise JkyAdapterAPIError(
                    f"Failed to list {object_type}",
                    details={"object_type": object_type, "page": page, "error": str(e)},
                ) from e

    async def get_object(self, object_type: str, object_id: str) -> dict[str, Any]:
        """
        获取单个对象

        Args:
            object_type: 对象类型，对应 API method
            object_id: 对象 ID

        Returns:
            对象数据

        Raises:
            NotFoundError: 对象不存在
        """
        # 对于单条查询，通常需要传入 ID 参数
        params = {"id": object_id}
        request_params = self._build_request_params(object_type, params)

        try:
            response = await self.http_client.post(
                self._host,
                data=request_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._extract_single_data(response)

        except JkyAdapterAPIError:
            raise
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                raise NotFoundError(
                    f"{object_type} not found",
                    resource_type=object_type,
                    resource_id=object_id,
                ) from e
            raise JkyAdapterAPIError(
                f"Failed to get {object_type}",
                details={"object_type": object_type, "object_id": object_id},
            ) from e

    async def create_object(self, object_type: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        创建对象

        Args:
            object_type: 对象类型，对应 API method
            data: 对象数据

        Returns:
            创建后的对象
        """
        request_params = self._build_request_params(object_type, data)

        try:
            response = await self.http_client.post(
                self._host,
                data=request_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._extract_single_data(response)

        except JkyAdapterAPIError:
            raise
        except Exception as e:
            raise JkyAdapterAPIError(
                f"Failed to create {object_type}",
                details={"object_type": object_type, "data": data, "error": str(e)},
            ) from e

    async def update_object(
        self,
        object_type: str,
        object_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        更新对象

        Args:
            object_type: 对象类型，对应 API method
            object_id: 对象 ID
            data: 更新数据

        Returns:
            更新后的对象
        """
        # 将 object_id 加入到 data 中
        data_with_id = {"id": object_id, **data}
        request_params = self._build_request_params(object_type, data_with_id)

        try:
            response = await self.http_client.post(
                self._host,
                data=request_params,
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

            return self._extract_single_data(response)

        except JkyAdapterAPIError:
            raise
        except Exception as e:
            raise JkyAdapterAPIError(
                f"Failed to update {object_type}",
                details={"object_type": object_type, "object_id": object_id, "error": str(e)},
            ) from e

    async def invoke(
        self,
        method: str,
        object_type: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        统一的 API 调用方法

        Args:
            method: API 方法名，如 "query", "get", "create", "update"
            object_type: 对象类型，如 "erp.vend.get"
            data: 请求体数据（用于 create/update 等）
            params: 查询参数（用于 query/get 等）

        Returns:
            API 响应数据
        """
        if method in ("list", "query"):
            results = []
            async for item in self.list_objects(
                object_type, filters=params, page_size=100
            ):
                results.append(item)
            return {"data": results, "total": len(results)}

        elif method == "get":
            # 对于 erp.vend.get 等接口，使用 code 参数而不是 id
            request_params = self._build_request_params(object_type, params or {})
            try:
                response = await self.http_client.post(
                    self._host,
                    data=request_params,
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )
                result = self._extract_single_data(response)
                return {"data": result}
            except Exception as e:
                raise JkyAdapterAPIError(
                    f"Failed to invoke {object_type}",
                    details={"method": method, "params": params, "error": str(e)},
                ) from e

        elif method == "create":
            if not data:
                raise ValueError("'create' method requires data")
            result = await self.create_object(object_type, data)
            return {"data": result}

        elif method == "update":
            if not data:
                raise ValueError("'update' method requires data")
            # 从 data 中获取 object_id（可能是 id, vendId 等）
            object_id = (
                data.get("id")
                or data.get("vendId")
                or (params.get("id") if params else None)
            )
            if not object_id:
                raise ValueError("'update' method requires data['id'] or data['vendId']")
            result = await self.update_object(object_type, object_id, data)
            return {"data": result}

        else:
            raise NotImplementedError(
                f"Method '{method}' not implemented in interface. "
                f"Please override invoke() in your interface class."
            )

    async def health_check(self) -> bool:
        """
        健康检查

        Returns:
            True: 连接正常
            False: 连接异常
        """
        try:
            # 验证认证配置
            await self.authenticate()
            return True
        except Exception as e:
            logger.warning("Health check failed: %s", e)
            return False


def json_dumps(obj: Any) -> str:
    """将对象转为 JSON 字符串，确保返回 str 类型（不是 bytes）"""
    try:
        import orjson
        # orjson.dumps 返回 bytes，需要解码
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode("utf-8")
    except ImportError:
        return _json.dumps(obj, ensure_ascii=False)


__all__ = ["JkyAdapterStandardInterface"]
