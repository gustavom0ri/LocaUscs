import sqlite3

conn = sqlite3.connect('../locauscs.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM usuarios")
usuarios = cursor.fetchall()

for usuario in usuarios:
    print(usuario)

conn.close()
