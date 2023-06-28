import os # Manipular rutas de archivos
from sqlalchemy import create_engine # Crear un motor de base de datos
from sqlalchemy.orm.session import sessionmaker # Crear nuevas sesiones para interactuar con la base de datos
from sqlalchemy.ext.declarative import declarative_base

fichero = "../datos.sqlite"
# leemos el fichero
directorio = os.path.dirname(os.path.realpath(__file__))
# direccion de bd, uniendo las 2 variables 
ruta = f"sqlite:///{os.path.join(directorio, fichero)}"
#creamos el motor
motor = create_engine(ruta, echo=True)
# creamos la sesion pasadole el motor
sesion  = sessionmaker(bind=motor)
# crear base para manejar las tablas de la bd 
base = declarative_base()

