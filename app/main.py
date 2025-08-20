from fastapi import FastAPI, HTTPException
from typing import List
import sqlite3
from . import database, modelos
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Función que se ejecuta una sola vez al iniciar la aplicación.
    Ideal para inicializar la base de datos.
    """
    print("Iniciando aplicación y base de datos...")
    database.init_db()
    yield

app = FastAPI(title="API de Gestión Académica", lifespan=lifespan)

@app.get("/")
def read_root():
    return {"mensaje": "Bienvenido a la API de Gestión Académica"}

# Endpoint para crear un nuevo usuario
@app.post("/usuarios/", response_model=modelos.UsuarioBase, status_code=201)
def crear_usuario(usuario: modelos.UsuarioCreate):
    """
    Crea un nuevo usuario en la base de datos.
    """
    usuario_tupla = database.a_tupla(usuario)
    conn = database.create_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO Usuarios VALUES (?,?,?,?,?,?,?,?)", usuario_tupla)
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="La cédula o matrícula ya existe.")
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error en la base de datos: {e}")
    finally:
        if conn:
            conn.close()
    return usuario

# --- Endpoints de Reportes ---

@app.get("/reportes/secciones", response_model=List[modelos.ReporteSeccion])
def obtener_reporte_secciones():
    """
    Consulta 1: Ver la lista de clases con estudiante y docente.
    """
    query = """
        SELECT
            est.Nombre || ' ' || est.Apellido AS Estudiante,
            a.Nombre AS Asignatura,
            doc.Nombre || ' ' || doc.Apellido AS Docente
        FROM Seccion s
        JOIN Usuarios est ON s.CedulaEstudiante = est.Cedula
        JOIN Asignaturas a ON s.ClaveAsignatura = a.Clave
        JOIN Usuarios doc ON s.CedulaDocente = doc.Cedula;
    """
    conn = database.create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    resultados = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in resultados]


@app.get("/reportes/conteo-estudiantes-docente", response_model=List[modelos.ReporteConteoDocente])
def obtener_conteo_estudiantes_por_docente():
    """
    Consulta 2: Contar cuántos estudiantes tiene cada docente.
    """
    query = """
        SELECT
            doc.Nombre || ' ' || doc.Apellido AS Docente,
            COUNT(s.CedulaEstudiante) AS Cantidad_Estudiantes
        FROM Seccion s
        JOIN Usuarios doc ON s.CedulaDocente = doc.Cedula
        GROUP BY Docente;
    """
    conn = database.create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    resultados = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in resultados]


@app.get("/reportes/objetivos-estudiantes", response_model=List[modelos.ReporteObjetivo])
def obtener_objetivos_estudiantes():
    """
    Consulta 3: Ver los objetivos de todos los estudiantes.
    """
    query = "SELECT Nombre || ' ' || Apellido as Estudiante, Objetivo FROM Usuarios WHERE Rol = 'E';"
    conn = database.create_connection()
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    resultados = cursor.execute(query).fetchall()
    conn.close()
    return [dict(row) for row in resultados]