import app
import requests

def test_db_connection():
    try:
        app.get_db()
    except app.psycopg2.OperationalError as e:
        print(f'Connection failed {e.pgcode}')

def test_root():
    assert requests.get('http://localhost:3400').status_code == 200
    