"""Middleware for LogTide SDK."""

# Each middleware is guarded by a try/except so that importing this package
# does not fail when only a subset of framework dependencies are installed.
# __all__ is built dynamically so that `from logtide_sdk.middleware import *`
# never raises AttributeError for frameworks that are not installed.

__all__ = []

try:
    from logtide_sdk.middleware.flask import LogTideFlaskMiddleware

    __all__.append("LogTideFlaskMiddleware")
except ImportError:
    pass

try:
    from logtide_sdk.middleware.django import LogTideDjangoMiddleware

    __all__.append("LogTideDjangoMiddleware")
except ImportError:
    pass

try:
    from logtide_sdk.middleware.fastapi import LogTideFastAPIMiddleware

    __all__.append("LogTideFastAPIMiddleware")
except ImportError:
    pass

try:
    from logtide_sdk.middleware.starlette import LogTideStarletteMiddleware

    __all__.append("LogTideStarletteMiddleware")
except ImportError:
    pass
