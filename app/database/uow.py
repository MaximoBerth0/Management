class UnitOfWork:
    def __init__(self, db):
        self.db = db

    def commit(self):
        self.db.commit()

    def rollback(self):
        self.db.rollback()
