import mysql.connector
from xmlrpc.server import SimpleXMLRPCServer
import logging
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
ip = "148.205.36.203"
server = SimpleXMLRPCServer(
    (ip, 9000),
    logRequests=True,
)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    database="ITAM"
)


def create_student(name, email):
    sql = "INSERT INTO ITAM.STUDENTS(name, email) values(%s, %s)"
    values = (name, email)
    cursor = mydb.cursor()
    cursor.execute(sql, values)
    mydb.commit()
    return {
        "status": "ok",
        "data": {
            "id": cursor.lastrowid
        }
    }

def get_student(id):
    sql = "SELECT * FROM ITAM.STUDENTS WHERE id = %s"
    values = (id,)
    cursor = mydb.cursor()
    cursor.execute(sql, values)
    student = cursor.fetchone()
    return {
        "status": "ok",
        "data": {
            "id": student[0], 
            "name": student[1], 
            "email": student[2], 
            "created_date": student[3], 
            "updated_date": student[4], 
            "is_active": student[5]
        }
    }

def delete_student(id):
    sql = "DELETE FROM ITAM.STUDENTS WHERE id = %s"
    values = (id,)
    cursor = mydb.cursor()
    cursor.execute(sql, values)
    mydb.commit()

    return {
        "status": "OK",
        "data": {
            "rowsAffected": cursor.rowcount
        }
    }

def update_student(id, name, email):
    sql = "UPDATE ITAM.STUDENTS SET name = %s, email = %s, updated_date = NOW() WHERE id = %s"
    values = (name, email, id)
    cursor = mydb.cursor()
    cursor.execute(sql, values)
    mydb.commit()

    return {
        "status": "OK",
        "data": {
            "rowsAffected": cursor.rowcount
        }
    }




server.register_function(create_student)
server.register_function(get_student)
server.register_function(update_student)
server.register_function(delete_student)

# Start the server
try:
    print('Use Control-C to exit')
    server.serve_forever()
except KeyboardInterrupt:
    print('Exiting')