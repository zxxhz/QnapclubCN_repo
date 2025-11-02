import json
import datetime
from collections import OrderedDict
from typing import Dict, Any, Iterator, List

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.auth.v3 import *

from .base import DataSource
from config import Config


class FeishuDataSource(DataSource):
    """飞书数据源"""
    
    def __init__(self, config: Config):
        super().__init__()
        self.app_token = config.app_token
        self.table_id = config.table_id
        self.view_id = config.view_id
        self.app_id = config.app_id
        self.app_secret = config.app_secret
        self.client = None
        self._init_client()

    def _init_client(self):
        """初始化Lark客户端"""
        # 获取tenant_access_token
        token = self._get_tenant_access_token()

        # 创建client
        self.client = (
            lark.Client.builder()
            .enable_set_token(True)
            .log_level(lark.LogLevel.DEBUG)
            .build()
        )

        return token

    def _get_tenant_access_token(self):
        """获取企业自建应用的tenant_access_token"""
        # 创建client
        auth_client = (
            lark.Client.builder()
            .app_id(self.app_id)
            .app_secret(self.app_secret)
            .log_level(lark.LogLevel.DEBUG)
            .build()
        )

        # 构造请求对象
        request: InternalTenantAccessTokenRequest = (
            InternalTenantAccessTokenRequest.builder()
            .request_body(
                InternalTenantAccessTokenRequestBody.builder()
                .app_id(self.app_id)
                .app_secret(self.app_secret)
                .build()
            )
            .build()
        )

        # 发起请求
        response: InternalTenantAccessTokenResponse = (
            auth_client.auth.v3.tenant_access_token.internal(request)
        )

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.auth.v3.tenant_access_token.internal failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            )
            return None

        # 处理业务结果
        try:
            # 尝试不同的响应结构获取token
            if hasattr(response, "data") and hasattr(
                response.data, "tenant_access_token"
            ):
                return response.data.tenant_access_token
            elif hasattr(response, "raw") and hasattr(response.raw, "content"):
                response_content = json.loads(response.raw.content)
                if "tenant_access_token" in response_content:
                    return response_content["tenant_access_token"]
                elif (
                    "data" in response_content
                    and "tenant_access_token" in response_content["data"]
                ):
                    return response_content["data"]["tenant_access_token"]
        except Exception:
            pass
        return None

    def _get_field_order(self) -> List[str]:
        """获取字段顺序"""
        return [
            "name",
            "changeLog",
            "category",
            "type",
            "icon80",
            "icon100",
            "description",
            "fwVersion",
            "version",
            "platform",
            "location",
            "internalName",
            "publishedDate",
            "maintainer",
            "developer",
            "forumLink",
            "language",
            "snapshot",
            "bannerImg",
            "tutorialLink",
        ]

    def _process_platform_field(
        self, field_value: Any, fields: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """处理platform字段"""
        platform_info_list = []

        if isinstance(field_value, list):
            # 处理多选情况
            for pid in field_value:
                location_url = self._extract_location_url(pid, fields.get("location"))
                platform_info = {
                    "platformID": pid,
                    "location": location_url,
                    "signature": "",  # 需要根据实际情况填充
                }
                platform_info_list.append(platform_info)
        else:
            # 处理单选情况
            location_url = self._extract_location_url(
                field_value, fields.get("location")
            )
            platform_info = {
                "platformID": field_value,
                "location": location_url,
                "signature": "",
            }
            platform_info_list = [platform_info]

        return platform_info_list

    def _extract_location_url(self, platform_id: str, location_field: Any) -> str:
        """从location字段中提取特定平台的URL"""
        if not location_field:
            return ""

        location_url = ""

        # 处理列表类型的location字段（飞书富文本格式）
        if isinstance(location_field, list):
            # 重建JSON字符串，处理text和link类型
            json_str = ""
            for item in location_field:
                if isinstance(item, dict):
                    if "text" in item:
                        json_str += item["text"]
                    elif "link" in item:
                        json_str += item["link"]

            try:
                # 解析JSON字符串
                location_dict = json.loads(json_str.replace("\n", ""))
                if platform_id in location_dict:
                    location_url = location_dict[platform_id].strip("` ")
            except json.JSONDecodeError:
                # 备用方法：直接查找URL模式
                import re

                urls = re.findall(
                    r"https?://[\w\.-]+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+", json_str
                )
                if urls and self._platform_id_match(platform_id, json_str):
                    location_url = urls[0]
        # 处理字符串类型
        elif isinstance(location_field, str):
            try:
                location_dict = json.loads(location_field.replace("\n", ""))
                if platform_id in location_dict:
                    location_url = location_dict[platform_id].strip("` ")
            except json.JSONDecodeError:
                pass
        # 处理字典类型
        elif isinstance(location_field, dict) and platform_id in location_field:
            location_url = location_field[platform_id].strip("` ")

        return location_url

    def _platform_id_match(self, platform_id: str, text: str) -> bool:
        """检查平台ID是否在文本中出现，用于备用URL匹配"""
        return platform_id.lower() in text.lower()

    def _process_field(
        self, field_name: str, field_value: Any, fields: Dict[str, Any]
    ) -> Any:
        """处理单个字段的值"""
        if (
            isinstance(field_value, list)
            and len(field_value) > 0
            and "text" in field_value[0]
        ):
            return field_value[0]["text"]
        elif field_name == "platform":
            return self._process_platform_field(field_value, fields)
        elif field_name == "internalName":
            # 确保internalName为字符串类型
            if isinstance(field_value, dict):
                return field_value.get("text", str(field_value))
            elif isinstance(field_value, list):
                if field_value and isinstance(field_value[0], dict):
                    return field_value[0].get("text", "")
                else:
                    return str(field_value)
            else:
                return str(field_value) if field_value is not None else ""
        elif field_name == "publishedDate":
            # 将毫秒级时间戳转换为指定格式的日期时间字符串
            try:
                timestamp = int(field_value) / 1000
                dt = datetime.datetime.fromtimestamp(timestamp)
                return dt.strftime("%Y-%m-%d %H:%M")
            except (TypeError, ValueError):
                return field_value
        else:
            return field_value

    def fetch_data(self) -> Iterator[Dict[str, Any]]:
        """获取数据的生成器方法（实现抽象方法）"""
        # 获取所有应用数据
        apps_list = self.fetch_and_convert_data()

        # 逐个返回应用信息
        for app_info in apps_list:
            yield app_info

    def fetch_and_convert_data(self) -> List[Dict[str, Any]]:
        """从飞书获取数据并转换为apps.json格式"""
        # 获取token
        token = self._get_tenant_access_token()
        if not token:
            print("获取tenant_access_token失败")
            return []

        # 获取字段顺序
        field_order = self._get_field_order()

        # 构造请求对象
        request: SearchAppTableRecordRequest = (
            SearchAppTableRecordRequest.builder()
            .app_token(self.app_token)
            .table_id(self.table_id)
            .user_id_type("open_id")
            .page_size(500)  # 单页最大500条记录
            .request_body(
                SearchAppTableRecordRequestBody.builder()
                .view_id(self.view_id)
                .field_names(field_order)  # 使用定义的字段顺序
                .build()
            )
            .build()
        )

        # 发起请求
        option = lark.RequestOption.builder().user_access_token(token).build()
        response: SearchAppTableRecordResponse = (
            self.client.bitable.v1.app_table_record.search(request, option)
        )

        # 处理失败返回
        if not response.success():
            lark.logger.error(
                f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
            )
            return []

        # 处理业务结果
        items = response.data.items
        apps_list: list[dict] = []

        for item in items:
            # 使用OrderedDict来保持字段顺序
            app_info = OrderedDict()
            fields = item.fields

            # 处理所有字段
            processed_fields = {}
            for field_name, field_value in fields.items():
                processed_fields[field_name] = self._process_field(
                    field_name, field_value, fields
                )

            # 按照定义的顺序添加字段
            for field_name in field_order:
                if field_name in processed_fields:
                    app_info[field_name] = processed_fields[field_name]

            apps_list.insert(0, app_info)

        return apps_list
