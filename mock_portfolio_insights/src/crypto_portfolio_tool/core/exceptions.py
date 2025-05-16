class APIRequestError(Exception):
    """Custom exception for API request failures."""
    
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.status_code = status_code

class DataValidationError(Exception):
    """Custom exception for data validation errors."""
    pass

class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass
class LogicError(Exception):
    """Custom exception for business logic errors."""
    pass

class DataError(Exception):
    """Base exception for data-related errors"""
    pass