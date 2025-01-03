from typing import Optional
from storage3.types import StorageError, StorageApiError


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


# Storage specific exceptions
class SupabaseStorageError(SupabaseError):
    """Base exception for Supabase storage-related errors"""

    pass


class SupabaseStorageAuthError(SupabaseStorageError):
    """Raised when storage operation fails due to authentication"""

    pass


class SupabaseStoragePermissionError(SupabaseStorageError):
    """Raised when storage operation fails due to insufficient permissions"""

    pass


class SupabaseStorageQuotaError(SupabaseStorageError):
    """Raised when storage operation fails due to quota limits"""

    pass


class SupabaseStorageNotFoundError(SupabaseStorageError):
    """Raised when requested storage resource is not found"""

    pass


class SupabaseStorageValidationError(SupabaseStorageError):
    """Raised when storage operation fails due to validation"""

    pass


def map_storage_error(error: StorageError | StorageApiError) -> SupabaseStorageError:
    """Maps storage3 errors to our custom exceptions.

    Args:
        error: Original storage error from storage3

    Returns:
        Appropriate SupabaseStorageError subclass
    """
    error_message = str(error)

    if "authentication" in error_message.lower():
        return SupabaseStorageAuthError(
            "Storage authentication failed", original_error=error
        )
    elif "permission" in error_message.lower():
        return SupabaseStoragePermissionError(
            "Insufficient storage permissions", original_error=error
        )
    elif "quota" in error_message.lower():
        return SupabaseStorageQuotaError("Storage quota exceeded", original_error=error)
    elif "not found" in error_message.lower():
        return SupabaseStorageNotFoundError(
            "Storage resource not found", original_error=error
        )
    elif "validation" in error_message.lower():
        return SupabaseStorageValidationError(
            "Storage validation failed", original_error=error
        )
    else:
        return SupabaseStorageError("Storage operation failed", original_error=error)
