import sqlite3
from typing import Tuple
from .modelos import UsuarioCreate # Importamos el modelo Pydantic

# La ruta apunta a la carpeta del volumen de Docker
# Se cambia la ruta para que apunte a /workspace/data/ que es donde está el volumen
DB_PATH = r'/workspace/data/GestionAcademica.db'

def create_connection():
    """Crea y devuelve una conexión a la base de datos."""
    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        # Habilitar claves foráneas
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar con la base de datos: {e}")
    return conn

def init_db():
    """
    Inicializa la base de datos: crea las tablas si no existen
    e inserta los datos estáticos iniciales.
    """
    conn = create_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    # --- Creación de Tablas ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Usuarios (
        Cedula TEXT PRIMARY KEY, Nombre TEXT NOT NULL, Apellido TEXT NOT NULL,
        Rol TEXT NOT NULL, Matricula TEXT UNIQUE, FechaNacimiento TEXT, Sexo TEXT,
        Objetivo TEXT
    );""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Asignaturas (
        Clave TEXT PRIMARY KEY,
        Nombre TEXT NOT NULL UNIQUE
    );""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Seccion (
        ID INTEGER PRIMARY KEY AUTOINCREMENT,
        CedulaEstudiante TEXT,
        ClaveAsignatura TEXT,
        CedulaDocente TEXT,
        FOREIGN KEY(CedulaEstudiante) REFERENCES Usuarios (Cedula),
        FOREIGN KEY(ClaveAsignatura) REFERENCES Asignaturas (Clave),
        FOREIGN KEY(CedulaDocente) REFERENCES Usuarios (Cedula),
        UNIQUE (CedulaEstudiante, ClaveAsignatura)
    );""")

    # --- Inserción de Datos Estáticos ---
    try:
        usuarios_reg_static = [
            ('444-4444444-4', 'Juan', 'Reyes', 'E', '2023-003', '2006-01-15', 'M', 'Pasar el semestre'),
            ('555-5555555-5', 'Maria', 'Sosa', 'D', 'PROF-002', '1980-03-25', 'F', 'Enseñar POO')
        ]
        cursor.executemany("INSERT OR IGNORE INTO Usuarios VALUES (?,?,?,?,?,?,?,?)", usuarios_reg_static)

        asignaturas_reg = [
            ('MAT-101', 'Matemática Básica'),
            ('PRO-101', 'Introducción a la Programación')
        ]
        cursor.executemany("INSERT OR IGNORE INTO Asignaturas VALUES (?,?)", asignaturas_reg)
        
        secciones_reg = [
            ('444-4444444-4', 'PRO-101', '555-5555555-5')
        ]
        cursor.executemany("INSERT OR IGNORE INTO Seccion (CedulaEstudiante, ClaveAsignatura, CedulaDocente) VALUES (?,?,?)", secciones_reg)

        conn.commit()
        print("Base de datos inicializada y datos estáticos insertados.")
    except sqlite3.Error as e:
        print(f"Error durante la inserción de datos estáticos: {e}")
    finally:
        conn.close()

def a_tupla(usuario: UsuarioCreate) -> Tuple:
    """Convierte un objeto Pydantic Usuario a una tupla para la BD."""
    return (
        usuario.cedula,
        usuario.nombre,
        usuario.apellido,
        usuario.rol.upper(),
        usuario.matricula,
        usuario.fecha_nacimiento.isoformat(),
        usuario.sexo.upper(),
        usuario.objetivo
    )