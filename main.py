from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field
from typing import Optional, List
from config.base_de_datos import sesion, motor, base
from modelos.ventas import Ventas as VentasModelo
from jwt_config import dame_token, valida_token


app = FastAPI()
app.title = 'Aplicacion de ventas'
app.version = '1.0.1'
base.metadata.create_all(bind=motor)

class Usuario(BaseModel):
    email:str
    clave:str
    
#class
class Ventas(BaseModel):
    #id: int = Field(ge=0, le=20)
    id: Optional[int] =None
    fecha: str
    tienda: str = Field(min_length=4, max_length=10)
    importe: str

    class Config:
        schema_extra = {
            "example": {
                "id": 5,
                "fecha": "18/02/2023",
                "tienda": "Tienda02",
                "importe": 45040
            }
        }
        
class Portador(HTTPBearer):
    async def __call__ (self, request:Request):
        autorizacion = await super().__call__(request)
        dato = valida_token(autorizacion.credentials)
        if dato['email'] != 'daniela@gmail.com':
            raise HTTPException(status_code=403, detail='No autorizado')
            
        

@app.get('/', tags=['Inicio'])
def mensaje():
    return HTMLResponse('<h2>Titulo</h2>')


@app.get('/ventas', tags=['Ventas'], response_model=list[Ventas], status_code=200, dependencies=[Depends(Portador())])
def dame_ventas() -> list[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).all()
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))


@app.get('/ventas/{id}', tags=['Ventas'], response_model=Ventas, status_code=200)
def dame_venta_por_id(id: int = Path(ge=1, le=1000)) -> Ventas:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={'mensaje':'No se encontro id'})
    
    return JSONResponse(status_code=200, content=jsonable_encoder(resultado))
 
@app.get('/ventas/', tags=['Ventas'], response_model=list[Ventas], status_code=200)
def dame_ventas_por_tienda(tienda: str = Query(min_length=4, max_length=20)) -> list[Ventas]:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.tienda == tienda).all()
    if not resultado:
        return JSONResponse(status_code=404, content={'mensaje':'No se encontro tienda'})
    
    return JSONResponse(content= jsonable_encoder(resultado))    


@app.post('/ventas', tags=['Ventas'], response_model=dict, status_code=201)
def crea_venta(venta: Ventas) -> dict:
    db = sesion()
    nueva_venta = VentasModelo(**venta.dict())
    db.add(nueva_venta)
    db.commit()
    return JSONResponse(content={'mensaje': 'venta registrada'}, status_code=201)


@app.put('/ventas/{id}', tags=['Ventas'], response_model=dict, status_code=200)
def actualiza_ventas(id: int, venta: Ventas) -> dict:
    db =sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id==id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={'mensaje':'No se ha podido actualizar'})
    
    resultado.fecha = venta.fecha
    resultado.tienda = venta.tienda
    resultado.importe = venta.importe
    db.commit()
    return JSONResponse(status_code=201,content={'mensaje':'Venta Actualizada'})    

@app.delete('/ventas/delet/{id}', tags=['Ventas'], response_model=dict, status_code=200)
def eliminar_ventas(id: int) -> dict:
    db = sesion()
    resultado = db.query(VentasModelo).filter(VentasModelo.id == id).first()
    if not resultado:
        return JSONResponse(status_code=404, content={'mensaje':'No se ha podido borrar'})
    db.delete(resultado)
    db.commit()
    return JSONResponse(content={'mensaje':'Venta eliminado'}, status_code=200)        
    
#Ruta de login 
@app.post('/login', tags=['Autenticaciom'])
def login(usuario:Usuario):
    if usuario.email == 'daniela@gmail.com' and usuario.clave == '1234':
        token:str=dame_token(usuario.dict())
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(content={'mensaje':'Aceso denegado'}, status_code=404)