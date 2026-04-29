from app.extensions import mysql
import MySQLdb.cursors

def create_invitation(group_id, sender_id, receiver_id):
    cur = mysql.connection.cursor()
    # Check if already invited or member
    cur.execute("SELECT id FROM invitations WHERE group_id=%s AND receiver_id=%s AND status='pending'", (group_id, receiver_id))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO invitations (group_id, sender_id, receiver_id)
            VALUES (%s,%s,%s)
        """, (group_id, sender_id, receiver_id))
        mysql.connection.commit()
    cur.close()

def get_pending_invitations(user_id):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("""
        SELECT i.id, g.name as group_name, u.name as sender_name
        FROM invitations i
        JOIN `groups` g ON i.group_id = g.id
        JOIN users u ON i.sender_id = u.id
        WHERE i.receiver_id = %s AND i.status = 'pending'
    """, (user_id,))
    invites = cur.fetchall()
    cur.close()
    return invites

def update_invitation_status(invite_id, status):
    cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cur.execute("UPDATE invitations SET status=%s WHERE id=%s", (status, invite_id))
    cur.execute("SELECT * FROM invitations WHERE id=%s", (invite_id,))
    invite = cur.fetchone()
    mysql.connection.commit()
    cur.close()
    return invite
