import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "123"),
            database=os.getenv("DB_NAME", "empresa"),
            autocommit=False
        )
    except mysql.connector.Error as err:
        print(f"Error de conexión a la base de datos: {err}")
        raise

def create_table():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS empleados (
            id INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            puesto VARCHAR(100) NOT NULL,
            salario DECIMAL(10, 2) NOT NULL
        )
        """)
        conn.commit()
        print("Tabla 'empleados' verificada/creada correctamente")
    except Exception as e:
        print(f"Error al crear/verificar tabla: {e}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()