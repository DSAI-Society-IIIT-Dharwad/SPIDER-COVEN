from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./scout.db")

# connect_args only needed for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    from backend.models import PriceSnapshot, Alert, Product
    Base.metadata.create_all(bind=engine)
    
    from sqlalchemy import text
    with engine.connect() as conn:
        try:
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_pin ON price_snapshots(pin_code)"))
            conn.execute(text("CREATE INDEX IF NOT EXISTS idx_asin_pin ON price_snapshots(asin, pin_code)"))
            conn.commit()
        except Exception as e:
            print(f"Index already exists: {e}")
            
    print("Database initialized at scout.db")

if __name__ == "__main__":
    init_db()
