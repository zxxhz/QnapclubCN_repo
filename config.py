import json
import os

CONFIG_FILE = "config.json"


class Config:
    """配置类，用于管理应用配置
    
    使用方法：
    1. 在其他文件中导入：from config import config_instance
    2. 访问配置项：config_instance.app_token, config_instance.app_secret等
    """
    def __init__(self):
        config = load_config()
        self.app_token = config.get("app_token", "")
        self.table_id = config.get("table_id", "")
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.user_access_token = config.get("user_access_token", "")


def load_config():
    """读取 config.json, 不存在则创建并返回默认配置"""
    default_config = {
        "app_token": "your_app_token_here",
        "table_id": "your_table_id_here",
        "app_id": "your_app_id_here",
        "app_secret": "your_app_secret_here",
    }
    try:
        if not os.path.exists(CONFIG_FILE):
            # 文件不存在，创建并写入默认配置
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(default_config, f, ensure_ascii=False, indent=4)
            print("配置文件不存在，已创建默认配置。")
            return default_config
        else:
            # 文件存在，读取配置
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
    except json.JSONDecodeError as e:
        print(f"配置文件格式错误: {e}")
        return default_config
    except Exception as e:
        print(f"读取配置文件时发生错误: {e}")
        return default_config


# 如果需要保存配置功能，可以取消下面的注释

# def save_config(config):
#     """保存配置到 config.json"""
#     try:
#         with open(CONFIG_FILE, "w", encoding="utf-8") as f:
#             json.dump(config, f, ensure_ascii=False, indent=4)
#     except Exception as e:
#         print(f"保存配置文件时发生错误: {e}")

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
