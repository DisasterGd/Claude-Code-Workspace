"""读取 .env 配置文件（数据库连接 + 服务端监听地址）。"""
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # dotenv 未安装时退化为仅读系统环境变量
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

if load_dotenv is not None and ENV_FILE.exists():
    load_dotenv(ENV_FILE)


def _get(name, default):
    value = os.environ.get(name)
    return value if value else default


class Config:
    def __init__(self):
        self.DB_HOST = _get("DB_HOST", "127.0.0.1")
        self.DB_PORT = int(_get("DB_PORT", "3306"))
        self.DB_USER = _get("DB_USER", "test")
        self.DB_PASSWORD = _get("DB_PASSWORD", "")
        self.DB_NAME = _get("DB_NAME", "1024test")
        self.SERVER_HOST = _get("SERVER_HOST", "127.0.0.1")
        self.SERVER_PORT = int(_get("SERVER_PORT", "9000"))


# 模块级单例：服务端与客户端共用
CONF = Config()
