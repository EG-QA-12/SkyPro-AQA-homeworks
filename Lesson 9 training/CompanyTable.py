from sqlalchemy import create_engine
from sqlalchemy.sql import text

class CompanyTable:
    __scripts = {
        "select": "select * from company where deleted_at is null",
        "select only active": "select * from company where \"is_active\" = true  and deleted_at is null",
        "delete by id": text("delete from company where id =:id_to_delete"),
        "insert new": text("insert into company(\"name\") values (:new_name)"),
        "get max id": "select MAX(\"id\") from company where deleted_at is null"
    }

    def __init__(self, connection_string):
        self.__db = create_engine(connection_string)

    def get_companies(self):
        return self.__db.execute(self.__scripts["select"]).fetchall()

    def get_active_companies(self):
        return self.__db.execute(self.__scripts["select only active"]).fetchall()


    def delete(self, id):
        self.__db.execute(self.__scripts["delete by id"], id_to_delete = id)

    def create(self, name):
        self.__db.execute(self.__scripts["insert new"], new_name=name)

    def get_max_id(self):
        return self.__db.execute(self.__scripts["get max id"]). \
            fetchall()[0][0]
