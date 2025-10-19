import json
from collections import OrderedDict

import lark_oapi as lark
from lark_oapi.api.bitable.v1 import *


def fetch_and_convert_data(config):
    """
    从飞书获取数据并转换为apps.json格式
    
    Args:
        config: 包含app_token、table_id和user_access_token的配置对象
        
    Returns:
        list: 转换后的应用信息列表
    """
    # 创建client
    # 使用 user_access_token 需开启 token 配置, 并在 request_option 中配置 token
    client = (
        lark.Client.builder()
        .enable_set_token(True)
        .log_level(lark.LogLevel.DEBUG)
        .build()
    )
    
    # 定义apps.json的字段顺序
    field_order = ["name", "changeLog", "category", "type", "icon80", "icon100", "description", "fwVersion", "version", "platform", "internalName", "publishedDate", "maintainer", "developer", "forumLink", "language", "snapshot", "bannerImg", "tutorialLink"]

    # 构造请求对象
    request: SearchAppTableRecordRequest = (
        SearchAppTableRecordRequest.builder()
        .app_token(config.app_token)
        .table_id(config.table_id)
        .user_id_type("open_id")
        .page_size(20)
        .request_body(
            SearchAppTableRecordRequestBody.builder()
            .view_id("vewAbrcCsi")
            .field_names(field_order)  # 使用定义的字段顺序
            .build()
        )
        .build()
    )

    # 发起请求
    option = (
        lark.RequestOption.builder()
        .user_access_token(config.user_access_token)
        .build()
    )
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
            if isinstance(field_value, list) and len(field_value) > 0 and 'text' in field_value[0]:
                processed_fields[field_name] = field_value[0]['text']
            elif field_name == 'platform':
                # 处理platform字段，转换为apps.json的格式
                platform_info = {
                    "platformID": field_value,
                    "location": "",  # 需要根据实际情况填充
                    "signature": ""   # 需要根据实际情况填充
                }
                processed_fields[field_name] = [platform_info]
            else:
                processed_fields[field_name] = field_value
        
        # 按照定义的顺序添加字段
        for field_name in field_order:
            if field_name in processed_fields:
                app_info[field_name] = processed_fields[field_name]
        
        apps_list.append(app_info)
    
    return apps_list


def save_apps_to_json(apps_list, output_file='apps_new.json'):
    """
    保存应用信息列表到JSON文件
    
    Args:
        apps_list: 应用信息列表
        output_file: 输出文件名
    
    Returns:
        str: 输出文件的路径
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(apps_list, f, ensure_ascii=False, indent=2)
    
    print(f"成功转换{len(apps_list)}个应用信息到{output_file}")
    return output_file