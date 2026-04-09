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
奇门接口签名测试

验证 Python 实现的签名与 PHP 实现一致

注意：本测试文件使用测试占位符配置，不从 .env 加载真实密钥
所有配置值均为测试专用占位符，非真实凭据
"""

import hashlib
import json

import pytest

from qdata_adapter_jky.interfaces.qimen import (
    JkyAdapterQimenInterface,
    json_dumps,
)

# 测试专用的占位符配置（硬编码，不从环境变量读取）
# 这些值仅用于测试签名算法正确性，非真实 API 凭据
TEST_QIMEN_CONFIG = {
    "app_key": "TEST_QIMEN_APP_KEY_12345678",
    "app_secret": "TEST_QIMEN_APP_SECRET_1234567890abcdef",
    "target_app_key": "TEST_TARGET_APP_KEY_12345678",
    "jkyappkey": "TEST_JKY_APP_KEY_12345678",
    "jkyappsecret": "TEST_JKY_APP_SECRET_1234567890abcdef",
    "jkycustomerid": "TEST_CUSTOMER_ID_123456",
}


class TestQimenJsonDumps:
    """测试 JSON 编码与 PHP 风格一致"""

    def test_json_dumps_php_style(self):
        """JSON 编码应为紧凑格式（匹配 PHP json_encode 默认输出）"""
        result = json_dumps({"pageNo": 1, "pageSize": 10})
        # PHP json_encode 默认输出是紧凑格式，不在 : 和 , 后面加空格
        assert result == '{"pageNo":1,"pageSize":10}', f"JSON 应该是紧凑格式: {result}"
        assert ": " not in result, f"JSON 不应包含 ': ' 空格: {result}"
        assert ", " not in result, f"JSON 不应包含 ', ' 空格: {result}"

    def test_json_dumps_ensure_ascii_false(self):
        """JSON 编码不应转义 Unicode"""
        result = json_dumps({"name": "测试"})
        assert "测试" in result, f"Unicode 应该原样输出: {result}"

    def test_json_dumps_none(self):
        """None 应返回空字符串"""
        assert json_dumps(None) == ""

    def test_json_dumps_empty_dict(self):
        """空对象应返回 {}"""
        assert json_dumps({}) == "{}"


class TestQimenJkySign:
    """测试 jkysign 生成"""

    @pytest.fixture
    def qimen_interface(self):
        """创建奇门接口实例（使用测试占位符配置）"""
        class MockContext:
            def __init__(self):
                self.auth_config = TEST_QIMEN_CONFIG
                self.base_url = "https://test-example.com/router/qm"
                self.settings = {}

        class MockHttpClient:
            pass

        return JkyAdapterQimenInterface(MockContext(), MockHttpClient())

    def test_jky_sign_with_php_style_json(self, qimen_interface):
        """jkysign 应使用 PHP json_encode 默认格式（紧凑 JSON）"""
        api = "jackyun.tradenotsensitiveinfos.list.get"
        timestamp = "2024-01-15 10:30:00"

        # 使用紧凑 JSON 匹配 PHP json_encode 默认输出（无空格）
        biz_dict = {"pageSize": 200, "pageIndex": 1}
        bizcontent = json.dumps(biz_dict, ensure_ascii=False, separators=(",", ":"))  # PHP 默认格式

        jkysign = qimen_interface._generate_jky_sign(api, bizcontent, timestamp)

        # 手动计算预期签名
        jky_app_key = TEST_QIMEN_CONFIG["jkyappkey"]
        jky_app_secret = TEST_QIMEN_CONFIG["jkyappsecret"]
        expected_sign_str = (
            jky_app_secret +
            'appkey' + jky_app_key +
            'bizcontent' + bizcontent +
            'contenttype' + 'JSON' +
            'method' + api +
            'timestamp' + timestamp +
            'version1.0' +
            jky_app_secret
        ).lower()
        expected_jkysign = hashlib.md5(expected_sign_str.encode()).hexdigest()

        assert jkysign == expected_jkysign, f"jkysign 不匹配: {jkysign} != {expected_jkysign}"

    def test_jky_sign_algorithm(self, qimen_interface):
        """验证 jkysign 算法正确性"""
        api = "jackyun.test.api"
        timestamp = "2024-01-15 10:30:00"
        bizcontent = '{"id": 1}'  # PHP 风格

        jkysign = qimen_interface._generate_jky_sign(api, bizcontent, timestamp)

        # 验证签名格式（32位小写十六进制）
        assert len(jkysign) == 32, f"签名长度应为32: {len(jkysign)}"
        assert jkysign.islower(), f"签名应为小写: {jkysign}"
        assert all(c in '0123456789abcdef' for c in jkysign), f"签名包含非法字符: {jkysign}"


class TestQimenTaobaoSign:
    """测试淘宝风格签名生成"""

    @pytest.fixture
    def qimen_interface(self):
        """创建奇门接口实例（使用测试占位符配置）"""
        class MockContext:
            def __init__(self):
                self.auth_config = TEST_QIMEN_CONFIG
                self.base_url = "https://test-example.com/router/qm"
                self.settings = {}

        class MockHttpClient:
            pass

        return JkyAdapterQimenInterface(MockContext(), MockHttpClient())

    def test_taobao_sign_uppercase(self, qimen_interface):
        """淘宝签名应为大写"""
        params = {"app_key": TEST_QIMEN_CONFIG["app_key"], "format": "json"}
        sign = qimen_interface._generate_sign(params)
        assert sign.isupper(), f"签名应为大写: {sign}"

    def test_taobao_sign_skips_arrays(self, qimen_interface):
        """淘宝签名应跳过数组参数"""
        params = {
            "app_key": TEST_QIMEN_CONFIG["app_key"],
            "shopIds": ["123", "456"],  # 数组应被跳过
            "format": "json",
        }
        sign = qimen_interface._generate_sign(params)

        # 手动计算（不包含数组）
        app_secret = TEST_QIMEN_CONFIG["app_secret"]
        expected_str = app_secret + f"app_key{TEST_QIMEN_CONFIG['app_key']}" + "formatjson" + app_secret
        expected_sign = hashlib.md5(expected_str.encode()).hexdigest().upper()

        assert sign == expected_sign, f"签名不匹配: {sign} != {expected_sign}"

    def test_taobao_sign_skips_at_prefix(self, qimen_interface):
        """淘宝签名应跳过以 @ 开头的值"""
        params = {
            "app_key": TEST_QIMEN_CONFIG["app_key"],
            "file": "@/path/to/file",  # 应被跳过
            "format": "json",
        }
        sign = qimen_interface._generate_sign(params)

        # 手动计算（不包含 @ 开头的值）
        app_secret = TEST_QIMEN_CONFIG["app_secret"]
        expected_str = app_secret + f"app_key{TEST_QIMEN_CONFIG['app_key']}" + "formatjson" + app_secret
        expected_sign = hashlib.md5(expected_str.encode()).hexdigest().upper()

        assert sign == expected_sign, f"签名不匹配: {sign} != {expected_sign}"


class TestQimenRequestParams:
    """测试请求参数构建"""

    @pytest.fixture
    def qimen_interface(self):
        """创建奇门接口实例（使用测试占位符配置）"""
        class MockContext:
            def __init__(self):
                self.auth_config = TEST_QIMEN_CONFIG
                self.base_url = "https://test-example.com/router/qm"
                self.settings = {}

        class MockHttpClient:
            pass

        return JkyAdapterQimenInterface(MockContext(), MockHttpClient())

    def test_build_request_params_structure(self, qimen_interface):
        """验证请求参数结构完整"""
        api = "jackyun.tradenotsensitiveinfos.list.get"
        bizcontent = {"pageSize": 200}

        params = qimen_interface._build_request_params(api, bizcontent)

        # 验证必需字段
        required_fields = [
            "app_key", "target_app_key", "format", "v", "sign_method",
            "timestamp", "method", "partner_id", "jkymethod", "jkysign",
            "jkytimestamp", "jkyversion", "jkyappkey", "jkycustomerid",
            "content", "sign"
        ]
        for field in required_fields:
            assert field in params, f"缺少必需字段: {field}"

    def test_build_request_params_content_is_php_style_json(self, qimen_interface):
        """验证 content 字段是紧凑 JSON 格式（匹配 PHP json_encode 默认输出）"""
        api = "jackyun.tradenotsensitiveinfos.list.get"
        bizcontent = {"pageSize": 200, "pageIndex": 1}

        params = qimen_interface._build_request_params(api, bizcontent)
        content = params["content"]

        # 验证是 PHP 默认格式（紧凑，不包含 ': ' 或 ', ' 空格）
        assert ": " not in content, f"content 不应包含 ': ' 空格（PHP 默认为紧凑格式）: {content}"
        assert ", " not in content, f"content 不应包含 ', ' 空格（PHP 默认为紧凑格式）: {content}"

        # 验证可以解析
        parsed = json.loads(content)
        assert parsed["pageSize"] == 200
        assert parsed["pageIndex"] == 1


class TestQimenPhpCompatibility:
    """测试与 PHP 实现的兼容性"""

    def test_json_encoding_matches_php(self):
        """验证 JSON 编码与 PHP json_encode 默认输出完全一致（对照真实 PHP 输出样例）"""
        # 每个元组为 (Python 输入, PHP json_encode 默认输出)
        # PHP json_encode 默认: 紧凑格式，不加空格，不转义 Unicode
        # 例: json_encode(["pageNo"=>1,"pageSize"=>10]) => '{"pageNo":1,"pageSize":10}'
        test_cases = [
            ({"pageNo": 1, "pageSize": 10}, '{"pageNo":1,"pageSize":10}'),
            ({"name": "测试", "count": 100}, '{"name":"测试","count":100}'),
            ({"items": [1, 2, 3]}, '{"items":[1,2,3]}'),
            ({"nested": {"a": 1, "b": 2}}, '{"nested":{"a":1,"b":2}}'),
        ]

        for data, expected_php_output in test_cases:
            python_result = json_dumps(data)
            assert python_result == expected_php_output, (
                f"JSON 编码与 PHP json_encode 默认输出不匹配:\n"
                f"Python: {python_result}\n"
                f"PHP:    {expected_php_output}"
            )
