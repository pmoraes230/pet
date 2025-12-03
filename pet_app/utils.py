from django.db import connection

def call_procedure(proc_name, params):
    with connection.cursor() as cursos:
        cursos.callproc(proc_name, params)
        result = cursos.fetchall()
    return result