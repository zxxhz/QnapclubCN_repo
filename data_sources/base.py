from abc import ABC, abstractmethod
from typing import Dict, Any, Iterator


class DataSource(ABC):
    """数据源基类"""

    def __init__(self):
        pass

    @abstractmethod
    def fetch_data(self) -> Iterator[Dict[str, Any]]:
        """获取数据的生成器方法"""
        pass
