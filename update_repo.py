from lxml import etree
import time
import json

def update_repo(input_file="apps.json", output_file=None):
    """
    根据应用数据更新仓库XML文件
    
    Args:
        input_file: 输入的apps.json文件路径
        output_file: 输出的XML文件路径，如果为None则自动生成带日期的文件名
    """
    apps: list = []
    # 从指定文件读取应用数据
    with open(input_file, "r", encoding="utf-8") as f:
        apps = json.load(f)

    # 创建根元素 <plugins>
    root = etree.Element("plugins")
    etree.SubElement(root, "cachechk").text = time.strftime("%Y%m%d%H%M")

    for app in apps:
        item = etree.SubElement(root, "item")
        etree.SubElement(item, "name").text = app.get("name", "")
        etree.SubElement(item, "changeLog").text = app.get("changeLog", "")
        etree.SubElement(item, "category").text = app.get("category", "")
        etree.SubElement(item, "type").text = app.get("type", "")
        etree.SubElement(item, "icon80").text = app.get("icon80", "https://help.qnapclub.cn/upload/logo_80x80.png")
        etree.SubElement(item, "icon100").text = app.get("icon100", "https://help.qnapclub.cn/upload/logo_100x100.png")
        etree.SubElement(item, "description").text = app.get("description", "QnapclubCN")
        etree.SubElement(item, "fwVersion").text = app.get("fwVersion", "")
        etree.SubElement(item, "version").text = app.get("version", "")
        # 支持 platform 为列表
        platforms = app.get("platform", [])
        if isinstance(platforms, dict):
            platforms = [platforms]
        for platform_data in platforms:
            platform = etree.SubElement(item, "platform")
            etree.SubElement(platform, "platformID").text = platform_data.get(
                "platformID", ""
            )
            etree.SubElement(platform, "location").text = platform_data.get("location", "")
            etree.SubElement(platform, "signature").text = platform_data.get(
                "signature", ""
            )
        etree.SubElement(item, "internalName").text = app.get("internalName", "")
        etree.SubElement(item, "publishedDate").text = app.get("publishedDate", "")
        etree.SubElement(item, "maintainer").text = app.get("maintainer", "")
        etree.SubElement(item, "developer").text = app.get("developer", "")
        etree.SubElement(item, "forumLink").text = app.get("forumLink", "")
        etree.SubElement(item, "language").text = app.get("language", "")
        etree.SubElement(item, "snapshot").text = app.get("snapshot", "")
        etree.SubElement(item, "bannerImg").text = app.get("bannerImg", "")
        etree.SubElement(item, "tutorialLink").text = app.get("tutorialLink", "")

    # 美化XML（添加换行和缩进）
    etree.indent(root, space="  ")

    # 生成XML字符串
    xml_str = etree.tostring(
        root, encoding="utf-8", xml_declaration=True, pretty_print=True
    )

    # 如果没有指定输出文件名，自动生成带日期的文件名
    if output_file is None:
        output_file = f"repo_build_{time.strftime('%Y%m%d')}.xml"

    # 保存到文件
    with open(output_file, "wb") as f:
        f.write(xml_str)

    print(f"已成功生成仓库文件: {output_file}")
    return output_file


# 如果直接运行此文件，则执行默认更新
if __name__ == "__main__":
    update_repo()
