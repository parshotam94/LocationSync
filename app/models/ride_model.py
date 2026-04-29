from app.extensions import mysql
import MySQLdb.cursors
from datetime import datetime

def start_ride(group_id, name):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO rides (group_id, name, start_time) 
        VALUES (%s, %s, %s)
    """, (group_id, name, datetime.now()))
    ride_id = cur.lastrowid
    mysql.connection.commit()
    cur.close()
    return ride_id

def end_ride(ride_id, total_distance, duration_minutes, avg_speed, participant_ids):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE rides 
        SET end_time = %s, total_distance = %s, duration_minutes = %s, avg_speed = %s
        WHERE id = %s
    """, (datetime.now(), total_distance, duration_minutes, avg_speed, ride_id))
    
    for uid in participant_ids:
        try:
            cur.execute("INSERT INTO ride_participants (ride_id, user_id) VALUES (%s, %s)", (ride_id, uid))
        except Exception:
            pass # ignore duplicates
            
    mysql.connection.commit()
    cur.close()

def get_rides_for_user(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT r.*, g.name as group_name 
        FROM rides r
        JOIN ride_participants rp ON r.id = rp.ride_id
        JOIN `groups` g ON r.group_id = g.id
        WHERE rp.user_id = %s
        ORDER BY r.end_time DESC
    """, (user_id,))
    rides = cur.fetchall()
    cur.close()
    return rides
