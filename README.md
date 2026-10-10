# Claude-Code 工作区

本仓库包含若干独立小项目。

## 目录

| 目录 | 说明 |
| --- | --- |
| [`1024test/`](1024test/) | 部署验收测试项目（Python TCP 客户端/服务端 + MySQL） |
| [`previous-projects/`](previous-projects/) | 历史项目：Symbol Finder、Capacity Converter |

## 1024test

Python + MySQL 的客户端/服务端示例项目，用于 Linux（systemd）部署与功能验收。

- 服务端 `server.py`：systemd 托管，后台持久运行、开机自启。
- 客户端命令 `1024test`：`-m` 创建用户、`-l` 登录、`-v` 查看版本。

详见 [1024test/README.md](1024test/README.md)。

## 历史项目（已归档）

- **Symbol Finder** — Windows 特殊符号查找工具（Tkinter 桌面应用，797 个符号）。
- **Capacity Converter** — 二进制容量换算工具（JS CLI + 网页版）。

详见 [previous-projects/README.md](previous-projects/README.md)。
