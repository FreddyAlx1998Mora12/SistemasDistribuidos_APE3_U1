import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'clave-secreta-para-desarrollo-y-pruebas-no-es-IA'
    LOG_LEVEL = 'DEBUG'
    # Directorio base
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))