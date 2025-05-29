from datetime import date, datetime
from sqlmodel import Session
from app.auth.hashing import hash_password
from app.models.order import Order
from app.models.user import User
from app.db.database import create_db_and_tables, drop_db_and_tables, engine

def seed_data():
    # Borrar la base de datos y las tablas existentes
    drop_db_and_tables() 
    # Crear la base de datos y las tablas
    create_db_and_tables()
    # Insertar los datos falsos
    insert_fake_data()

# Función para insertar datos falsos
def insert_fake_data():
    with Session(engine) as session:
        try:
            # Crear datos falsos para User
            users = [
                User(username="user_admin", email="user_admin@example.com", hashed_password=hash_password("user_admin"), role="admin", created_at=datetime.utcnow()),
                User(username="user_client", email="user_client@example.com", hashed_password=hash_password("user_client"), role="client", created_at=datetime.utcnow())
            ]
            session.add_all(users)
            session.commit()
        except Exception as e:
            print(f"Error creating Users: {e}")

        try:
            # Crear datos falsos para Order
            orders = [
                Order(user_id=1, product_id=1, quantity=2, created_at=datetime.utcnow()),
                Order(user_id=2, product_id=2, quantity=1, created_at=datetime.utcnow())
            ]
            session.add_all(orders)
            session.commit()
        except Exception as e:
            print(f"Error creating Orders: {e}")

if __name__ == "__main__":
    seed_data()
