#!/usr/bin/env python
import serial, time
import sys
import sqlite3
import signal

# connect to database and create cursor
db_connection = sqlite3.connect('test.db')
cursor = db_connection.cursor()

# create a table named sensor_data if it does not already exist
def create_table():
    cursor.execute('CREATE TABLE IF NOT EXISTS sensor_data(id INTEGER PRIMARY KEY AUTOINCREMENT, date_time TEXT, soil_moisture INTEGER, water_level TEXT)')

def dynamic_data_entry(serial_value):
    # create timestamp from localtime
    date_time = str(time.strftime("%m.%d.%y %H:%M:%S", time.localtime()))
    # strip the last 3 characters of the string to get the soil moisture value
    soil_moisture = serial_value[:-3]
    try:
        # fault tolerance: try to cast it to an int
        # if it is not able to cast to an int then it is garbled data because soil moisture should be an int
        # if it is less than 0 or greater than 1023 then it is garbled data because that would be outside of the range of possible values
        x = int(soil_moisture)
        if (x < 0 or x > 1023):
            cursor.execute('INSERT INTO  sensor_data(date_time, soil_moisture, water_level) VALUES (?, ?, ?)', ('Error: Soil moisture value out of range', 0, 'Error: Soil moisture value'))
            db_connection.commit()
            return 
    except ValueError:
        cursor.execute('INSERT INTO  sensor_data(date_time, soil_moisture, water_level) VALUES (?, ?, ?)', ('Error: Non-integer soil moisture value', 0, 'Error: Non-integer soil moisture value'))
        db_connection.commit()
        return
    # grab the character at the 3rd index from the end
    water_level = serial_value[-3]
    # if it is an 'e' then set water level to 'empty'
    if (water_level == 'e'):
        water_level = 'empty'
    # if it is a 'f' then set water level to 'full'
    elif (water_level == 'f'):
        water_level = 'full'
    # fault tolerance: if it is neither e or f then flag it as garbled data
    else:
        cursor.execute('INSERT INTO  sensor_data(date_time, soil_moisture, water_level) VALUES (?, ?, ?)', ('Error: Unknown water level value', 0, 'Error: Unknown water level value'))
        db_connection.commit()
        return
    # insert data into the table
    cursor.execute('INSERT INTO  sensor_data(date_time, soil_moisture, water_level) VALUES (?, ?, ?)', (date_time, soil_moisture, water_level))
    db_connection.commit()

# define signal handler that closes connections and does a clean exit
def signal_handler(signal, frame):
    serial_connection.close()
    db_connection.close()
    sys.exit(0)

# fault tolerance: try to connect to the serial port but catch a serial exception close connections and do a clean exit
try:
    # fault tolerance: set timeout to 10 so that if it is not receiving data it will not block forever
    serial_connection = serial.Serial('/dev/cu.usbserial-DN01J60W', 57600, timeout = 10)
except serial.serialutil.SerialException:
    print "Error opening port. Try again"
    db_connection.close()
    sys.exit(0)

# set signal handler for SIGINT
signal.signal(signal.SIGINT, signal_handler)

# create table if it does not already exist
create_table()

# allow for time to make connection
time.sleep(2)

# flush serial connection buffer
serial_connection.flush()

# continuously try to readlines from the serial connection and store in database
while 1:
    try:
        serial_data = serial_connection.readline()
        print serial_data
        # fault tolerance: exit gracefully when Arduino is no longer receiving data
        # after the timeout occurs it will return whatever data it has recevied thus far
        # in this case it will be nothing which will indicate the Arduino has not received data for the full timeout time
        # it should receive data every 5 seconds
        if (serial_data == ''):
            print "No longer receiving data. Exiting."
            serial_connection.close()
            db_connection.close()
            sys.exit(0)
        else:
            dynamic_data_entry(serial_data)
    except:
        print "Done"
        serial_connection.close()
        db_connection.close()
        sys.exit(0)