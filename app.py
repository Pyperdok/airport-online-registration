from flask import Flask, send_file, send_from_directory
from flask import request
from flask import render_template
import psycopg2
from werkzeug.routing import BaseConverter
import random
import os
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

app = Flask(__name__)
class UUID(BaseConverter):
    regex = r'[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
app.url_map.converters['uuid'] = UUID
app.config['TEMPLATES_AUTO_RELOAD'] = True


#Создает соединение с БД
def get_db():
    conn = psycopg2.connect('postgresql://postgres:12345678@localhost:5432/airport')
    conn.set_client_encoding('UTF8')
    return conn

#Ищет по номеру бронирования рейс и пассажира
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

#Ищет пассажира по его ID
@app.route('/api/passengers/<uuid:id>')
def get_passenger(id) -> str:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(f"select * from passengers where id = '{id}'")
    res = cursor.fetchone()
    return res

#Проверяет паспортные данные введенные пассажиром
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

#Завершает регистрацию пассажира, изменяя его статус регистрации
@app.route('/api/bookings/<uuid:id>', methods=['POST'])
def finish_registration(id) -> str:
    if request.method == 'POST':
        data = request.get_json()
        conn = get_db()
        cursor = conn.cursor()
        sql = f"""UPDATE bookings SET ("isRegistered", "seat") = ('True', '{int(data['seat'])}') where id = '{id}'"""
        cursor.execute(sql)
        conn.commit()
        routeList = get_flight(id)
        with open(f'./{id}', 'w') as f:
            f.write(str(routeList))
        cursor.close()
    
    return 'True'
            
     
#Возвращает форму для ввода паспортных данных
@app.route('/passport')
def passport():
    context = {}
    context['id'] = request.args['flight']
    return render_template('passport.html', context=context)

#Возвращает интерфейс для начала регистрации
@app.route('/booking')
def booking():
    context = dict(get_flight(request.args['flight']))
    return render_template('booking.html', context=context)

#Возвращает форму для выбора места
@app.route('/seat')
def seat():
    context = {}
    conn = get_db()
    cursor = conn.cursor()
    context['id'] = request.args['flight']
    cursor.execute(f"""SELECT "flightId" from bookings where id = '{context['id']}'""")
    res = cursor.fetchone()
    flightId = res[0]
    cursor.execute(f"""select seat from bookings where "flightId" = '{flightId}'""")
    raw = cursor.fetchall()
    context['seats'] = [True]*256
    for s in raw:
        context['seats'][s[0]] = False
    print(context['seats'])
    return render_template('seat.html', context=context)

#Возвращает форму для ввода номера бронирования (Начальная страница)
@app.route('/')
def main():
    return render_template('main.html')

@app.route('/route')
def route():
    context = {}
    context['id'] = request.args['flight']
    return render_template('route.html', context=context)

@app.route('/download/<uuid:id>')
def download(id):
    return send_file(f'./{id}')

if __name__ == '__main__':
    app.run(debug=False, port=3400)