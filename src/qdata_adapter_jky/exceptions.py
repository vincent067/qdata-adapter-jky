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
jky 适配器异常定义
"""

from qdata_adapter.exceptions import AdapterError, AuthenticationError, ResponseError


class JkyAdapterError(AdapterError):
    """
    jky 适配器基础异常

    Example:
        >>> raise JkyAdapterError("操作失败", code="OP_FAILED")
    """

    def __init__(self, message: str, code: str = "JKY_ERROR", details: dict | None = None):
        super().__init__(message, code, details)


class JkyAdapterAuthError(AuthenticationError):
    """
    jky 认证失败异常

    Example:
        >>> raise JkyAdapterAuthError("Invalid API key")
    """

    def __init__(self, message: str = "Authentication failed", details: dict | None = None):
        super().__init__(message, "JKY_AUTH_ERROR", details)


class JkyAdapterAPIError(ResponseError):
    """
    jky API 错误异常

    Attributes:
        status_code: HTTP 状态码
        api_code: jky 错误码

    Example:
        >>> raise JkyAdapterAPIError(
        ...     "API call failed",
        ...     status_code=500,
        ...     api_code="INTERNAL_ERROR"
        ... )
    """

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        api_code: str | None = None,
        response_body: dict | None = None,
        details: dict | None = None,
    ):
        details = details or {}
        if api_code is not None:
            details["api_code"] = api_code
        super().__init__(message, "JKY_API_ERROR", status_code, response_body, details)
        self.api_code = api_code


__all__ = [
    "JkyAdapterError",
    "JkyAdapterAuthError",
    "JkyAdapterAPIError",
]