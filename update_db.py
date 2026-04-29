import mysql.connector

with open('app/static/database/schema.sql', 'r') as f:
    sql_script = f.read()

cnx = mysql.connector.connect(user='root', password='267694', host='localhost')
cursor = cnx.cursor()

# Drop existing database to ensure clean schema recreation
cursor.execute("DROP DATABASE IF EXISTS tracker_db")
cnx.commit()

# Recreate database and tables
for result in cursor.execute(sql_script, multi=True):
    pass

cnx.commit()
cursor.close()
cnx.close()
print("Database dropped and recreated with new schema successfully!")
