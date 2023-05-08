import app
import requests
from selenium import webdriver

def test_db_connection():
    try:
        app.get_db()
    except app.psycopg2.OperationalError as e:
        print(f'Connection failed {e.pgcode}')

def test_root():
    assert requests.get('http://localhost:3400').status_code == 200

def test_browser():
    driver = webdriver.Chrome('chromedriver')
    driver.get("http://localhost:3400")
    assert driver.title == 'Page Title'
    driver.close()
    