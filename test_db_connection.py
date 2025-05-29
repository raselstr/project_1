import psycopg2
from psycopg2 import OperationalError

def test_connection(host, user, password, dbname, port=5432):
    try:
        conn = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            dbname=dbname,
            port=port,
            connect_timeout=3
        )
        conn.close()
        print(f"✅ Success connecting to PostgreSQL at host '{host}'")
        return True
    except OperationalError as e:
        print(f"❌ Failed connecting to PostgreSQL at host '{host}': {e}")
        return False

if __name__ == "__main__":
    user = "raselstr"
    password = "r283l8tr"
    dbname = "tkdd"
    port = 5432

    # Test host 'db' (Docker container hostname)
    test_connection("db", user, password, dbname, port)

    # Test host 'localhost' (local machine)
    test_connection("localhost", user, password, dbname, port)
