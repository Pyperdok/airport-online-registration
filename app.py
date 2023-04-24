from flask import Flask
from flask import request
from flask import render_template
import psycopg2
from werkzeug.routing import BaseConverter
import random

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

app = Flask(__name__)
class UUID(BaseConverter):
    regex = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
app.url_map.converters['uuid'] = UUID
app.config['TEMPLATES_AUTO_RELOAD'] = True


def get_db():
    conn = psycopg2.connect('postgresql://postgres:12345678@localhost:5432/airport')
    conn.set_client_encoding('UTF8')
    return conn

@app.route('/api/bookings/<uuid:id>')
def get_flight(id) -> str:
    db = get_db()
    cursor = db.cursor()
    cursor.execute("""SELECT bookings.id, flights.company, flights.from, flights.to, flights.path, flights.timefrom, flights.timeto,
passengers.firstname, passengers.lastname, passengers.patronymic
FROM bookings LEFT JOIN passengers
ON "passengerId" = passengers.id
LEFT JOIN flights
ON "flightId" = flights.id""")
    raw = cursor.fetchone()
    result = {}
    for i,c in enumerate(cursor.description): 
        result[c.name] = str(raw[i])
    return result

@app.route('/api/passengers/<uuid:id>')
def get_passenger(id) -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"select * from passengers where id = '{id}'")
    res = cursor.fetchone()
    return res

@app.route('/api/passengers/validate', methods=['POST'])
def validate_passenger() -> str:
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"""SELECT *FROM public.passengers where 
firstname = '{data['firstname']}' and
lastname = '{data['lastname']}' and
patronymic = '{data['patronymic']}' and
birthdate = '{data['birthdate']}' and
series = '{data['series']}'""")
        if cursor.fetchone() is not None:
            return 'True'
    return 'False'

@app.route('/api/bookings/<uuid:id>', methods=['POST'])
def finish_registration(id) -> str:
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) from bookings where id = '{id}' and seat = {data['seat']}")
        res = cursor.fetchone()
        if res is None:
            cursor.execute(f"UPDATE bookings SET seat = '{data['seat']}' where id = '{id}'")
            
     

@app.route('/passport')
def passport():
    context = {}
    context['id'] = request.args['flight']
    return render_template('passport.html', context=context)

@app.route('/booking')
def booking():
    context = dict(get_flight(request.args['flight']))
    return render_template('booking.html', context=context)

@app.route('/seat')
def choose_seat():
    context = {}
    context['id'] = request.args['flight']
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"select seat from bookings where id = '{context['id']}'")
    raw = cursor.fetchone()
    for i,c in enumerate(cursor.description): 
        context[c.name] = str(raw[i])
    if context['seat'] == "None":
        context['seat'] = random.randint(1, 255)
    return render_template('seat.html', context=context)

@app.route('/')
def main():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(debug=False, port=3400)