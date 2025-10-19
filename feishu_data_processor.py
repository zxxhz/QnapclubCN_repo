import json
import datetime
from collections import OrderedDict

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *
from lark_oapi.api.auth.v3 import *


def get_tenant_access_token(app_id, app_secret):
    """
    获取企业自建应用的tenant_access_token

    Args:
        app_id: 应用的App ID
        app_secret: 应用的App Secret

    Returns:
        str: tenant_access_token，如果获取失败返回None
    """
    # 创建client
    client = (
        lark.Client.builder()
        .app_id(app_id)
        .app_secret(app_secret)
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )

    # 构造请求对象
    request: InternalTenantAccessTokenRequest = (
        InternalTenantAccessTokenRequest.builder()
        .request_body(
            InternalTenantAccessTokenRequestBody.builder()
            .app_id(app_id)
            .app_secret(app_secret)
            .build()
        )
        .build()
    )

    # 发起请求
    response: InternalTenantAccessTokenResponse = (
        client.auth.v3.tenant_access_token.internal(request)
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
        if hasattr(response, 'data') and hasattr(response.data, 'tenant_access_token'):
            return response.data.tenant_access_token
        elif hasattr(response, 'raw') and hasattr(response.raw, 'content'):
            response_content = json.loads(response.raw.content)
            if 'tenant_access_token' in response_content:
                return response_content['tenant_access_token']
            elif 'data' in response_content and 'tenant_access_token' in response_content['data']:
                return response_content['data']['tenant_access_token']
    except Exception:
        pass
    return None


def fetch_and_convert_data(config):
    """
    从飞书获取数据并转换为apps.json格式

    Args:
        config: 包含app_token、table_id、app_id和app_secret的配置对象

    Returns:
        list: 转换后的应用信息列表
    """
    # 如果配置中有app_id和app_secret，尝试获取tenant_access_token
    if hasattr(config, "app_id") and hasattr(config, "app_secret"):
        tenant_token = get_tenant_access_token(config.app_id, config.app_secret)
        if tenant_token:
            token = tenant_token

    # 创建client
    client = (
        lark.Client.builder()
        .enable_set_token(True)
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )

    # 定义apps.json的字段顺序
    field_order = [
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

    # 构造请求对象
    request: SearchAppTableRecordRequest = (
        SearchAppTableRecordRequest.builder()
        .app_token(config.app_token)
        .table_id(config.table_id)
        .user_id_type("open_id")
        .page_size(500) # 懒得写分页 单页最大500条记录
        .request_body(
            SearchAppTableRecordRequestBody.builder()
            .view_id("vewAbrcCsi")
            .field_names(field_order)  # 使用定义的字段顺序
            .build()
        )
        .build()
    )

    # 发起请求
    option = lark.RequestOption.builder().user_access_token(token).build()
    response: SearchAppTableRecordResponse = client.bitable.v1.app_table_record.search(
        request, option
    )

    # 处理失败返回
    if not response.success():
        lark.logger.error(
            f"client.bitable.v1.app_table_record.search failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}, resp: \n{json.dumps(json.loads(response.raw.content), indent=4, ensure_ascii=False)}"
        )
        return []

    # 处理业务结果
    items = response.data.items
    apps_list = []

    for item in items:
        # 使用OrderedDict来保持字段顺序
        app_info = OrderedDict()
        fields = item.fields

        # 先处理所有字段，去掉type
        processed_fields = {}
        for field_name, field_value in fields.items():
            if (
                isinstance(field_value, list)
                and len(field_value) > 0
                and "text" in field_value[0]
            ):
                processed_fields[field_name] = field_value[0]["text"]
            elif field_name == "platform":
                # 处理platform字段，转换为apps.json的格式
                platform_info_list = []
                # 如果是列表（多选），遍历每个平台ID
                if isinstance(field_value, list):
                    for pid in field_value:
                        # 处理location字段，提取URL并移除反引号
                        location_url = ""

                        if "location" in fields:
                            # 处理列表类型的location字段（飞书富文本格式）
                            if isinstance(fields["location"], list):
                                # 重建JSON字符串，处理text和link类型
                                json_str = ""
                                for item in fields["location"]:
                                    if isinstance(item, dict):
                                        if "text" in item:
                                            json_str += item["text"]
                                        elif "link" in item:
                                            json_str += item["link"]

                                try:
                                    # 解析JSON字符串
                                    location_dict = json.loads(
                                        json_str.replace("\n", "")
                                    )
                                    if pid in location_dict:
                                        location_url = location_dict[pid].strip("` ")
                                except json.JSONDecodeError:
                                    # 备用方法：直接查找URL模式
                                    import re

                                    urls = re.findall(
                                        r"https?://[\w\.-]+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+",
                                        json_str,
                                    )
                                    if urls:
                                        location_url = (
                                            urls[0]
                                            if platform_id_match(pid, json_str)
                                            else ""
                                        )
                            # 处理字符串类型
                            elif isinstance(fields["location"], str):
                                try:
                                    location_dict = json.loads(
                                        fields["location"].replace("\n", "")
                                    )
                                    if pid in location_dict:
                                        location_url = location_dict[pid].strip("` ")
                                except json.JSONDecodeError:
                                    pass
                            # 处理字典类型
                            elif (
                                isinstance(fields["location"], dict)
                                and pid in fields["location"]
                            ):
                                location_url = fields["location"][pid].strip("` ")

                        def platform_id_match(platform_id, text):
                            """检查平台ID是否在文本中出现，用于备用URL匹配"""
                            return platform_id.lower() in text.lower()

                        platform_info = {
                            "platformID": pid,
                            "location": location_url,
                            "signature": "",  # 需要根据实际情况填充
                        }
                        platform_info_list.append(platform_info)
                else:
                    # 保持对单选情况的兼容
                    # 处理location字段，提取URL并移除反引号
                    location_url = ""

                    if "location" in fields:
                        # 处理列表类型的location字段（飞书富文本格式）
                        if isinstance(fields["location"], list):
                            # 重建JSON字符串，处理text和link类型
                            json_str = ""
                            for item in fields["location"]:
                                if isinstance(item, dict):
                                    if "text" in item:
                                        json_str += item["text"]
                                    elif "link" in item:
                                        json_str += item["link"]

                            try:
                                # 解析JSON字符串
                                location_dict = json.loads(json_str.replace("\n", ""))
                                if field_value in location_dict:
                                    location_url = location_dict[field_value].strip(
                                        "` "
                                    )
                            except json.JSONDecodeError:
                                # 备用方法：直接查找URL模式
                                import re

                                urls = re.findall(
                                    r"https?://[\w\.-]+[\w\-\._~:/?#[\]@!\$&\'\(\)\*\+,;=.]+",
                                    json_str,
                                )
                                if urls:
                                    location_url = (
                                        urls[0]
                                        if platform_id_match(field_value, json_str)
                                        else ""
                                    )
                        # 处理字符串类型
                        elif isinstance(fields["location"], str):
                            try:
                                location_dict = json.loads(
                                    fields["location"].replace("\n", "")
                                )
                                if field_value in location_dict:
                                    location_url = location_dict[field_value].strip(
                                        "` "
                                    )
                            except json.JSONDecodeError:
                                pass
                        # 处理字典类型
                        elif (
                            isinstance(fields["location"], dict)
                            and field_value in fields["location"]
                        ):
                            location_url = fields["location"][field_value].strip("` ")

                    def platform_id_match(platform_id, text):
                        """检查平台ID是否在文本中出现，用于备用URL匹配"""
                        return platform_id.lower() in text.lower()

                    platform_info = {
                        "platformID": field_value,
                        "location": location_url,
                        "signature": "",
                    }
                    platform_info_list = [platform_info]
                processed_fields[field_name] = platform_info_list
            elif field_name == "internalName":
                # 确保internalName为字符串类型
                if isinstance(field_value, dict):
                    # 提取dict中的text字段或转换为字符串
                    processed_fields[field_name] = field_value.get(
                        "text", str(field_value)
                    )
                elif isinstance(field_value, list):
                    # 处理列表类型，取第一个元素的text或转换为字符串
                    if field_value and isinstance(field_value[0], dict):
                        processed_fields[field_name] = field_value[0].get("text", "")
                    else:
                        processed_fields[field_name] = str(field_value)
                else:
                    processed_fields[field_name] = (
                        str(field_value) if field_value is not None else ""
                    )
            elif field_name == "publishedDate":
                # 将毫秒级时间戳转换为指定格式的日期时间字符串
                try:
                    # 处理毫秒级时间戳
                    timestamp = int(field_value) / 1000
                    dt = datetime.datetime.fromtimestamp(timestamp)
                    processed_fields[field_name] = dt.strftime("%Y-%m-%d %H:%M")
                except (TypeError, ValueError):
                    # 保留原始值如果转换失败
                    processed_fields[field_name] = field_value
            else:
                processed_fields[field_name] = field_value

        # 按照定义的顺序添加字段
        for field_name in field_order:
            if field_name in processed_fields:
                app_info[field_name] = processed_fields[field_name]

        apps_list.insert(0, app_info)

    return apps_list


def save_apps_to_json(apps_list, output_file="apps_new.json"):
    """
    保存应用信息列表到JSON文件

    Args:
        apps_list: 应用信息列表
        output_file: 输出文件名

    Returns:
        str: 输出文件的路径
    """
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(apps_list, f, ensure_ascii=False, indent=2)

    print(f"成功转换{len(apps_list)}个应用信息到{output_file}")
    return output_file
