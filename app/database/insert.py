from app.database import connector
from app.logger import logs


class Session(object):
    def __init__(self, user, password, host, port, db):
        self.engine = connector.engine(user, password, host, port, db)
        self.session = connector.session(self.engine)

    def insert_one(self, row):
        if row.abstract:
            self.session.add(row)
        try:
            self.session.commit()
        except Exception as e:
            logs.error(e)
            self.session.rollback()

    def insert_all(self, rows):
        self.session.add_all(rows)
        try:
            self.session.commit()
        except:
            self.session.rollback()

    def close(self):
        self.session.close()