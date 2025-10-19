# QnapclubCN_repo

QnapclubCN 的 qnap AppStore 软件源，使用飞书多维表格作为数据库，存储应用信息并自动生成仓库XML文件。

## 项目简介

本项目旨在提供一个自动化的QNAP应用仓库管理系统，通过飞书多维表格来维护应用信息，实现数据的可视化管理和自动生成符合QNAP应用商店格式的XML仓库文件。

## 项目结构

```
QnapclubCN_repo/
├── .gitignore            # Git忽略文件
├── LICENSE               # 许可证文件
├── README.md             # 项目说明文档
├── config.py.example     # 配置文件模板
├── feishu_data_processor.py  # 飞书数据处理模块
├── main.py               # 主程序入口
├── update_repo.py        # 仓库XML生成模块
├── apps_new.json         # 生成的应用数据JSON文件
└── repo_build_YYYYMMDD.xml  # 生成的仓库XML文件
```

## 功能说明

1. **数据获取与转换**：从飞书多维表格获取应用数据，转换为标准JSON格式
2. **仓库XML生成**：将JSON格式的应用数据转换为QNAP应用商店所需的XML格式
3. **自动处理字段**：移除飞书表格中的"type"字段，保留"text"内容
4. **字段顺序保持**：确保生成的JSON和XML文件中的字段顺序符合规范

## 安装与使用

### 环境要求

- Python 3.6+
- 依赖包：lark_oapi, lxml, json, collections

### 安装依赖

```bash
pip install lark-oapi lxml
```

### 配置设置

1. 复制配置文件模板并填写必要信息：

```bash
cp config.py.example config.py
```

2. 编辑 `config.py` 文件，填入飞书API所需的信息：

```python
# 飞书配置信息
app_token = "你的应用Token"
user_access_token = "你的用户访问Token"
table_id = "你的表格ID"
```

### 运行程序

运行主程序，自动完成从数据获取到仓库生成的全流程：

```bash
python main.py
```

## 工作流程

1. **数据获取**：通过 `feishu_data_processor.py` 中的 `fetch_and_convert_data()` 函数从飞书获取数据
2. **数据转换**：将飞书格式的数据转换为标准JSON格式，保存到 `apps_new.json`
3. **XML生成**：通过 `update_repo.py` 中的 `update_repo()` 函数将JSON数据转换为XML格式
4. **结果输出**：生成以日期命名的XML文件，如 `repo_build_20251019.xml`

## 模块说明

### main.py

主程序入口，集成了数据处理和仓库生成功能。

### feishu_data_processor.py

- `fetch_and_convert_data(config)`: 从飞书获取数据并转换为标准格式
- `save_apps_to_json(apps_list, output_file)`: 保存应用数据到JSON文件

### update_repo.py

- `update_repo(input_file, output_file)`: 将应用数据JSON转换为XML格式的仓库文件

## 自定义配置

### 修改字段顺序

在 `feishu_data_processor.py` 中，可以修改 `field_order` 列表来调整字段顺序：

```python
field_order = ["name", "changeLog", "category", "type", ...]
```

### 调整输出文件名

可以通过修改函数参数来自定义输出文件名：

```python
# 修改JSON输出文件名
save_apps_to_json(apps_list, output_file='自定义文件名.json')

# 修改XML输出文件名
update_repo(input_file='apps.json', output_file='自定义仓库.xml')
```

## 注意事项

1. 确保飞书API配置正确，包括应用Token、用户访问Token和表格ID
2. 飞书表格中的字段名称应与 `field_order` 中的字段名保持一致
3. 生成的XML文件需要放置在Web服务器可访问的位置，以提供给QNAP设备访问

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。

## 贡献

欢迎提交Issues和Pull Requests来改进本项目。
