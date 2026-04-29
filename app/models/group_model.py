from app.extensions import mysql
import MySQLdb.cursors

def create_group(name, code, owner_id):
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO `groups` (name, invite_code, owner_id) VALUES (%s,%s,%s)", (name, code, owner_id))
    group_id = cur.lastrowid
    cur.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s,%s)", (group_id, owner_id))
    mysql.connection.commit()
    cur.close()
    return group_id

def get_groups_for_user(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT g.* FROM `groups` g
        JOIN group_members gm ON g.id = gm.group_id
        WHERE gm.user_id = %s
    """, (user_id,))
    groups = cur.fetchall()
    cur.close()
    return groups

def get_group_by_code(code):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("SELECT * FROM `groups` WHERE invite_code = %s", (code,))
    group = cur.fetchone()
    cur.close()
    return group

def add_member(group_id, user_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("INSERT INTO group_members (group_id, user_id) VALUES (%s,%s)", (group_id, user_id))
        mysql.connection.commit()
    except Exception:
        pass # ignore if already member
    finally:
        cur.close()