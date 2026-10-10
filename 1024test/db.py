"""MySQL 数据访问层：建表 + 用户的增、查、校验。"""
import pymysql


def get_connection(conf):
    return pymysql.connect(
        host=conf.DB_HOST,
        port=conf.DB_PORT,
        user=conf.DB_USER,
        password=conf.DB_PASSWORD,
        database=conf.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )


def ensure_table(conn):
    with conn.cursor() as cur:
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(64) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
    conn.commit()


def create_user(conn, username, password):
    """创建用户，重名时返回 False。"""
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, password),
            )
        conn.commit()
        return True
    except pymysql.err.IntegrityError:
        conn.rollback()
        return False


def user_exists(conn, username):
    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM users WHERE username = %s", (username,))
        return cur.fetchone() is not None


def verify_user(conn, username, password):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT 1 FROM users WHERE username = %s AND password = %s",
            (username, password),
        )
        return cur.fetchone() is not None
