import yaml
import os
import sys

CONFIG_FILE = "config.yaml"


class Config:
    """配置类，用于管理应用配置

    使用方法：
    1. 在其他文件中导入：from config import config_instance
    2. 访问配置项：config_instance.app_token, config_instance.app_secret等
    """

    def __init__(self):
        config = load_config()
        self.data_source: str = config.get("data_source", "")
        if not self.data_source:
            print("未指定数据来源, 请在config.yaml中配置'data_source'.", file=sys.stderr)
            sys.exit(1)
        if self.data_source == "feishu":
            self.app_token: str = config["feishu"].get("app_token", "")
            self.table_id: str = config["feishu"].get("table_id", "")
            self.view_id: str = config["feishu"].get("view_id", "")
            self.app_id: str = config["feishu"].get("app_id", "")
            self.app_secret: str = config["feishu"].get("app_secret", "")
        else:
            print(f"不支持的数据来源: {self.data_source} ,目前仅支持'feishu'.", file=sys.stderr)
            sys.exit(1)


def load_config():
    """读取 config.yaml, 不存在则报错退出"""
    try:
        if not os.path.exists(CONFIG_FILE):
            print("配置文件不存在, 请修改config.yaml后重试.", file=sys.stderr)
            sys.exit(1)
        else:
            # 文件存在，读取配置
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            return config
    except yaml.YAMLError as e:
        print(f"配置文件格式错误: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"读取配置文件时发生错误: {e}", file=sys.stderr)
        sys.exit(1)


# 创建默认配置实例供导入使用
# 这样在其他文件中可以直接导入这个实例，避免重复创建
config_instance = Config()

"""
使用示例：

# 在其他Python文件中使用配置
# 方法1：导入配置实例（推荐）
# from config import config_instance
# token = config_instance.app_token
# secret = config_instance.app_secret

# 方法2：创建新的配置实例
# from config import Config
# custom_config = Config()
# token = custom_config.app_token
"""
