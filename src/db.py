import sqlite3


class Database:
    def __init__(self, name):
        self.table = name
        self.con = sqlite3.connect(f"{name}.db")
        self.con.execute(f"CREATE TABLE IF NOT EXISTS {name} (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, display_name TEXT, io TEXT, datetime DEFAULT CURRENT_TIMESTAMP)")
        res = self.con.execute(f"SELECT * from {name}")

    def enter(self, user_id: int, display_name: str):
        self.con.execute(
            f"INSERT INTO {self.table}(user_id, display_name, io) VALUES (?, ?, 'in')",
            (user_id, display_name)
        )
        self.con.commit()

    def leave(self, user_id: int, display_name: str):
        self.con.execute(
            f"INSERT INTO {self.table}(user_id, display_name, io) VALUES (?, ?, 'out')",
            (user_id, display_name)
        )
        self.con.commit()

    def current_all(self):
        res = self.con.execute(
            f"SELECT user_id, display_name, io, strftime('%s', MAX(datetime)) FROM {self.table} GROUP BY user_id, io"
        )

        current = {}

        for r in res:
            if r[0] not in current:
                current[r[0]] = {}
            current[r[0]]["display_name"], current[r[0]][r[2]] = r[1], int(r[3])
            if ("in" in current[r[0]] and "out" in current[r[0]]) and (current[r[0]]["in"] < current[r[0]]["out"]):
                del current[r[0]]

        return current

    def get_by_user_id(self, user_id):
        res = self.con.execute(
            f"SELECT user_id, display_name, io, strftime('%s', datetime) FROM {self.table} WHERE user_id = ?", (user_id, )
        )

        return [r for r in res]

    def get_by_date(self, str_time: str):
        res = self.con.execute(
            f"SELECT user_id, display_name, io, strftime('%s', datetime) FROM {self.table} WHERE date(datetime) = ?", (str_time, )
        )

        return [r for r in res]

    def get_all(self):
        res = self.con.execute(
            f"SELECT user_id, display_name, io, strftime('%s', datetime) FROM {self.table}"
        )

        return [r for r in res]
