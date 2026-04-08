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
jky qimen 接口实现

备用接口实现，用于奇门网关 API。
参考旧PHP实现: JkyQMSDK.php
"""

from __future__ import annotations

import hashlib
import http
import json as _json
import logging
import time
from typing import TYPE_CHECKING, Any, AsyncIterator

from qdata_adapter.exceptions import NotFoundError

from qdata_adapter_jky.exceptions import JkyAdapterAPIError, JkyAdapterAuthError
from qdata_adapter_jky.interfaces.base import BaseInterface

if TYPE_CHECKING:
    from qdata_adapter.client import HttpClient
    from qdata_adapter.context import ConnectorContext

logger = logging.getLogger(__name__)


class JkyAdapterQimenInterface(BaseInterface):
    """
    jky qimen 接口实现

    备用接口，支持奇门网关认证方式和 API 规范。
    API文档: https://open.jackyun.com/developer/document.html?alias=outsystem_openplat

    Example:
        >>> context = ConnectorContext(
        ...     connector_id="test",
        ...     app_software_code="jky",
        ...     base_url="https://zci2vl4joy.api.taobao.com/router/qm",
        ...     auth_config={
        ...         "app_key": "xxx",
        ...         "app_secret": "xxx",
        ...         "jkyappkey": "xxx",
        ...         "jkyappsecret": "xxx",
        ...         "jkycustomerid": "xxx",
        ...     },
        ... )
        >>> interface = JkyAdapterQimenInterface(context, http_client)
    """

    interface_name = "qimen"

    # 奇门网关地址
    DEFAULT_HOST = "https://zci2vl4joy.api.taobao.com/router/qm"

    # 吉客云的数据键映射（与 Standard 接口相同）
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
        self._host = self.context.base_url or self.DEFAULT_HOST

    def _generate_jky_sign(self, api: str, bizcontent: str, timestamp: str) -> str:
        """
        生成吉客云签名（jkysign）

        签名算法：
        str = 'appkey' + jkyappkey + 'bizcontent' + bizcontent + 'contenttypeJSON'
              + 'method' + api + 'timestamp' + timestamp + 'version1.0'
        jkysign = md5(lowercase(jkyappsecret + str + jkyappsecret))

        Args:
            api: API方法名
            bizcontent: JSON格式的请求参数
            timestamp: 时间戳

        Returns:
            吉客云签名字符串
        """
        auth_config = self.get_auth_config()
        jky_app_key = auth_config.get("jkyappkey", "")
        jky_app_secret = auth_config.get("jkyappsecret", "")

        sign_str = (
            f"appkey{jky_app_key}"
            f"bizcontent{bizcontent}"
            f"contenttypeJSON"
            f"method{api}"
            f"timestamp{timestamp}"
            f"version1.0"
        )
        sign_str = jky_app_secret + sign_str + jky_app_secret
        return hashlib.md5(sign_str.lower().encode()).hexdigest()

    def _generate_sign(self, params: dict[str, Any]) -> str:
        """
        生成淘宝风格签名（sign）

        签名算法：
        1. 按 key 升序排序
        2. 拼接 key + value（跳过以 @ 开头的值和数组）
        3. 前后用 app_secret 包裹
        4. MD5 后转大写

        Args:
            params: 所有请求参数

        Returns:
            签名字符串
        """
        auth_config = self.get_auth_config()
        app_secret = auth_config.get("app_secret", "")

        # 按 key 升序排序
        sorted_params = sorted(params.items())
        string_to_sign = app_secret

        for key, value in sorted_params:
            # 跳过数组和以 @ 开头的值
            if isinstance(value, list):
                continue
            if isinstance(value, str) and value.startswith("@"):
                continue
            string_to_sign += f"{key}{value}"

        string_to_sign += app_secret
        return hashlib.md5(string_to_sign.encode()).hexdigest().upper()

    def _build_request_params(
        self, api: str, bizcontent: dict[str, Any] | None = None
    ) -> dict[str, Any]:
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

        # 系统参数
        sys_params = {
            "app_key": auth_config.get("app_key", ""),
            "target_app_key": auth_config.get("target_app_key", ""),
            "format": "json",
            "v": "2.0",
            "sign_method": "md5",
            "timestamp": timestamp,
            "method": api,
            "partner_id": "top-sdk-java-dynamicVersionNo",
        }

        # 吉客云特定参数
        sys_params["jkymethod"] = api
        sys_params["jkysign"] = self._generate_jky_sign(api, bizcontent_json, timestamp)
        sys_params["jkytimestamp"] = timestamp
        sys_params["jkyversion"] = "1.0"
        sys_params["jkyappkey"] = auth_config.get("jkyappkey", "")
        sys_params["jkycustomerid"] = auth_config.get("jkycustomerid", "")
        sys_params["content"] = bizcontent_json

        # 生成签名
        sys_params["sign"] = self._generate_sign(sys_params)

        return sys_params

    async def authenticate(self) -> dict[str, Any]:
        """
        获取认证凭证

        Qimen 接口使用 HMAC 签名认证，无需额外认证请求。
        此方法仅验证配置是否完整。

        Returns:
            认证信息

        Raises:
            JkyAdapterAuthError: 认证配置缺失
        """
        auth_config = self.get_auth_config()

        app_key = auth_config.get("app_key")
        app_secret = auth_config.get("app_secret")
        jky_app_key = auth_config.get("jkyappkey")
        jky_app_secret = auth_config.get("jkyappsecret")
        jky_customer_id = auth_config.get("jkycustomerid")

        missing = []
        if not app_key:
            missing.append("app_key")
        if not app_secret:
            missing.append("app_secret")
        if not jky_app_key:
            missing.append("jkyappkey")
        if not jky_app_secret:
            missing.append("jkyappsecret")
        if not jky_customer_id:
            missing.append("jkycustomerid")

        if missing:
            raise JkyAdapterAuthError(
                f"Missing required credentials: {', '.join(missing)}",
                details={"missing": missing},
            )

        logger.debug("Authentication configured for app_key: %s, jkyappkey: %s",
                     app_key[:8] + "..." if app_key else None,
                     jky_app_key[:8] + "..." if jky_app_key else None)

        return {
            "app_key": app_key,
            "jkyappkey": jky_app_key,
            "authenticated": True,
        }

    def _extract_list_data(self, response: dict[str, Any]) -> tuple[list[Any], int]:
        """
        从响应中提取列表数据

        Args:
            response: API 响应（可能是字符串或字典）

        Returns:
            (数据列表, 总数)

        Raises:
            JkyAdapterAPIError: API 调用失败
        """
        # 如果是字符串，尝试解析为 JSON
        if isinstance(response, str):
            try:
                response = _json.loads(response)
            except _json.JSONDecodeError:
                raise JkyAdapterAPIError(
                    f"Failed to parse response as JSON: {response[:200]}",
                    details={"raw_response": response[:500]},
                )

        # Qimen 响应格式: {"response": {...}}
        if isinstance(response, dict) and "response" in response:
            response = response["response"]

        # 检查 flag 和 code
        flag = response.get("flag", "")
        code = response.get("code")

        if flag == "failure" or (code is not None and code != 0 and code != 200):
            message = response.get("message", response.get("sub_message", "Unknown error"))
            raise JkyAdapterAPIError(
                f"API error: {message}",
                api_code=str(code),
                details=response,
            )

        # 尝试从 result.data 或 jackyunData 获取数据
        result = response.get("result") or response.get("jackyunData") or {}
        if result is None:
            result = {}

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
        logger.warning("Unexpected response data format: %s",
                       list(data.keys()) if isinstance(data, dict) else type(data))
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
        # 检查错误码
        code = response.get("code") or response.get("jackyunCode")
        if code and code != 200:
            message = response.get("message") or response.get("msg", "Unknown error")
            raise JkyAdapterAPIError(
                f"API error: {message}",
                api_code=str(code),
                details=response,
            )

        # 尝试从 result.data 获取数据
        result = response.get("result") or response.get("jackyunData") or {}
        data = result.get("data", {})

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
            object_type: 对象类型，对应 API method
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
        创建对象（暂不支持）

        Args:
            object_type: 对象类型
            data: 对象数据

        Returns:
            创建后的对象

        Raises:
            NotImplementedError: 此接口暂不支持写操作
        """
        raise NotImplementedError(
            "Create operations are not supported in this adapter. "
            "This adapter is read-only."
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


__all__ = ["JkyAdapterQimenInterface"]
