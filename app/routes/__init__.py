"""Routes package."""
from app.routes.public import pub_bp
from app.routes.admin import admin_bp

__all__ = ['pub_bp', 'admin_bp']
