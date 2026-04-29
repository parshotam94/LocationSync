import mysql.connector

with open('app/static/database/schema.sql', 'r') as f:
    sql_script = f.read()

# Connect without DB first to ensure it creates tracker_db
cnx = mysql.connector.connect(user='root', password='267694', host='localhost')
cursor = cnx.cursor()

# Execute multi-statement SQL
for result in cursor.execute(sql_script, multi=True):
    pass

cnx.commit()
cursor.close()
cnx.close()
print("Database schema updated successfully!")
