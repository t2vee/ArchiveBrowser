from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Database setup: replace with your database URL
DATABASE_URL = "postgresql://postgres:linuxmoment@localhost:5432/postgres"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

def clear_database():
    db_session = SessionLocal()
    try:
        # Reflect the tables
        Base.metadata.reflect(bind=engine)

        # Clear all data from all tables
        for table in reversed(Base.metadata.sorted_tables):
            print(f"Clearing table {table}")
            db_session.execute(table.delete())

        db_session.commit()
        print("Database cleared successfully.")
    except Exception as e:
        db_session.rollback()
        print(f"An error occurred: {e}")
    finally:
        db_session.close()

if __name__ == "__main__":
    clear_database()
