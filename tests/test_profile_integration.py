import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, User, MedicalProfile, PersonalProfile, UserSettings

# Use in-memory SQLite for speed and isolation
@pytest.fixture
def db_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_profile_relationships(db_session):
    # 1. Create User
    user = User(username="test_profile", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # 2. Add Profiles
    med_profile = MedicalProfile(user_id=user.id, blood_type="O+", allergies="None")
    pers_profile = PersonalProfile(user_id=user.id, occupation="Dev", hobbies="Coding")
    settings = UserSettings(user_id=user.id, theme="dark")
    
    db_session.add_all([med_profile, pers_profile, settings])
    db_session.commit()
    
    # 3. Verify Relationships
    reloaded_user = db_session.query(User).filter_by(username="test_profile").first()
    assert reloaded_user is not None
    assert reloaded_user.medical_profile.blood_type == "O+"
    assert reloaded_user.personal_profile.occupation == "Dev"
    assert reloaded_user.settings.theme == "dark"

def test_cascade_delete(db_session):
    # Create user with profile
    user = User(username="delete_me", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    med = MedicalProfile(user_id=user.id)
    db_session.add(med)
    db_session.commit()
    
    # Verify existence
    assert db_session.query(MedicalProfile).filter_by(user_id=user.id).count() == 1
    
    # Delete User
    db_session.delete(user)
    db_session.commit()
    
    # Verify Cascade
    assert db_session.query(MedicalProfile).filter_by(user_id=user.id).count() == 0

def test_invalid_profile_data(db_session):
    # Test handling of nullable fields
    user = User(username="null_test", password_hash="hash")
    db_session.add(user)
    db_session.commit()
    
    # Create empty profile
    med = MedicalProfile(user_id=user.id) # All fields nullable except ID/UserID
    db_session.add(med)
    db_session.commit()
    
    assert med.blood_type is None
    # Ensure it doesn't crash
