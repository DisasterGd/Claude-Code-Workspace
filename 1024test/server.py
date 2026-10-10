"""1024test 服务端：由 systemd 托管，监听本地端口，操作 MySQL。

协议（每行一条命令，回复一行结果）：
    REGISTER <user> <password>  -> true / false
    CHECK <user>                -> EXISTS / NOT_EXISTS
    LOGIN <user> <password>     -> OK / FAIL
    PING                        -> PONG
"""
import logging
import socketserver

import config
import db

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s"
)
log = logging.getLogger("1024test.server")


class RequestHandler(socketserver.StreamRequestHandler):
    def handle(self):
        line = self.rfile.readline()
        if not line:
            return
        raw = line.decode("utf-8").strip()
        log.info("收到命令: %s", raw)
        resp = self.dispatch(raw)
        self.wfile.write((resp + "\n").encode("utf-8"))
        self.wfile.flush()

    def dispatch(self, raw):
        parts = raw.split(" ")
        cmd = parts[0].upper()
        args = parts[1:]
        conn = db.get_connection(config.CONF)
        try:
            db.ensure_table(conn)
            if cmd == "REGISTER" and len(args) == 2:
                return "true" if db.create_user(conn, args[0], args[1]) else "false"
            if cmd == "CHECK" and len(args) == 1:
                return "EXISTS" if db.user_exists(conn, args[0]) else "NOT_EXISTS"
            if cmd == "LOGIN" and len(args) == 2:
                return "OK" if db.verify_user(conn, args[0], args[1]) else "FAIL"
            if cmd == "PING":
                return "PONG"
            return "ERROR"
        except Exception as exc:  # noqa: BLE001
            log.exception("处理命令失败: %s", exc)
            return "ERROR"
        finally:
            conn.close()


def main():
    conf = config.CONF
    server = socketserver.ThreadingTCPServer(
        (conf.SERVER_HOST, conf.SERVER_PORT), RequestHandler
    )
    log.info("1024test 服务已启动，监听 %s:%s", conf.SERVER_HOST, conf.SERVER_PORT)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
