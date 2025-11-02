# QnapclubCN_repo

QnapclubCN 的 qnap AppStore 软件源，使用飞书多维表格作为数据库，存储应用信息并自动生成仓库 XML 文件。

## 项目简介

本项目旨在提供一个自动化的 QNAP 应用仓库管理系统，通过飞书多维表格来维护应用信息，实现数据的可视化管理和自动生成符合 QNAP 应用商店格式的 XML 仓库文件。项目采用模块化设计，使用面向对象方法实现数据源抽象，支持灵活的数据处理和转换。

## 项目结构

```
QnapclubCN_repo/
├── .gitignore            # Git忽略文件
├── LICENSE               # 许可证文件
├── README.md             # 项目说明文档
├── apps.json             # 生成的应用数据JSON文件
├── config.py             # 配置管理模块
├── config.yaml.example   # 配置文件模板
├── data_sources/         # 数据源模块目录
│   ├── __init__.py       # 模块初始化文件
│   ├── base.py           # 数据源抽象基类
│   └── feishu.py         # 飞书数据源实现
├── main.py               # 主程序入口
├── repo.xml              # 生成的仓库XML文件
└── update_repo.py        # 仓库XML生成模块
```

## 核心功能

1. **模块化数据源设计**：使用抽象基类定义数据源接口，便于扩展不同的数据来源
2. **飞书多维表格集成**：从飞书多维表格获取应用数据，支持多种认证方式
3. **数据转换与处理**：自动处理飞书格式的数据，转换为标准 JSON 格式
4. **仓库 XML 生成**：将 JSON 格式的应用数据转换为 QNAP 应用商店所需的 XML 格式
5. **灵活的配置系统**：使用 YAML 格式配置文件，支持不同数据源的配置

## 安装与使用

### 环境要求

- Python 3.8+
- 依赖包：lark_oapi, lxml, pyyaml

### 安装依赖

```bash
pip install lark-oapi lxml pyyaml
```

### 配置设置

1. 复制配置文件模板并填写必要信息：

```bash
cp config.yaml.example config.yaml
```

2. 编辑 `config.yaml` 文件，填入必要的配置信息（使用 YAML 格式）：

```yaml
# 数据来源配置
data_source: feishu # 当前仅支持feishu

# 飞书配置信息
feishu:
  app_token: "your_app_token_here" # 必填：飞书多维表格的应用Token
  table_id: "your_table_id_here" # 必填：多维表格ID
  view_id: "" # 选填：视图ID，不填则使用默认视图
  app_id: "your_app_id_here" # 必填：应用ID
  app_secret: "your_app_secret_here" # 必填：应用密钥
```

### 运行程序

运行主程序，自动完成从数据获取到仓库生成的全流程：

```bash
python main.py
```

程序执行成功后，将生成两个文件：

- `apps.json` - 转换后的应用数据 JSON 文件
- `repo.xml` - 生成的仓库 XML 文件

## 工作流程

1. **配置加载**：程序启动时通过 `config.py` 加载 `config.yaml` 中的配置信息
2. **数据源初始化**：根据配置创建相应的数据源实例（目前仅支持飞书）
3. **数据获取与转换**：
   - 通过 `FeishuDataSource.fetch_data()` 方法从飞书获取数据
   - 数据以生成器形式返回，需要转换为列表进行处理
4. **JSON 保存**：将转换后的数据保存到 `apps.json` 文件
5. **XML 生成**：调用 `update_repo()` 函数将 JSON 数据转换为 XML 格式并保存

## 模块说明

### main.py

主程序入口，负责协调各模块工作流程：

- 加载配置
- 初始化数据源
- 获取和处理数据
- 保存 JSON 文件
- 生成 XML 仓库文件

### data_sources/base.py

数据源抽象基类，定义所有数据源必须实现的接口：

```python
class DataSource(ABC):
    @abstractmethod
    def fetch_data(self) -> Iterator[Dict[str, Any]]:
        """获取数据的生成器方法"""
        pass
```

### data_sources/feishu.py

飞书数据源实现，继承自 `DataSource` 基类：

- 实现 `fetch_data()` 方法，以生成器形式返回数据
- 处理飞书多维表格的各种字段类型
- 支持认证和 API 调用

### config.py

配置管理模块：

- 提供 `Config` 类管理应用配置
- 实现 `load_config()` 函数读取 YAML 配置文件
- 支持不同数据源的配置验证

### update_repo.py

仓库 XML 生成模块：

- 提供 `update_repo()` 函数将 JSON 数据转换为 XML 格式
- 支持自定义输入输出文件名
- 生成符合 QNAP 应用商店规范的 XML 结构

## 自定义配置

### 修改输出文件名

可以修改 `main.py` 中的相关代码来自定义输出文件名：

```python
# 修改JSON输出文件名
with open("自定义_apps.json", "w", encoding="utf-8") as f:
    json.dump(apps_list, f, ensure_ascii=False, indent=2)

# 修改XML输出文件名
update_repo(input_file="apps.json", output_file="自定义_repo.xml")
```

### 扩展新的数据源

要添加新的数据源实现：

1. 在 `data_sources` 目录下创建新的数据源文件
2. 实现 `DataSource` 抽象基类的 `fetch_data()` 方法
3. 在 `data_sources/__init__.py` 中导出新的数据源类
4. 在 `config.py` 中添加新数据源的配置支持

## 注意事项

1. 确保飞书 API 配置正确，包括应用 Token、表格 ID 和认证信息
2. 生成的 XML 文件需要放置在 Web 服务器可访问的位置，以提供给 QNAP 设备访问
3. 飞书表格中的字段名称应与 `update_repo.py` 中处理的字段保持一致
4. 如果数据量较大，`fetch_data()` 方法返回的生成器有助于减少内存占用

## 许可证

本项目采用 [GNU General Public License v3.0](LICENSE) 许可证。

## 贡献

欢迎提交 Issues 和 Pull Requests 来改进本项目。如有任何问题或建议，请在 GitHub 上提交 Issue。
