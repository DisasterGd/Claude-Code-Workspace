from setuptools import setup

setup(
    name="1024test",
    version="1.0.0",
    description="1024test 部署验收测试项目（TCP 客户端/服务端）",
    py_modules=["cli", "server", "db", "config"],
    install_requires=["pymysql", "python-dotenv"],
    entry_points={"console_scripts": ["1024test=cli:main"]},
)
