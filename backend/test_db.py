from app.db import get_connection


connection = get_connection()

cursor = connection.cursor()

cursor.execute("SELECT * FROM users;")

result = cursor.fetchone()

print(result)

cursor.close()
connection.close()