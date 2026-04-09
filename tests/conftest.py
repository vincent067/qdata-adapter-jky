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
Pytest 配置和 Fixtures

支持：
1. 从 .env 文件加载测试配置
2. Mock 和真实 API 测试切换
3. HTTP 流量录制（用于调试）
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import pytest
from qdata_adapter import ConnectorContext

# =============================================================================
# 配置常量
# =============================================================================

ADAPTER_NAME = "jky"
# 测试使用固定的 base_url，不从环境变量读取
BASE_URL = "https://api.example.com"
ENVIRONMENT = "sandbox"
USE_REAL_API = os.getenv("USE_REAL_API", "false").lower() == "true"
RECORD_TRAFFIC = os.getenv("RECORD_HTTP_TRAFFIC", "false").lower() == "true"
TEST_DATA_DIR = Path(os.getenv("TEST_DATA_DIR", "tests/data"))


# =============================================================================
# 辅助函数
# =============================================================================

def save_http_recording(
    test_name: str,
    request_data: dict,
    response_data: dict,
    interface: str = "standard",
) -> None:
    """
    保存 HTTP 请求/响应记录

    Args:
        test_name: 测试名称
        request_data: 请求数据
        response_data: 响应数据
        interface: 接口类型
    """
    if not RECORD_TRAFFIC:
        return

    # 创建记录目录
    recording_dir = TEST_DATA_DIR / "recordings" / datetime.now().strftime("%Y%m%d")
    recording_dir.mkdir(parents=True, exist_ok=True)

    # 构建文件名
    timestamp = datetime.now().strftime("%H%M%S")
    filename = f"{interface}_{test_name}_{timestamp}.json"
    filepath = recording_dir / filename

    # 保存记录
    record = {
        "timestamp": datetime.now().isoformat(),
        "test_name": test_name,
        "interface": interface,
        "request": request_data,
        "response": response_data,
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

    print(f"\n[录制] HTTP 记录已保存: {filepath}")


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def test_config() -> dict[str, Any]:
    """测试配置 fixture"""
    return {
        "use_real_api": USE_REAL_API,
        "record_traffic": RECORD_TRAFFIC,
        "test_data_dir": TEST_DATA_DIR,
        "base_url": BASE_URL,
        "environment": ENVIRONMENT,
    }


@pytest.fixture
def standard_auth_config() -> dict[str, str]:
    """
    standard 接口认证配置

    使用测试占位符，确保测试可重复且无需真实凭据。
    如需真实 API 测试，请设置 USE_REAL_API=true 并在 .env 中配置。
    """
    return {
        "AppKey": "test-app-key-12345",
        "AppSecret": "test-app-secret-1234567890abcdef",
        "token": "test-token-123",
    }

@pytest.fixture
def qimen_auth_config() -> dict[str, str]:
    """
    qimen 接口认证配置

    优先从环境变量读取，使用默认值作为 fallback。
    如需真实测试，请在 .env 文件中配置真实凭据。
    """
    prefix = ADAPTER_NAME.upper()
    return {
        "app_key": os.getenv(f"{prefix}_QIMEN_APP_KEY", "test-qimen-app-key"),
        "app_secret": os.getenv(f"{prefix}_QIMEN_APP_SECRET", "test-qimen-app-secret"),
        "target_app_key": os.getenv(f"{prefix}_QIMEN_TARGET_APP_KEY", "test-target-app-key"),
        "jkyappkey": os.getenv(f"{prefix}_QIMEN_JKY_APP_KEY", "test-jky-app-key"),
        "jkyappsecret": os.getenv(f"{prefix}_QIMEN_JKY_APP_SECRET", "test-jky-app-secret"),
        "jkycustomerid": os.getenv(f"{prefix}_QIMEN_CUSTOMER_ID", "test-customer-id"),
    }


@pytest.fixture
def base_context() -> ConnectorContext:
    """基础上下文 fixture"""
    return ConnectorContext(
        connector_id="test-connector",
        app_software_code=ADAPTER_NAME,
        base_url=BASE_URL,
        auth_config={},
    )


@pytest.fixture
def standard_context(standard_auth_config: dict) -> ConnectorContext:
    """standard 接口上下文 fixture"""
    return ConnectorContext(
        connector_id="test-connector-standard",
        app_software_code=ADAPTER_NAME,
        base_url=BASE_URL,
        auth_config=standard_auth_config,
        settings={"interface": "standard"},
        environment=ENVIRONMENT,
    )

@pytest.fixture
def qimen_context(qimen_auth_config: dict) -> ConnectorContext:
    """qimen 接口上下文 fixture"""
    return ConnectorContext(
        connector_id="test-connector-qimen",
        app_software_code=ADAPTER_NAME,
        base_url=BASE_URL,
        auth_config=qimen_auth_config,
        settings={"interface": "qimen"},
        environment=ENVIRONMENT,
    )


@pytest.fixture
def mock_token_cache() -> Any:
    """Mock Token 缓存 fixture"""
    class MockTokenCache:
        _cache: dict[str, Any] = {}

        async def get(self, key: str) -> Any:
            return self._cache.get(key)

        async def set(self, key: str, value: Any, ttl: int | None = None) -> None:
            self._cache[key] = value

        async def delete(self, key: str) -> None:
            self._cache.pop(key, None)

    return MockTokenCache()


@pytest.fixture
def http_recorder():
    """HTTP 记录器 fixture"""
    class HTTPRecorder:
        def __init__(self):
            self.records = []

        def record(self, test_name: str, request: dict, response: dict, interface: str = "standard"):
            self.records.append({
                "test_name": test_name,
                "request": request,
                "response": response,
                "interface": interface,
            })
            save_http_recording(test_name, request, response, interface)

        def clear(self):
            self.records.clear()

    return HTTPRecorder()


# =============================================================================
# Pytest 钩子
# =============================================================================

def pytest_configure(config):
    """Pytest 配置钩子"""
    # 添加自定义标记
    config.addinivalue_line(
        "markers", "real_api: 标记需要真实 API 的测试"
    )
    config.addinivalue_line(
        "markers", "record_http: 标记需要录制 HTTP 流量的测试"
    )


def pytest_runtest_setup(item):
    """测试前设置"""
    # 检查是否需要跳过真实 API 测试
    if "real_api" in item.keywords and not USE_REAL_API:
        pytest.skip("跳过真实 API 测试 (USE_REAL_API=false)")