from sqlalchemy import text

from scripts.database.database import engine

def test():

    with engine.connect() as conn:

        version = conn.execute(
            text("SELECT version();")
        )

        print(version.fetchone())


if __name__ == "__main__":

    test()