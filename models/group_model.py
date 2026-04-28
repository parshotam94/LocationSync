from app.extensions import mysql

def create_group(name, code):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO groups (name, invite_code) VALUES (%s,%s)", (name, code))
    mysql.connection.commit()
    cur.close()