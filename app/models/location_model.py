from app.extensions import mysql
import MySQLdb.cursors

def insert_location(data):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO locations (user_id, group_id, latitude, longitude)
        VALUES (%s,%s,%s,%s)
    """, (
        data["user_id"], data["group_id"],
        data["lat"], data["lng"]
    ))
    mysql.connection.commit()
    cur.close()

def get_locations_for_group(group_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT l.user_id, l.latitude, l.longitude, l.timestamp, u.name as user_name
        FROM locations l
        JOIN users u ON l.user_id = u.id
        WHERE l.group_id = %s 
        ORDER BY l.timestamp ASC
    """, (group_id,))
    locations = cur.fetchall()
    cur.close()
    return locations