import json

from config import config_instance
from data_sources import FeishuDataSource, SQLiteDataSource
from update_repo import update_repo


def main():
    # 从飞书获取数据并转换
    if config_instance.data_source == "feishu":
        feishu_ds = FeishuDataSource(config_instance)
        apps_list: list[dict] = list(feishu_ds.fetch_data())
    # 从SQLite数据库获取数据并转换
    elif config_instance.data_source == "sqlite":
        sqlite_ds = SQLiteDataSource(config_instance)
        apps_list: list[dict] = list(sqlite_ds.fetch_data())

    if apps_list:
        # 保存转换后的数据到JSON文件
        with open("apps.json", "w", encoding="utf-8") as f:
            json.dump(apps_list, f, ensure_ascii=False, indent=2)

        print(f"成功转换{len(apps_list)}个应用信息到apps.json")

        # 使用转换后的数据更新仓库XML
        print("\n开始更新仓库XML文件...")
        update_repo(input_file="apps.json", output_file="repo.xml")
        print("仓库XML文件更新完成")
    else:
        print("未获取到有效应用数据，仓库XML文件未更新")


if __name__ == "__main__":
    main()
