# setting up the sqlite database using sqlalchemy
import sqlite3 as sql
import sqlalchemy as sa
import class_structure as cl

# setup engine and database
engine = sa.create_engine('sqlite:///baseball.db', echo=True)

# safe to call multiple times as it will FIRST check for table presence
cl.metadata.create_all(engine)


