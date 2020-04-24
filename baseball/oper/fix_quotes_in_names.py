# this is a one time fix to remove quotes from the names in the starters table
import sqlalchemy as sa


def remove_quotes_fix():

    engine = sa.create_engine('sqlite:///baseball.db', echo=True)
    # c = dbs.engine.connect()
    c = engine.connect()

    query = 'UPDATE starters ' \
            'SET player_nm = REPLACE(player_nm, \'\"\', \'\')'

    try:
        c.execute(query)
    except Exception as e:
        print("Something went wrong with the db_remove")
        c.close()
        return False

    query = 'SELECT * FROM starters LIMIT 10'
    results = c.execute(query).fetchall()
    print(results)

    return True
