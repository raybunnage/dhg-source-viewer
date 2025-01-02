# Base Exception for your entire application
class ApplicationError(Exception):
    """Base exception class for all application errors"""

    def __init__(self, message: str, original_error: Exception = None):
        self.message = message
        self.original_error = original_error
        super().__init__(self.message)


# Service-level base exceptions
class ServiceError(ApplicationError):
    """Base exception for all service-related errors"""

    pass


# Database specific exceptions
class DatabaseError(ServiceError):
    """Base exception for all database-related errors"""

    pass


class SupabaseError(DatabaseError):
    """Specific Supabase-related errors"""

    pass


# Specific Supabase error types
class SupabaseConnectionError(SupabaseError):
    """Raised when unable to connect to Supabase"""

    pass


class SupabaseQueryError(SupabaseError):
    """Raised when a query fails"""

    pass


# AI Service exceptions
class AIServiceError(ServiceError):
    """Base exception for AI-related services"""

    pass


class AnthropicError(AIServiceError):
    """Specific Anthropic-related errors"""

    pass


# Storage service exceptions
class StorageError(ServiceError):
    """Base exception for storage-related services"""

    pass


class GoogleDriveError(StorageError):
    """Specific Google Drive-related errors"""

    pass


# Auth related exceptions
class AuthError(ServiceError):
    """Base exception for authentication/authorization related errors"""

    pass


class SupabaseAuthenticationError(AuthError):
    """Raised when Supabase authentication fails (login, signup, etc.)"""

    pass


class SupabaseAuthorizationError(AuthError):
    """Raised when Supabase authorization/permissions fail (RLS, policies)"""

    pass
