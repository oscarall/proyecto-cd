import json
import xmlrpc.client
from faker import Faker
fake = Faker()

proxy = xmlrpc.client.ServerProxy('http://148.205.36.203:9000')
name = fake.name()
email = fake.email()
print(f"Creando estudiante {name} con correo {email}")
student_id = proxy.create_student(name, email)["data"]["id"]
print(f"Id del nuevo estudiante: {student_id}")
student = proxy.get_student(student_id)
new_name = fake.name()
print(f"Información del estudiante: {json.dumps(student)}\n\nActualizando el nombre a {new_name}...")
proxy.update_student(student_id, new_name, email)
student = proxy.get_student(student_id)
print(f"Información del estudiante actualizado: {json.dumps(student)}\n\nDeshabilitando estudiante...")
proxy.disable_student(student_id)
student = proxy.get_student(student_id)
print(f"Información del estudiante deshabilitado: {json.dumps(student)}")