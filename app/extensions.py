"""Shared extensions and utilities."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from markupsafe import Markup

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message_category = 'info'
login_manager.session_protection = 'strong'

# --- Markdown renderer ---
import markdown as md_module

_md_instance = None


def get_markdown_renderer():
    """Return a cached Markdown renderer instance with extensions."""
    global _md_instance
    if _md_instance is None:
        _md_instance = md_module.Markdown(
            extensions=['extra', 'codehilite', 'toc', 'attr_list', 'def_list'],
        )
    return _md_instance


def render_markdown(text):
    """Render markdown text to safe HTML markup."""
    if not text:
        return Markup('')
    md = get_markdown_renderer()
    md.reset()
    return Markup(md.convert(text))
