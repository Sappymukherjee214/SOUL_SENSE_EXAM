
import pytest
import tkinter as tk
from unittest.mock import MagicMock, patch, ANY
from app.ui.profile import UserProfileView
from app.ui.results import ResultsManager
from app.utils.file_validation import ValidationError

class TestUIExportSecurity:

    @pytest.fixture
    def mock_app(self):
        app = MagicMock()
        app.username = "test_user"
        app.settings = {}
        app.colors = {"bg": "white", "card_bg": "white", "text_primary": "black"}
        # Mock i18n
        app.i18n.get = MagicMock(return_value="Test Label")
        # Mock styles
        app.ui_styles.get_font = MagicMock(return_value=("Arial", 10))
        return app

    @pytest.fixture
    def profile_view(self, mock_app):
        root = MagicMock()
        view = UserProfileView(root, mock_app)
        # Mock view container
        view.view_container = MagicMock()
        # Mock styles and colors since they are accessed
        view.colors = mock_app.colors
        view.styles = mock_app.ui_styles
        return view

    @pytest.fixture
    def results_manager(self, mock_app):
        return ResultsManager(mock_app)

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("app.ui.profile.messagebox")
    @patch("builtins.open", new_callable=MagicMock)
    @patch("json.dump")
    @patch("app.utils.file_validation.validate_file_path")
    def test_profile_export_success(self, mock_validate, mock_json, mock_open, mock_msg, mock_dialog, profile_view):
        """Test successful export flow in Profile UI"""
        # Setup mocks
        mock_dialog.return_value = "C:/Users/test/Documents/export.json"
        mock_validate.return_value = "C:/Users/test/Documents/export.json"
        
        # Call the render method to create the button/closure
        profile_view._render_export_view()
        pass 

    @patch("tkinter.filedialog.asksaveasfilename")
    @patch("app.utils.file_validation.validate_file_path")
    @patch("app.ui.results.generate_pdf_report")
    @patch("app.ui.results.messagebox")
    def test_results_pdf_export_security(self, mock_msg, mock_gen, mock_validate, mock_dialog, results_manager):
        """Test validation is called during PDF export"""
        # Case 1: Success
        mock_dialog.return_value = "C:/safe/report.pdf"
        mock_validate.return_value = "C:/safe/report.pdf"
        
        results_manager.export_results_pdf()
        
        mock_validate.assert_called_with("C:/safe/report.pdf", allowed_extensions=[".pdf"])
        mock_gen.assert_called()

        # Case 2: Validation Failure
        mock_dialog.return_value = "C:/unsafe/report.exe"
        mock_validate.side_effect = ValidationError("Invalid extension")
        mock_gen.reset_mock()
        
        results_manager.export_results_pdf()
        
        # msg.showerror called with "Security Error" and something containing "Invalid extension"
        assert mock_msg.showerror.called
        args = mock_msg.showerror.call_args
        assert args[0][0] == "Security Error"
        assert "Invalid extension" in str(args[0][1])
        mock_gen.assert_not_called()

