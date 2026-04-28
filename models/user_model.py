from app.extensions import mysql

def create_user(name, email, password):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                (name, email, password))
    mysql.connection.commit()
    cur.close()