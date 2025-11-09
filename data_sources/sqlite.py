import json
import re
from collections import OrderedDict
from typing import Dict, Any, Iterator, List
import sqlite3

from .base import DataSource
from config import Config


class SQLiteDataSource(DataSource):
    """SQLite数据源"""

    def __init__(self, config: Config):
        super().__init__()
        self.db_path = config.db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def close(self):
        self.cursor.close()
        self.conn.close()

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

    def _extract_location_url(self, platform_id: str, location_field: Any) -> str:
        """从location字段中提取特定平台的URL"""
        if not location_field:
            return ""

        location_url = ""

        # 处理列表类型的location字段
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
                # 如果不是JSON字符串，尝试直接提取URL
                urls = re.findall(
                    r"https?://[\w\.-]+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+",
                    location_field,
                )
                if urls:
                    location_url = urls[0]
        # 处理字典类型
        elif isinstance(location_field, dict) and platform_id in location_field:
            location_url = location_field[platform_id].strip("` ")

        return location_url

    def _platform_id_match(self, platform_id: str, text: str) -> bool:
        """检查平台ID是否在文本中出现，用于备用URL匹配"""
        return platform_id.lower() in text.lower()

    def _process_platform_field(
        self, field_value: Any, fields: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """处理platform字段"""
        platform_info_list = []

        # 尝试解析JSON字符串
        if isinstance(field_value, str):
            try:
                field_value = json.loads(field_value)
            except (json.JSONDecodeError, TypeError):
                # 如果解析失败，尝试按逗号分割
                if "," in field_value:
                    field_value = [p.strip() for p in field_value.split(",")]
                else:
                    field_value = [field_value]

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

    def _process_field(
        self, field_name: str, field_value: Any, fields: Dict[str, Any]
    ) -> Any:
        """处理单个字段的值"""
        if field_value is None:
            return ""

        if field_name == "platform":
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
                return str(field_value)
        elif field_name == "publishedDate":
            # 日期全是TEXT类型，直接返回字符串值，不需要时间戳转换
            if field_value is None:
                return ""
            else:
                return str(field_value)
        # 处理location字段，尝试解析JSON
        elif field_name == "location" and isinstance(field_value, str):
            try:
                return json.loads(field_value)
            except json.JSONDecodeError:
                return field_value
        # 处理富文本字段
        elif (
            isinstance(field_value, list)
            and len(field_value) > 0
            and isinstance(field_value[0], dict)
            and "text" in field_value[0]
        ):
            return field_value[0]["text"]
        else:
            return field_value

    def fetch_data(self) -> Iterator[Dict[str, Any]]:
        """获取数据的生成器方法（实现抽象方法）"""
        # 获取字段顺序
        field_order = self._get_field_order()

        # 查询数据库 - 使用明确的列名替代SELECT *，更严谨且性能更好
        # 根据_get_field_order方法中定义的字段顺序来指定查询列
        columns = [
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

        # 构建查询语句，使用明确的列名列表
        columns_str = ", ".join(columns)
        query = f"SELECT {columns_str} FROM data"

        self.cursor.execute(query)
        rows = self.cursor.fetchall()

        # 获取列名
        columns = [column[0] for column in self.cursor.description]

        # 处理每一行数据
        for row in rows:
            # 创建原始字段字典
            raw_fields = dict(zip(columns, row))

            # 使用OrderedDict来保持字段顺序
            app_info = OrderedDict()

            # 处理所有字段
            processed_fields = {}
            for field_name, field_value in raw_fields.items():
                processed_fields[field_name] = self._process_field(
                    field_name, field_value, raw_fields
                )

            # 按照定义的顺序添加字段
            for field_name in field_order:
                if field_name in processed_fields:
                    app_info[field_name] = processed_fields[field_name]

            # 添加其他可能存在的字段
            for field_name, field_value in processed_fields.items():
                if field_name not in app_info:
                    app_info[field_name] = field_value

            yield app_info
