# * ---------- IMPORTS --------- *
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
import os
import psycopg2
import cv2
import numpy as np
import re
import awsiot.greengrasscoreipc
import awsiot.greengrasscoreipc.client as client
from awsiot.greengrasscoreipc.model import (
    IoTCoreMessage,
    SubscribeToIoTCoreRequest,
    PublishToIoTCoreRequest,
    QOS,
)
import json

# Get the relativ path to this file (we will use it later)
#FILE_PATH = "/home/pi/DOCKERS"
FILE_PATH = "/app"
# * ---------- Create App --------- *
app = Flask(__name__)
CORS(app, support_credentials=True)


# * ---------- DATABASE CONFIG --------- *
#DATABASE_USER = os.environ['DATABASE_USER']
#DATABASE_PASSWORD = os.environ['DATABASE_PASSWORD']
#DATABASE_HOST = os.environ['DATABASE_HOST']
#DATABASE_PORT = os.environ['DATABASE_PORT']
#DATABASE_NAME = os.environ['DATABASE_NAME']

def DATABASE_CONNECTION():
    return psycopg2.connect(user="pcieiqtj", password="PeF3NhDl4Y_yZScwgqizlkBl0rNNxP3g", host="kashin.db.elephantsql.com", port="5432", database="pcieiqtj")


def Publish_User(topic, message):
    TIMEOUT = 10

    ipc_client = awsiot.greengrasscoreipc.connect()

    qos = QOS.AT_LEAST_ONCE

    request = PublishToIoTCoreRequest()
    request.topic_name = topic
    request.payload = bytes(message, "utf-8")
    request.qos = qos
    operation = ipc_client.new_publish_to_iot_core()
    operation.activate(request)
    future = operation.get_response()
    future.result(TIMEOUT)


"""
def Subscribe_User(topic):
    TIMEOUT = 10

    ipc_client = awsiot.greengrasscoreipc.connect()

    class StreamHandler(client.SubscribeToIoTCoreStreamHandler):
        def __init__(self):
            super().__init__()

        def on_stream_event(self, event: IoTCoreMessage) -> None:
            try:
                message = str(event.message.payload, "utf-8")
                # Handle message.
            except:
                traceback.print_exc()

        def on_stream_error(self, error: Exception) -> bool:
            # Handle error.
            # Return True to close stream, False to keep stream open.
            return True

        def on_stream_closed(self) -> None:
            # Handle close.
            pass

    qos = QOS.AT_MOST_ONCE

    request = SubscribeToIoTCoreRequest()
    request.topic_name = topic
    request.qos = qos
    handler = StreamHandler()
    operation = ipc_client.new_subscribe_to_iot_core(handler)
    future = operation.activate(request)
    future.result(TIMEOUT)

    # Keep the main thread alive, or the process will exit.
    while True:
        time.sleep(10)

    # To stop subscribing, close the operation stream.
    operation.close()
"""

# * --------------------  ROUTES ------------------- *
# * ---------- Test server ---------- *


@app.route('/')
def index():
    return "<html>AWS server side is live</html>"

# * ---------- Get data from the face recognition ---------- *


@app.route('/receive_data', methods=['POST'])
def get_receive_data():
    if request.method == 'POST':
        json_data = request.get_json()

        # Check if the user is already in the DB
        try:
            # Connect to the DB
            connection = DATABASE_CONNECTION()
            cursor = connection.cursor()

            # Query to check if the user as been saw by the camera today
            user_saw_today_sql_query =\
                f"SELECT * FROM users WHERE date = '{json_data['date']}' AND name = '{json_data['name']}'"

            cursor.execute(user_saw_today_sql_query)
            result = cursor.fetchall()
            connection.commit()

            # If use is already in the DB for today:
            if result:
                print('user IN')
                image_path = f"{FILE_PATH}/assets/img/{json_data['date']}/{json_data['name']}/departure.jpg"

                # Save image
                os.makedirs(
                    f"{FILE_PATH}/assets/img/{json_data['date']}/{json_data['name']}", exist_ok=True)
                cv2.imwrite(image_path, np.array(json_data['picture_array']))
                json_data['picture_path'] = image_path

                # Update user in the DB
                update_user_querry = f"UPDATE users SET departure_time = '{json_data['hour']}', departure_picture = '{json_data['picture_path']}' WHERE name = '{json_data['name']}' AND date = '{json_data['date']}'"
                cursor.execute(update_user_querry)

                # Publish user leave
                user_data = {
                    "name": {json_data['name']},
                    "date": {json_data['date']},
                    "departure_time": {json_data['hour']}
                }
                user_data = json.dumps(user_data)
                Publish_User(topic="user/leave", message=user_data)

            else:
                print("user OUT")
                # Save image
                image_path = f"{FILE_PATH}/assets/img/history/{json_data['date']}/{json_data['name']}/arrival.jpg"
                os.makedirs(
                    f"{FILE_PATH}/assets/img/history/{json_data['date']}/{json_data['name']}", exist_ok=True)
                cv2.imwrite(image_path, np.array(json_data['picture_array']))
                json_data['picture_path'] = image_path

                # Create a new row for the user today:
                insert_user_querry = f"INSERT INTO users (name, date, arrival_time, arrival_picture) VALUES ('{json_data['name']}', '{json_data['date']}', '{json_data['hour']}', '{json_data['picture_path']}')"
                cursor.execute(insert_user_querry)

                # Publish user arrival
                user_data = {
                    "name": {json_data['name']},
                    "date": {json_data['date']},
                    "arrival_time": {json_data['hour']}
                }
                user_data = json.dumps(user_data)
                Publish_User(topic="user/arrival", message=user_data)

        except (Exception, psycopg2.DatabaseError) as error:
            print("ERROR DB: ", error)
        finally:
            connection.commit()

            # closing database connection.
            if connection:
                cursor.close()
                connection.close()
                print("PostgreSQL connection is closed")

        # Return user's data to the front
        return jsonify(json_data)


# * ---------- Get all the data of an employee ---------- *
@app.route('/get_employee/<string:name>', methods=['GET'])
def get_employee(name):
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = DATABASE_CONNECTION()
        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        user_information_sql_query = f"SELECT * FROM users WHERE name = '{name}'"

        cursor.execute(user_information_sql_query)
        result = cursor.fetchall()
        connection.commit()

        # if the user exist in the db:
        if result:
            print('RESULT: ', result)
            # Structure the data and put the dates in string for the front
            for k, v in enumerate(result):
                answer_to_send[k] = {}
                for ko, vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
            print('answer_to_send: ', answer_to_send)
        else:
            answer_to_send = {'error': 'User not found...'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if (connection):
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(answer_to_send)


# * --------- Get the 5 last users seen by the camera --------- *
@app.route('/get_5_last_entries', methods=['GET'])
def get_5_last_entries():
    answer_to_send = {}
    # Check if the user is already in the DB
    try:
        # Connect to DB
        connection = DATABASE_CONNECTION()

        cursor = connection.cursor()
        # Query the DB to get all the data of a user:
        lasts_entries_sql_query = f"SELECT * FROM users ORDER BY id DESC;"

        cursor.execute(lasts_entries_sql_query)
        result = cursor.fetchall()
        connection.commit()

        # if DB is not empty:
        if result:
            # Structure the data and put the dates in string for the front
            for k, v in enumerate(result):
                answer_to_send[k] = {}
                for ko, vo in enumerate(result[k]):
                    answer_to_send[k][ko] = str(vo)
        else:
            answer_to_send = {'error': 'error detect'}

    except (Exception, psycopg2.DatabaseError) as error:
        print("ERROR DB: ", error)
    finally:
        # closing database connection:
        if (connection):
            cursor.close()
            connection.close()

    # Return the user's data to the front
    return jsonify(answer_to_send)


# * ---------- Add new employee ---------- *
@app.route('/add_employee', methods=['POST'])
@cross_origin(supports_credentials=True)
def add_employee():
    try:
        # Get the picture from the request
        image_file = request.files['image']
        print(request.form['nameOfEmployee'])

        # Store it in the folder of the know faces:
        file_path = os.path.join(
            f"{FILE_PATH}/assets/img/users/{request.form['nameOfEmployee']}.jpg")
        image_file.save(file_path)
        answer = 'new employee succesfully added'
    except:
        answer = 'Error while adding new employee. Please try later...'
    return jsonify(answer)


# * ---------- Get employee list ---------- *
@app.route('/get_employee_list', methods=['GET'])
def get_employee_list():
    employee_list = {}

    # Walk in the user folder to get the user list
    walk_count = 0
    for file_name in os.listdir(f"{FILE_PATH}/assets/img/users/"):
        # Capture the employee's name with the file's name
        name = re.findall("(.*)\.jpg", file_name)
        if name:
            employee_list[walk_count] = name[0]
        walk_count += 1

    return jsonify(employee_list)


# * ---------- Delete employee ---------- *
@app.route('/delete_employee/<string:name>', methods=['GET'])
def delete_employee(name):
    try:
        # Remove the picture of the employee from the user's folder:
        print('name: ', name)
        file_path = os.path.join(f'{FILE_PATH}/assets/img/users/{name}.jpg')
        os.remove(file_path)
        answer = 'Employee succesfully removed'
    except:
        answer = 'Error while deleting new employee. Please try later'

    return jsonify(answer)


# * -------------------- RUN SERVER -------------------- *
if __name__ == '__main__':
    # * --- DEBUG MODE: --- *
    # app.run(host='localhost', port=5000, debug=True)
    #  * --- DOCKER PRODUCTION MODE: --- *
    app.run(debug=True, host='0.0.0.0', port=5001)
