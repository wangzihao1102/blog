"""Flask application factory."""
import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, render_markdown
from app.models.user import User
from app.routes.public import pub_bp
from app.routes.admin import admin_bp


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance folder exists
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(pub_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Create tables and seed admin user
    with app.app_context():
        db.create_all()
        _seed_admin_user()

    # Register SQLAlchemy event for auto-rendering markdown on body change
    from sqlalchemy import event
    from app.models.post import Post

    @event.listens_for(Post.body, 'set')
    def receive_set(target, value, oldvalue, initiator):
        if value is not None:
            target.body_html = str(render_markdown(value))

    return app


def _seed_admin_user():
    """Create default admin user if none exists."""
    if not User.query.first():
        admin = User(username=Config.ADMIN_USERNAME)
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
