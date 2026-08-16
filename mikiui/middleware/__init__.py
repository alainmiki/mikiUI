"""MikiUI middleware package."""

from .error_handler import ErrorHandlerMiddleware, register_exception_handlers

__all__ = ["ErrorHandlerMiddleware", "register_exception_handlers"]
