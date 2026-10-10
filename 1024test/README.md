# 1024test

部署验收测试项目：Python TCP **客户端/服务端** + MySQL，最终由 systemd 托管。

## 架构

```
1024test (客户端命令)  ──TCP──>  server.py (服务端, systemd 托管)  ──>  MySQL
```

- 客户端命令 `1024test` 通过 TCP 连接服务端，服务端操作 MySQL。
- 服务端由 systemd 保证后台持久运行、开机自启。

## 命令与验收行为

| 命令 | 期望输出 | 说明 |
| --- | --- | --- |
| `1024test -m user 123456` | `true` | 创建用户 `user`（密码 `123456`） |
| `1024test -l user` | `password：` | 用户存在，等待输入密码 |
| （随后输入）`123456` | `logining` | 密码校验通过，登录成功 |
| `1024test -l user`（用户已删除） | `无该用户` | 用户不存在 |
| `1024test -v`（服务已关闭） | `无法执行` | 服务端未运行，客户端连不上 |

## 文件结构

```
1024test/
├── server.py          服务端（TCP 监听 + MySQL 操作）
├── cli.py             客户端命令 1024test
├── db.py              MySQL 数据访问层
├── config.py          读取 .env 配置
├── setup.py           安装入口（生成 1024test 命令）
├── requirements.txt   依赖：pymysql、python-dotenv
├── .env.example       配置模板（复制为 .env 填写真实值）
├── 1024test.service   systemd 单元文件
└── README.md          本文档
```

## 部署步骤（Ubuntu）

> 假设项目已解压到 `/home/test`（目录内即为全部文件，无二级目录）。

### 1. 准备数据库

```bash
# 创建库 1024test、用户 test（仅赋该库增删改查权限）——用 root 执行
mysql -u root -p -e "
CREATE DATABASE IF NOT EXISTS 1024test DEFAULT CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS 'test'@'localhost' IDENTIFIED BY '你的密码';
GRANT SELECT,INSERT,UPDATE,DELETE ON 1024test.* TO 'test'@'localhost';
FLUSH PRIVILEGES;"
```

### 2. 填写配置

```bash
cd /home/test
cp .env.example .env
vim .env   # 填写 DB_PASSWORD 等
```

### 3. 创建虚拟环境并安装依赖

```bash
cd /home/test
python3 -m venv venv
venv/bin/pip install -r requirements.txt
venv/bin/pip install -e .      # 生成 venv/bin/1024test 命令
ln -s /home/test/venv/bin/1024test /usr/local/bin/1024test
```

### 4. 用 systemd 托管服务

```bash
cp /home/test/1024test.service /etc/systemd/system/1024test.service
systemctl daemon-reload
systemctl enable --now 1024test    # 启动 + 开机自启
```

> 若虚拟环境名不是 `venv`，请同步修改 `1024test.service` 里的 `ExecStart` 路径。

### 5. 常用运维命令

```bash
systemctl status 1024test    # 查看状态
systemctl restart 1024test   # 重启服务
systemctl stop 1024test      # 关闭服务
journalctl -u 1024test -f    # 查看日志
```
