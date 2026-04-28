from app.extensions import mysql

def upsert_location(data):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO locations (user_id, group_id, latitude, longitude)
        VALUES (%s,%s,%s,%s)
        ON DUPLICATE KEY UPDATE latitude=%s, longitude=%s
    """, (
        data["user_id"], data["group_id"],
        data["lat"], data["lng"],
        data["lat"], data["lng"]
    ))
    mysql.connection.commit()
    cur.close()