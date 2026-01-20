
import sys
import os
import logging

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db import check_db_state, engine
from sqlalchemy import inspect
from app.models import AssessmentResult # Import to ensure it's registered with Base

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_assessments():
    logger.info("Starting migration for Assessment Module...")
    
    # 1. Trigger table creation
    check_db_state()
    
    # 2. Verify
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if "assessment_results" in tables:
        logger.info("✅ 'assessment_results' table verified successfully.")
        
        # Check columns
        columns = [c['name'] for c in inspector.get_columns("assessment_results")]
        required = ['id', 'user_id', 'assessment_type', 'total_score', 'details']
        
        missing = [req for req in required if req not in columns]
        
        if not missing:
            logger.info("✅ All required columns present.")
        else:
            logger.error(f"❌ Missing columns: {missing}")
            
    else:
        logger.error("❌ 'assessment_results' table failed to create.")

if __name__ == "__main__":
    migrate_assessments()
