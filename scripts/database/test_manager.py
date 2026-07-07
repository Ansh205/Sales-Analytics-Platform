from scripts.database.database_manager import DatabaseManager


def main():

    db = DatabaseManager()

    print("=" * 50)

    print("Testing Database Manager")

    print("=" * 50)

    db.test_connection()

    print()

    print("Orders Table Exists :")

    print(db.table_exists("orders"))

    print()

    print("Returns Table Exists :")

    print(db.table_exists("returns"))

    print()

    print("People Table Exists :")

    print(db.table_exists("people"))

    db.close()


if __name__ == "__main__":

    main()