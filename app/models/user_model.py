from app.extensions import mysql
import MySQLdb.cursors
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(name, email, password):
    cur = mysql.connection.cursor()
    hashed_password = generate_password_hash(password)
    cur.execute("INSERT INTO users (name, email, password) VALUES (%s,%s,%s)",
                (name, email, hashed_password))
    mysql.connection.commit()
    cur.close()

def get_user_by_email(email):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()
    cur.close()
    return user

def get_user_by_id(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    return user