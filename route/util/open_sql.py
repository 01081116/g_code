import pymysql


class PyMySQLData:
    def __init__(self, host, port, user, password, db, charset='utf8mb4'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db
        self.charset = charset
        self.connection = None
        self.cursor = None

    def connect(self):
        self.connection = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            db=self.db,
            charset=self.charset,
            cursorclass=pymysql.cursors.DictCursor
        )
        self.cursor = self.connection.cursor()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()

    def query(self, sql, params=None):
        self.connect()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            result = self.cursor.fetchall()
        except Exception as e:
            print(f"执行SQL查询时出现错误: {e}")
            result = None
        finally:
            self.close()
        return result

    def insert(self, sql, values):
        self.connect()
        try:
            self.cursor.execute(sql, values)
            self.connection.commit()
        except Exception as e:
            print(f"执行SQL插入时出现错误: {e}")
            self.connection.rollback()
        finally:
            self.close()

    def execute(self, sql, params=None):
        self.connect()
        try:
            if params:
                self.cursor.execute(sql, params)
            else:
                self.cursor.execute(sql)
            self.connection.commit()
        except Exception as e:
            print(f"执行SQL插入/更新时出现错误: {e}")
            self.connection.rollback()
        finally:
            self.close()
