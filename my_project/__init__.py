from .services.auth import AuthService
from .services.database import DatabaseService

# Create package-level instances
default_auth = AuthService()
default_db = DatabaseService()

# Version info
__version__ = '1.0.0'