from pydantic import BaseModel
from datetime import date
from typing import Optional, List

# Modelo base para un usuario con los campos comunes
class UsuarioBase(BaseModel):
    cedula: str
    nombre: str
    apellido: str
    rol: str
    matricula: Optional[str] = None
    fecha_nacimiento: date
    sexo: str
    objetivo: Optional[str] = "No definido"

# Modelo para la creación de un usuario (lo que se envía a la API)
class UsuarioCreate(UsuarioBase):
    pass

# Modelo para representar un reporte de sección
class ReporteSeccion(BaseModel):
    Estudiante: str
    Asignatura: str
    Docente: str

# Modelo para el conteo de estudiantes por docente
class ReporteConteoDocente(BaseModel):
    Docente: str
    Cantidad_Estudiantes: int

# Modelo para los objetivos de los estudiantes
class ReporteObjetivo(BaseModel):
    Estudiante: str
    Objetivo: str