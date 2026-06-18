from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

def handle_integrity_error(e: IntegrityError) -> HTTPException:
    if e.orig.pgcode == "23505":
        return HTTPException(status_code=409, detail="Ya existe un registro con estos valores y deben ser únicos")
    if e.orig.pgcode == "23503":
        return HTTPException(status_code=409, detail="No se puede eliminar, tiene registros asociados")
    return HTTPException(status_code=500, detail="Error de base de datos")