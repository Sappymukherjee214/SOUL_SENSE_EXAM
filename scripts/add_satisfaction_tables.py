# scripts/add_satisfaction_tables.py
from app.db import get_engine
from app.models import Base, SatisfactionRecord, SatisfactionHistory

def create_satisfaction_tables():
    """Create satisfaction tables in database"""
    engine = get_engine()
    Base.metadata.create_all(engine, tables=[
        SatisfactionRecord.__table__,
        SatisfactionHistory.__table__
    ])
    print("✅ Created satisfaction tables")

if __name__ == "__main__":
    create_satisfaction_tables()