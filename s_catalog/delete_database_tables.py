'''
Thia module removes all the tables from s_classifieds db
'''
from sqlalchemy import create_engine
import create_database


def drop_tables(tables):
    engine = create_engine("postgresql://postgres:postgres@localhost/s_classifieds")
    for table in tables:
        table.__table__.drop(engine)


if __name__ == "__main__":
    tables_to_drop = [create_database.Ad, create_database.SubCategory, create_database.Category,
                      create_database.City, create_database.User]
    drop_tables(tables_to_drop)