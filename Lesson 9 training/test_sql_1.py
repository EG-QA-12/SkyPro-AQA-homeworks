from sqlalchemy import create_engine, inspect
from sqlalchemy.sql import text

db_connection_string = "postgresql://x_clients_user:ypYaT7FBULZv2VxrJuOHVoe78MEElWlb@dpg-crgp14o8fa8c73aritj0-a.frankfurt-postgres.render.com/x_clients_db_75hr"

def test_db_connection():
    db = create_engine(db_connection_string)
    inspector = inspect(db)
    names = inspector.get_table_names()
    assert names[0] == 'app_users'

def test_select ():
    db = create_engine(db_connection_string)
    rows = db.execute("select* from company").fetchall()
    row1 = rows[0]
    assert row1 [0] == 2895
    assert row1["name"] == "Asi test"

def test_select_1_row():
    db = create_engine(db_connection_string)
    sql_statement = text("select * from company where id = :company_id")
    rows = db.execute(sql_statement, company_id = 3080).fetchall()

    assert len(rows) == 1
    assert rows[0]["name"] == "Empoyer get ind company"

def test_select_1_row_with_two_filters():
    db = create_engine(db_connection_string)
    sql_statement = text("select * from company where \"is_active\" = :is_active and id >= :id")
    rows = db.execute(sql_statement, id=3212, is_active=True).fetchall()

    assert len(rows) == 1

def test_select_1_row_with_two_filters():
    db = create_engine(db_connection_string)
    sql_statement = text("select * from company where \"is_active\" = :is_active and id >= :id")
    my_params = {
        'id': 3215,
        'is_active': True
    }

    rows = db.execute(sql_statement, my_params).fetchall()

    assert len(rows) == 3

def test_insert():
    db = create_engine(db_connection_string)
    sql = text("insert into company(\"name\") values (:new_name)")
    rows = db.execute(sql, new_name = 'SkyPro')

def test_update():
    db = create_engine(db_connection_string)
    sql = text("update company set description = :descr where id = :id")
    rows = db.execute(sql, descr = 'New descr', id = 3277)

def test_delete():
    db = create_engine(db_connection_string)
    sql = text("delete from company where id = :id")
    rows = db.execute(sql, id = 3277)