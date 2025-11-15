import pytest
from unittest.mock import Mock
from src.daip_live.p7_gui_v1.viewmodel.command import SyncCommand, AsyncCommand


class TestCommand:
    """TDD for Command system functionality"""
    
    def test_command_initialization(self):
        """RED: Test that Command can be initialized"""
        def test_func():
            return "result"
        
        cmd = SyncCommand(test_func)
        assert cmd is not None
        assert cmd.execute_func == test_func
    
    def test_command_execution(self):
        """RED: Test basic command execution"""
        mock_func = Mock(return_value="success")
        
        cmd = SyncCommand(mock_func)
        result = cmd.execute()
        
        mock_func.assert_called_once()
        assert result == "success"
    
    def test_command_with_parameters(self):
        """RED: Test command execution with parameters"""
        mock_func = Mock(return_value="result")
        
        cmd = SyncCommand(mock_func)
        result = cmd.execute("arg1", "arg2", keyword="value")
        
        mock_func.assert_called_once_with("arg1", "arg2", keyword="value")
        assert result == "result"
    
    def test_command_validation(self):
        """RED: Test command validation functionality"""
        def test_func():
            return "result"
        
        def validation_func():
            return True
        
        cmd = SyncCommand(test_func, validation_func)
        
        assert cmd.can_execute() is True
    
    def test_command_validation_prevents_execution(self):
        """RED: Test that invalid command raises exception when executed"""
        def test_func():
            return "result"
        
        def validation_func():
            return False
        
        cmd = SyncCommand(test_func, validation_func)
        
        assert cmd.can_execute() is False
        
        with pytest.raises(RuntimeError, match="Command cannot execute"):
            cmd.execute()
    
    def test_command_with_parameters_validation(self):
        """RED: Test command with parameters and validation"""
        mock_func = Mock(return_value="result")
        mock_validation = Mock(return_value=True)
        
        cmd = SyncCommand(mock_func, mock_validation)
        result = cmd.execute("param1", "param2")
        
        mock_func.assert_called_once_with("param1", "param2")
        mock_validation.assert_called_once()
        assert result == "result"