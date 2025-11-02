import json

from config import config_instance
from data_sources import feishu
from update_repo import update_repo


def main():
    # 从飞书获取数据并转换
    if config_instance.data_source == "feishu":
        apps_list: list[dict] = feishu.fetch_and_convert_data(config_instance)

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
