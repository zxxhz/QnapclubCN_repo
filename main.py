from config import config_instance
from feishu_data_processor import fetch_and_convert_data, save_apps_to_json
from update_repo import update_repo


def main():
    # 从飞书获取数据并转换
    apps_list = fetch_and_convert_data(config_instance)

    if apps_list:
        # 保存转换后的数据到JSON文件
        apps_file = save_apps_to_json(apps_list)

        # 使用转换后的数据更新仓库XML
        print("\n开始更新仓库XML文件...")
        update_repo(input_file=apps_file, output_file="repo.xml")


if __name__ == "__main__":
    main()
