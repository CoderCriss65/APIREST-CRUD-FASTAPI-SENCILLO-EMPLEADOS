from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import mysql.connector
from database import get_db_connection, create_table

app = FastAPI()

# Configuración CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modelos Pydantic
class Empleado(BaseModel):
    nombre: str
    puesto: str
    salario: float

class EmpleadoResponse(BaseModel):
    id: int
    nombre: str
    puesto: str
    salario: float

# Crear tabla al iniciar (opcional, ya que dices que ya tienes la tabla)
@app.on_event("startup")
async def startup():
    create_table()

# 📌 1️⃣ Obtener todos los empleados
@app.get("/empleados")
async def get_empleados():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM empleados")
        empleados = cursor.fetchall()
        return empleados
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 📌 2️⃣ Obtener un empleado por su ID
@app.get("/empleados/{id}")
async def get_empleado(id: int):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM empleados WHERE id = %s", (id,))
        empleado = cursor.fetchone()
        if not empleado:
            raise HTTPException(status_code=404, detail={"mensaje": "Empleado no encontrado"})
        return empleado
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 📌 3️⃣ Agregar un nuevo empleado
@app.post("/empleados", status_code=status.HTTP_201_CREATED)
async def create_empleado(empleado: Empleado):
    if not empleado.nombre or not empleado.puesto or not empleado.salario:
        raise HTTPException(status_code=400, detail={"mensaje": "Todos los campos son obligatorios"})
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO empleados (nombre, puesto, salario) VALUES (%s, %s, %s)",
            (empleado.nombre, empleado.puesto, empleado.salario)
        )
        conn.commit()
        empleado_id = cursor.lastrowid
        return {"mensaje": "Empleado agregado", "id": empleado_id}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 📌 3.1️⃣ Inserción masiva de empleados
@app.post("/empleados/masivo", status_code=status.HTTP_201_CREATED)
async def create_empleados_masivo(empleados: List[Empleado]):
    # Validar que el array no esté vacío
    if not empleados or len(empleados) == 0:
        raise HTTPException(status_code=400, detail={"mensaje": "Debe enviar un array de empleados válido."})
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Construir los valores para la consulta SQL
        valores = [(e.nombre, e.puesto, e.salario) for e in empleados]
        
        cursor.executemany(
            "INSERT INTO empleados (nombre, puesto, salario) VALUES (%s, %s, %s)",
            valores
        )
        conn.commit()
        return {"mensaje": "Empleados agregados correctamente", "filasInsertadas": cursor.rowcount}
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 📌 4️⃣ Actualizar un empleado
@app.put("/empleados/{id}")
async def update_empleado(id: int, empleado: Empleado):
    if not empleado.nombre or not empleado.puesto or not empleado.salario:
        raise HTTPException(status_code=400, detail={"mensaje": "Todos los campos son obligatorios"})
    
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE empleados SET nombre = %s, puesto = %s, salario = %s WHERE id = %s",
            (empleado.nombre, empleado.puesto, empleado.salario, id)
        )
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail={"mensaje": "Empleado no encontrado"})
        
        conn.commit()
        return {"mensaje": "Empleado actualizado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 📌 5️⃣ Eliminar un empleado
@app.delete("/empleados/{id}")
async def delete_empleado(id: int):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM empleados WHERE id = %s", (id,))
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail={"mensaje": "Empleado no encontrado"})
        
        conn.commit()
        return {"mensaje": "Empleado eliminado correctamente"}
    except HTTPException:
        raise
    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail={"error": str(e)})
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Para ejecutar: uvicorn main:app --reload --host 0.0.0.0 --port 8000