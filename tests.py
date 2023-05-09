import app
import requests
from selenium import webdriver
import re

def test_uuid_regex():
    assert re.match(app.UUID.regex, '123e4567-e89b-12d3-a456-426655440000') is not None

def test_db_connection():
    try:
        app.get_db()
    except app.psycopg2.OperationalError as e:
        print(f'Connection failed {e.pgcode}')

def test_app():
    assert requests.get('http://localhost:3400').status_code == 200

def test_browser():
    driver = webdriver.Chrome('chromedriver')
    driver.get("http://localhost:3400")
    assert driver.title == 'Page Title'
    driver.close()
    