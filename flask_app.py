from flask import Flask, render_template, g
from flask_bootstrap import Bootstrap
import sqlite3
import signal

# usage: python test.py

app = Flask(__name__)
Bootstrap(app)

@app.before_request
def before_request():
    # connect to the database
    g.db_connection = sqlite3.connect('test.db')

@app.route('/')
def display_data():
    # create a cursor
    cursor = g.db_connection.cursor()
    # execute a select all statement and order it in descending order so the most recent data is at the top of the table
    cursor.execute('SELECT * FROM sensor_data ORDER BY id DESC')
    # fetch all of the rows
    rows = cursor.fetchall()
    # set alert flag to false
    alert = False
    # if the most recent row's water level value is 'empty' then set the alert to refill
    if rows[0][3] == 'empty':
    	alert = 'REFILL YO WATER'
    # render the template to display the data
    return render_template('display_data.html', rows = rows, alert = alert)

if __name__ == "__main__": 
    app.run(debug=True)