from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# Configuración de MySQL
MYSQL_USER = "alex"
MYSQL_PASSWORD = "Acoaco.123"
MYSQL_HOST = "localhost"
MYSQL_PORT = "3306"
MYSQL_DATABASE = "test"

# URL de conexión a MySQL
SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

# Crear engine con configuración para MySQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_pre_ping=True,  # Verifica conexiones antes de usarlas
    pool_recycle=300,    # Recicla conexiones cada 5 minutos
    echo=False           # Cambia a True para ver las queries SQL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo para guardar JSON
class JsonData(Base):
    __tablename__ = "json_data"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True)  # Especificar longitud para MySQL
    content = Column(Text)  # Aquí guardamos el JSON como string
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# Función para obtener la sesión
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para testear la conexión
def test_connection():
    """Prueba la conexión a la base de datos"""
    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("✅ Conexión a MySQL exitosa")
            return True
    except Exception as e:
        print(f"❌ Error conectando a MySQL: {e}")
        return False

# Verificar conexión al importar el módulo
try:
    # Probar conexión al importar
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    print("✅ Conexión a MySQL establecida")
except Exception as e:
    print(f"⚠️  Advertencia: No se pudo conectar a MySQL: {e}")
    print("💡 Verifica que:")
    print("   - MySQL esté ejecutándose")
    print("   - Los datos de conexión sean correctos")
    print("   - El usuario 'alex' tenga permisos en la base de datos 'test'")
    print("   - pymysql esté instalado: pip install pymysql")

# Script de prueba cuando se ejecuta directamente
if __name__ == "__main__":
    print("🔍 Probando conexión a MySQL...")
    if test_connection():
        print("✅ Conexión exitosa")
        print("💡 Las tablas deben crearse usando app.sql")
    else:
        print("❌ Error de conexión - revisar configuración")