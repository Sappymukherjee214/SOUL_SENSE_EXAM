import pytest
import sys
from unittest.mock import MagicMock, patch, call

# --- PRE-MOCK CRITICAL DEPENDENCIES ---
# We MUST mock these before 'app.cli' is imported because app.cli imports them at module level.
# If we don't, they try to load DB/Files and fail.
sys.modules['app.db'] = MagicMock()
sys.modules['app.questions'] = MagicMock()
sys.modules['app.services.exam_service'] = MagicMock() # This is the Mock Class source
sys.modules['app.utils'] = MagicMock()
# --------------------------------------

# Now safe to import
from app.cli import SoulSenseCLI

# Mocks for dependencies
@pytest.fixture
def mock_deps():
    return {
        'auth_manager': MagicMock(),
        'session_manager': MagicMock(),
        # Mock settings loaded inside CLI init
        'settings': {'question_count': 5, 'theme': 'dark'} 
    }

@pytest.fixture
def cli_instance(mock_deps):
    # Need to patch where it's used IN app.cli (or the mocks we injected)
    # Since we mocked app.utils in sys.modules, app.utils.load_settings is a Mock.
    
    app_utils_mock = sys.modules['app.utils']
    app_utils_mock.load_settings.return_value = mock_deps['settings']
    
    with patch('app.cli.SENTIMENT_AVAILABLE', False):
        cli = SoulSenseCLI(
            auth_manager=mock_deps['auth_manager'],
            session_manager=mock_deps['session_manager']
        )
        return cli

def test_cli_initialization(cli_instance):
    """Verify CLI initializes with injected dependencies and settings"""
    assert cli_instance.num_questions == 5
    assert cli_instance._auth_manager is not None
    assert cli_instance._session_manager is not None

def test_cli_setup_nltk_called():
    """Verify NLTK setup is attempted"""
    with patch('app.cli.SENTIMENT_AVAILABLE', True), \
         patch('app.cli.nltk') as mock_nltk, \
         patch('app.utils.load_settings'):
        
        # Simulate lookup error triggering download
        mock_nltk.data.find.side_effect = LookupError
        
        SoulSenseCLI()
        
        mock_nltk.download.assert_called_with('vader_lexicon', quiet=True)

def test_happy_path_flow(cli_instance):
    """Simulate a standard flow: Login -> Exam -> Result"""
    # Inputs: 
    # 1. Login choice "1" (Mocked via run logic, but CLI logic is separate)
    # Actually SoulSenseCLI.authenticate handling...
    
    # We need to mock the inputs sequence
    # Flow:
    # prompt name -> "user"
    # prompt age -> "25"
    inputs = ["user", "25"] 
    
    with patch.object(cli_instance, 'get_input', side_effect=inputs), \
         patch.object(cli_instance, 'print_header'), \
         patch.object(cli_instance, 'clear_screen'):
        
        # Mock DB context used in authenticate
        with patch('app.db.safe_db_context') as mock_ctx:
            mock_session = MagicMock()
            mock_ctx.return_value.__enter__.return_value = mock_session
            # Mock query finding no user -> create new
            mock_session.query.return_value.filter_by.return_value.first.return_value = None
            
            cli_instance.authenticate()
            
            assert cli_instance.username == "user"
            assert cli_instance.age == 25
            # Verify user creation
            assert mock_session.add.called

@patch('app.services.exam_service.ExamSession')
def test_initialize_session(MockSession, cli_instance):
    cli_instance.username = "test"
    cli_instance.age = 20
    
    with patch('app.cli.load_questions', return_value=[(1,"Q","T",10,30)]), \
         patch('app.cli.get_random_questions_by_age', return_value=[(1,"Q","T",10,30)]):
        
        cli_instance.initialize_session()
        
        assert cli_instance.session is not None
        assert cli_instance.session.start_exam.called

