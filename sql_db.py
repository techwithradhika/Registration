import mysql.connector
from mysql.connector import Error

try:
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = connection.cursor()
    database_name = "Registration"
    cursor.execute("CREATE DATABASE IF NOT EXISTS {}".format(database_name))
    print("Database '{}' created successfully!".format(database_name))
    cursor.execute("USE {}".format(database_name))
    create_table_query = """
    CREATE TABLE IF NOT EXISTS Register(
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Name VARCHAR(255) NOT NULL,
        Email VARCHAR(255) NOT NULL,
        DateOfBirth DATE
    )
    """
    cursor.execute(create_table_query)
    print("Table 'Register' created successfully")
except Error as e:
    print("Error while connecting to MySQL:", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection closed.")
