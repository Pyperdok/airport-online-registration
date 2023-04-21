from flask import Flask
from flask import request
import psycopg2
from werkzeug.routing import BaseConverter

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

app = Flask(__name__)
class UUID(BaseConverter):
    regex = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
app.url_map.converters['uuid'] = UUID

def get_db_connection():
    conn = psycopg2.connect('postgresql://postgres:12345678@localhost:5432/airport')
    conn.set_client_encoding('UTF8')
    return conn

@app.route('/api/bookings/<uuid:id>')
def get_flight(id) -> str:
    res = {
        'id' : 1,
        'company': '',
        'from' : '',
        'to' : '',
        'timefrom' : '',
        'timeto' : ''
    }
    return "Regex"

@app.route('/api/passengers/<uuid:id>')
def get_passenger(id) -> str:
    # res = {
    #     'firstname' : 1,
    #     'lastname': '',
    #     'patronymic' : '',
    #     'birthdate' : '',
    #     'series' : '',
    #     'number' : ''
    # }
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(f"select * from passengers where id = '{id}'")
    res = cursor.fetchone()
    return res

@app.route('/api/bookings/<uuid:id>')
def choose_seat(id):
    pass

@app.route('/api/bookings/<uuid:id>')
def register(id):
    pass

if __name__ == '__main__':
    app.run(debug=False, port=3400)