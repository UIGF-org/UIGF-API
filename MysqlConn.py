import pymysql
import json


class MysqlConn:
    def __init__(self):
        self.conn = None
        self.cursor = None
        with open("config/db.json", "r") as f:
            mysql_config = json.loads(f.read())
        self.__host = mysql_config["host"]
        self.__port = mysql_config["port"]
        self.__user = mysql_config["user"]
        self.__password = mysql_config["password"]
        self.__database = mysql_config["database"]

    def connect(self):
        try:
            self.conn = pymysql.connect(host=self.__host, port=self.__port, user=self.__user, password=self.__password,
                                        database=self.__database, charset="utf8")
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(e)
            return False
        else:
            return True

    def close(self):
        self.cursor.close()
        self.conn.close()

    def execute(self, sql, params=None):
        try:
            self.connect()
            self.cursor.execute(sql, params)
            self.conn.commit()
        except Exception as e:
            print("SQL Execute error: " + str(e))
            print("Original SQL: " + sql)
            self.conn.rollback()
            return False
        else:
            return True

    def fetch_one(self, sql):
        try:
            self.connect()
            self.cursor.execute(sql)
            result = self.cursor.fetchone()
            self.close()
        except Exception as e:
            print("SQL fetch error: " + str(e))
            print("Original SQL: " + sql)
            result = None
        if result is None:
            return None
        else:
            return result

    def fetch_all(self, sql):
        try:
            self.connect()
            self.cursor.execute(sql)
            result = self.cursor.fetchall()
            self.close()
        except Exception as e:
            print("SQL fetchall error: " + str(e))
            print("Original SQL: " + sql)
            result = ()
        return result
